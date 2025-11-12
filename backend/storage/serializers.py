from rest_framework import serializers
from django.contrib.auth import get_user_model
from openfga_sdk import ReadRequestTupleKey, Tuple
from openfga_sdk.client.models import (
    ClientListRelationsRequest,
    ClientListObjectsRequest,
    ClientWriteRequest,
    ClientTuple,
)

from user.serializers import UserReadSerializer
from services.openfga.sync import client
from services.openfga.relations import FileRelation, FolderRelation, UserRelation

from .models import Folder, File

User = get_user_model()


class FolderWriteSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Folder
        fields = "__all__"


class FolderReadSerializer(serializers.ModelSerializer):
    owner = UserReadSerializer(read_only=True)

    class Meta:
        model = Folder
        fields = "__all__"


class FileWriteSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = File
        fields = "__all__"


class FileReadSerializer(serializers.ModelSerializer):
    owner = UserReadSerializer(read_only=True)
    folder = FolderReadSerializer(read_only=True)

    class Meta:
        model = File
        fields = "__all__"


class FileShareWriteSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=True)
    role = serializers.ChoiceField(
        choices=[
            (FileRelation.EDITOR, "Editor"),
            (FileRelation.VIEWER, "Viewer"),
        ],
        required=True,
    )

    def validate_user(self, value):
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

    def create(self, validated_data):
        return client.write(
            ClientWriteRequest(
                writes=[
                    ClientTuple(
                        user=f"{UserRelation.TYPE}:{validated_data['user']}",
                        relation=validated_data["role"],
                        object=f"{FileRelation.TYPE}:{self.context['file_id']}",
                    )
                ]
            )
        )


class FileShareReadSerializer(serializers.Serializer):
    user = UserReadSerializer(read_only=True)
    role = serializers.CharField(read_only=True)
