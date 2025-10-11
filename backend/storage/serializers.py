from rest_framework import serializers

from user.serializers import UserReadSerializer

from .models import Folder, File


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
