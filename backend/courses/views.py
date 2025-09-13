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

from .permissions import UserCanEditCourseClass
from .serializers import (
    CourseSerializer,
    CourseCategorySerializer,
    CourseClassReadSerializer,
    CourseClassWriteSerializer,
)


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
    }
    PERMISSION_MAP = {
        "list": [AllowAny],
        "retrieve": [AllowAny],
        "create": [DjangoModelPermissions],
        "update": [IsAuthenticated, DjangoModelPermissions, UserCanEditCourseClass],
        "partial_update": [
            IsAuthenticated,
            DjangoModelPermissions,
            UserCanEditCourseClass,
        ],
        "destroy": [IsAuthenticated, DjangoModelPermissions],
        "me": [IsAuthenticated],
        "my_enrollment": [IsAuthenticated],
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
