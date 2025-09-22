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
    content_object_data = serializers.JSONField(write_only=True, required=False)
    content_object = serializers.SerializerMethodField()

    def get_content_object(self, obj):
        if isinstance(obj.content_object, Module):
            return ModuleSerializer(obj.content_object).data
        elif isinstance(obj.content_object, Lesson):
            return LessonSerializer(obj.content_object).data
        return None

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
            "content_object",
        ]

    def _get_model_and_serializer(self, content_type: ContentType):
        type_str = content_type.model or ""
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
        content_object_data = attrs.pop("content_object_data", {})
        is_created = self.instance is None

        # If updating, prevent changing content_type
        if (
            not is_created
            and content_type
            and content_type != self.instance.content_type
        ):
            raise serializers.ValidationError(
                {"content_type": "Changing content type is not allowed."}
            )
        # If updating, use existing content_type if not provided
        if not is_created and not content_type:
            content_type = self.instance.content_type

        ModelClass, SerClass = self._get_model_and_serializer(content_type)
        attrs["_content_model"] = ModelClass
        attrs["_content_serializer"] = SerClass

        if not is_created:
            try:
                obj = ModelClass.objects.get(pk=self.instance.object_id)
            except ModelClass.DoesNotExist:
                raise serializers.ValidationError({"object_id": "Object not found."})
            attrs["_content_instance"] = obj

        nested = SerClass(data=content_object_data)
        nested.is_valid(raise_exception=True)
        attrs["_content_validated_data"] = nested.validated_data
        return attrs

    def create(self, validated_data):
        ModelClass = validated_data.pop("_content_model")
        _SerClass = validated_data.pop("_content_serializer")

        if "_content_instance" in validated_data:
            content_obj = validated_data.pop("_content_instance")
        else:
            content_obj = ModelClass.objects.create(
                **validated_data.pop("_content_validated_data")
            )

        node = ContentNode.objects.create(
            object_id=content_obj.pk,
            **validated_data,
        )
        return node

    def update(self, instance: ContentNode, validated_data):
        if content_validated_data := validated_data.get("_content_validated_data"):
            ser = validated_data.pop("_content_serializer")(
                instance=instance.content_object,
                data=content_validated_data,
                partial=True,
            )
            ser.is_valid(raise_exception=True)
            ser.save()
        instance.full_clean()
        return super().update(instance, validated_data)


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
