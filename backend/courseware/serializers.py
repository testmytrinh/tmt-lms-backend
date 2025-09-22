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
    content_object_data = serializers.JSONField(write_only=True, required=True)

    class Meta:
        model = ContentNode
        fields = [
            "id",
            "title",
            "content_type",
            "course_class",
            "parent",
            "order",
            "content_object_data",
        ]

    def _get_model_and_serializer(self, type_str: str):
        type_str = (type_str or "").strip().lower()
        m = {
            "module": (Module, ModuleSerializer),
            "lesson": (Lesson, LessonSerializer),
        }
        if type_str in m:
            return m[type_str]
        raise serializers.ValidationError(
            {"content_type": f"Unsupported type: {type_str}"}
        )

    def validate(self, attrs):
        content_type = attrs.get("content_type")
        content_object_data = attrs.get("content_object_data", {})
        is_created = self.instance is None

        ModelClass, SerClass = self._get_model_and_serializer(content_type)

        if not is_created:
            try:
                obj = ModelClass.objects.get(pk=self.instance.object_id)
            except ModelClass.DoesNotExist:
                raise serializers.ValidationError({"object_id": "Object not found."})
            attrs["_content_instance"] = obj
            attrs["_content_model"] = ModelClass
        else:
            if not isinstance(content_object_data, dict):
                raise serializers.ValidationError(
                    {"content_object_data": "Must be an object"}
                )
            nested = SerClass(data=content_object_data)
            nested.is_valid(raise_exception=True)
            attrs["_content_validated_data"] = nested.validated_data
            attrs["_content_model"] = ModelClass
        return attrs

    def create(self, validated_data):
        ModelClass = validated_data.pop("_content_model")

        if "_content_instance" in validated_data:
            content_obj = validated_data.pop("_content_instance")
        else:
            content_obj = ModelClass.objects.create(
                **validated_data.pop("_content_validated_data")
            )

        ct = ContentType.objects.get_for_model(ModelClass)
        node = ContentNode.objects.create(
            content_type=ct,
            object_id=content_obj.pk,
            **validated_data,
        )
        return node

    def update(self, instance: ContentNode, validated_data):
        # If content update fields are provided, swap content
        has_type = "content_type" in self.initial_data
        _ = validated_data.pop("content_type", None)
        _ = validated_data.pop("object_id", None)
        _ = validated_data.pop("content_object_data", None)
        if has_type:
            ModelCls = validated_data.pop("_content_model")
            if "_content_instance" in validated_data:
                content_obj = validated_data.pop("_content_instance")
            else:
                content_obj = ModelCls.objects.create(
                    **validated_data.pop("_content_validated_data")
                )
            ct = ContentType.objects.get_for_model(ModelCls)
            instance.content_type = ct
            instance.object_id = content_obj.pk

        for field in ("title", "course_class", "parent", "order"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.full_clean()
        instance.save()
        return instance


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
