from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    DjangoModelPermissions,
)

from . import queries
from .models import (
    CourseTemplate,
    Module,
    Enrollment,
    Lesson,
    StudyGroup,
)
from .permissions import UserCanEditClass, UserCanViewClass
from .serializers import (
    CourseSerializer,
    CourseCategorySerializer,
    CourseClassReadSerializer,
    CourseClassWriteSerializer,
    CourseTemplateSerializer,
    ModuleSerializer,
    EnrollmentSerializer,
    LessonSerializer,
    StudyGroupSerializer,
)


class CourseViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
):
    permission_classes = [AllowAny]
    queryset = queries.get_all_courses()
    serializer_class = CourseSerializer


class CourseCategoryViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
):
    permission_classes = [AllowAny]
    queryset = queries.get_all_course_categories()
    serializer_class = CourseCategorySerializer


class CourseClassViewSet(viewsets.ModelViewSet):
    QUERYSET_MAP = {
        "list": lambda req: queries.get_active_open_classes(),
        "retrieve": lambda req: queries.get_visible_classes(req.user),
        "update": lambda req: queries.get_all_classes(),
        "partial_update": lambda req: queries.get_all_classes(),
        "destroy": lambda req: queries.get_all_classes(),
        "me": lambda req: queries.get_user_classes(req.user),
    }
    PERMISSION_MAP = {
        "list": [AllowAny],
        "retrieve": [AllowAny],
        "create": [DjangoModelPermissions],
        "update": [IsAuthenticated, DjangoModelPermissions | UserCanEditClass],
        "partial_update": [
            IsAuthenticated,
            DjangoModelPermissions | UserCanEditClass,
        ],
        "destroy": [IsAuthenticated, DjangoModelPermissions],
        "me": [IsAuthenticated],
    }
    SERIALIZER_MAP = {
        "list": CourseClassReadSerializer,
        "retrieve": CourseClassReadSerializer,
        "create": CourseClassWriteSerializer,
        "update": CourseClassWriteSerializer,
        "partial_update": CourseClassWriteSerializer,
        "destroy": CourseClassWriteSerializer,
        "me": CourseClassReadSerializer,
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
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(classes, many=True)
        return Response(serializer.data)


class CourseTemplateViewSet(viewsets.ModelViewSet):
    queryset = CourseTemplate.objects.all()
    serializer_class = CourseTemplateSerializer


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class StudyGroupViewSet(viewsets.ModelViewSet):
    queryset = StudyGroup.objects.all()
    serializer_class = StudyGroupSerializer
