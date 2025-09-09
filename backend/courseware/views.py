from rest_framework import viewsets

from .serializers import (
    CourseTemplateReadSerializer,
    ModuleSerializer,
    LessonSerializer,
    TemplateNodeSerializer,
)
from .pagination import StandardResultsSetPagination
from .models import CourseTemplate, TemplateNode, Module, Lesson


class CourseTemplateViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    queryset = CourseTemplate.objects.all()
    serializer_class = CourseTemplateReadSerializer


class TemplateNodeViewSet(viewsets.ModelViewSet):
    queryset = TemplateNode.objects.all()
    serializer_class = TemplateNodeSerializer


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# class StudyGroupViewSet(viewsets.ModelViewSet):
#     queryset = StudyGroup.objects.all()
#     serializer_class = StudyGroupSerializer
