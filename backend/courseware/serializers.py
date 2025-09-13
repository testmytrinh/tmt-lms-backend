from rest_framework import serializers

from user.serializers import UserReadSerializer

from .models import CourseTemplate, Lesson, Module, TemplateNode


class CourseTemplateReadSerializer(serializers.ModelSerializer):
    owner = UserReadSerializer(read_only=True)

    class Meta:
        model = CourseTemplate
        fields = "__all__"


class CourseTemplateWriteSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

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


class TemplateNodeListSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(source="content_type.model")
    title = serializers.CharField(source="content_object.title", read_only=True)

    class Meta:
        model = TemplateNode
        fields = "__all__"


class TemplateNodeDetailSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(source="content_type.model")
    content_object = serializers.SerializerMethodField()

    def get_content_object(self, obj):
        if isinstance(obj.content_object, Module):
            return ModuleSerializer(obj.content_object).data
        elif isinstance(obj.content_object, Lesson):
            return LessonSerializer(obj.content_object).data
        return None

    class Meta:
        model = TemplateNode
        fields = "__all__"


class TemplateNodeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateNode
        fields = "__all__"
