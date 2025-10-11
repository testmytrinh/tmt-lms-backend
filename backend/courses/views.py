from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    DjangoModelPermissions,
)

from enrollment.serializers import EnrollmentReadSerializer

from . import pagination, queries

from .permissions import UserCanModifyCourseClass
from .serializers import (
    CourseSerializer,
    CourseCategorySerializer,
    CourseClassReadSerializer,
    CourseClassWriteSerializer,
)
from django.contrib.auth import get_user_model
from user.serializers import UserReadSerializer
from services.openfga.relations import CourseClassRelation, UserRelation
from services.openfga.sync.utils import sync_single_type_subjects
from openfga_sdk import ReadRequestTupleKey
from services.openfga.sync import client as fga_client


class CourseViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [AllowAny]
    queryset = queries.get_all_courses()
    serializer_class = CourseSerializer
    pagination_class = pagination.LargeResultsSetPagination


class CourseCategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [AllowAny]
    queryset = queries.get_all_course_categories()
    serializer_class = CourseCategorySerializer
    pagination_class = pagination.LargeResultsSetPagination


class CourseClassViewSet(viewsets.ModelViewSet):
    pagination_class = pagination.StandardResultsSetPagination
    QUERYSET_MAP = {
        "list": lambda _: queries.get_active_open_classes(),
        "retrieve": lambda req: queries.get_visible_classes(req.user),
        "update": lambda _: queries.get_all_classes(),
        "partial_update": lambda _: queries.get_all_classes(),
        "destroy": lambda _: queries.get_all_classes(),
        "me": lambda req: queries.get_user_classes(req.user),
        "my_enrollment": lambda req: queries.get_visible_classes(req.user),
        "access": lambda _: queries.get_all_classes(),
        "role_access": lambda _: queries.get_all_classes(),
    }
    PERMISSION_MAP = {
        "list": [AllowAny],
        "retrieve": [AllowAny],
        "create": [DjangoModelPermissions],
        "update": [IsAuthenticated, DjangoModelPermissions | UserCanModifyCourseClass],
        "partial_update": [
            IsAuthenticated,
            DjangoModelPermissions | UserCanModifyCourseClass,
        ],
        "destroy": [IsAuthenticated, DjangoModelPermissions],
        "me": [IsAuthenticated],
        "my_enrollment": [IsAuthenticated],
        "access": [IsAuthenticated, UserCanModifyCourseClass],
        "role_access": [IsAuthenticated, UserCanModifyCourseClass],
    }
    SERIALIZER_MAP = {
        "list": CourseClassReadSerializer,
        "retrieve": CourseClassReadSerializer,
        "create": CourseClassWriteSerializer,
        "update": CourseClassWriteSerializer,
        "partial_update": CourseClassWriteSerializer,
        "destroy": CourseClassWriteSerializer,
        "me": CourseClassReadSerializer,
        "my_enrollment": EnrollmentReadSerializer,
        "access": None,
    }

    def get_queryset(self):
        fn = self.QUERYSET_MAP.get(self.action, lambda req: queries.get_no_classes())
        return fn(self.request)

    def get_permissions(self):
        permission_classes = self.PERMISSION_MAP.get(self.action, [])
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        return self.SERIALIZER_MAP.get(self.action, None)

    @action(detail=False, methods=["get"])
    def me(self, request):
        classes = self.get_queryset()
        page = self.paginate_queryset(classes)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"], url_path="my-enrollment")
    def my_enrollment(self, request, pk=None):
        enrollment = self.get_object().enrollments.get(user=request.user)
        return Response(
            data=self.get_serializer(enrollment).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get", "post"], url_path="access")
    def access(self, request, pk=None):
        course_class = self.get_object()
        object_key = f"{CourseClassRelation.TYPE}:{course_class.pk}"

        def list_user_ids(relation: str) -> list[str]:
            tuples = fga_client.read(
                ReadRequestTupleKey(object=object_key, relation=relation)
            ).tuples
            prefix = f"{UserRelation.TYPE}:"
            return [t.key.user.removeprefix(prefix) for t in tuples if t.key.user.startswith(prefix)]

        if request.method.lower() == "get":
            data = {
                "teacher": list_user_ids(CourseClassRelation.TEACHER),
                "editor": list_user_ids(CourseClassRelation.EDITOR),
                "student": list_user_ids(CourseClassRelation.STUDENT),
                "guest": list_user_ids(CourseClassRelation.GUEST),
            }
            return Response(data)

        # POST: push updates for provided roles only (others unchanged)
        payload = request.data or {}
        updated_roles = {}
        for role, relation in (
            ("teacher", CourseClassRelation.TEACHER),
            ("editor", CourseClassRelation.EDITOR),
            ("student", CourseClassRelation.STUDENT),
            ("guest", CourseClassRelation.GUEST),
        ):
            if role in payload:
                ids = payload.get(role) or []
                try:
                    desired_ids = {str(int(i)) for i in ids}
                except Exception:
                    return Response({role: ["Must be a list of user ids."]}, status=status.HTTP_400_BAD_REQUEST)
                sync_single_type_subjects(
                    object_key=object_key,
                    subject_type=UserRelation.TYPE,
                    relation=relation,
                    desired_subject_ids=desired_ids,
                )
                updated_roles[role] = list(desired_ids)

        return Response({"updated": updated_roles}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get", "put"], url_path="roles/(?P<role>[^/.]+)")
    def role_access(self, request, role=None, pk=None):
        """Manage a single role's user list for this class.

        GET: returns serialized users in the role.
        PUT: replaces users for the role with provided list of ids.
        """
        role_map = {
            "teacher": CourseClassRelation.TEACHER,
            "editor": CourseClassRelation.EDITOR,
            "student": CourseClassRelation.STUDENT,
            "guest": CourseClassRelation.GUEST,
        }
        relation = role_map.get((role or "").lower())
        if not relation:
            return Response({"detail": "Unknown role"}, status=status.HTTP_404_NOT_FOUND)

        course_class = self.get_object()
        object_key = f"{CourseClassRelation.TYPE}:{course_class.pk}"

        def list_users_for_relation(rel: str):
            tuples = fga_client.read(ReadRequestTupleKey(object=object_key, relation=rel)).tuples
            prefix = f"{UserRelation.TYPE}:"
            ids = [t.key.user.removeprefix(prefix) for t in tuples if t.key.user.startswith(prefix)]
            User = get_user_model()
            users = list(User.objects.filter(pk__in=ids))
            return UserReadSerializer(users, many=True).data

        if request.method.lower() == "get":
            return Response({"users": list_users_for_relation(relation)})

        # PUT: replace with provided list of user ids
        ids = request.data.get("users")
        if not isinstance(ids, list):
            return Response({"users": ["Must be a list of user ids."]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            desired_ids = {str(int(i)) for i in ids}
        except Exception:
            return Response({"users": ["All ids must be integers."]}, status=status.HTTP_400_BAD_REQUEST)

        sync_single_type_subjects(
            object_key=object_key,
            subject_type=UserRelation.TYPE,
            relation=relation,
            desired_subject_ids=desired_ids,
        )
        return Response({"users": list_users_for_relation(relation)})
