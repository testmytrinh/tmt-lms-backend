from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType


from .models import Lesson, Module, ContentNode


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class ContentNodeListSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(source="content_type.model")

    class Meta:
        model = ContentNode
        fields = "__all__"


class ContentNodeDetailSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(source="content_type.model")
    content_object = serializers.SerializerMethodField()

    def get_content_object(self, obj):
        if isinstance(obj.content_object, Module):
            return ModuleSerializer(obj.content_object).data
        elif isinstance(obj.content_object, Lesson):
            return LessonSerializer(obj.content_object).data
        return None

    class Meta:
        model = ContentNode
        fields = "__all__"


class ContentNodeWriteSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        slug_field="model",  # or use "id"
        queryset=ContentType.objects.all(),
    )

    class Meta:
        model = ContentNode
        fields = "__all__"


class ContentNodeTreeSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(source="content_type.model")
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        if obj.children.exists():
            return ContentNodeTreeSerializer(obj.children.all(), many=True).data
        return []

    class Meta:
        model = ContentNode
        fields = "__all__"
