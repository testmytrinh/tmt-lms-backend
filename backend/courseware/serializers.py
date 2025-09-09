from rest_framework import serializers

from .models import CourseTemplate, Lesson, Module, TemplateNode


class CourseTemplateReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTemplate
        fields = "__all__"


class CourseTemplateWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTemplate
        fields = "__all__"


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"

class TemplateNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateNode
        fields = "__all__"