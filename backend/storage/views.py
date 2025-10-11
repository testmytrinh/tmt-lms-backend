from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from services.s3.storages import PublicMediaStorage, PrivateMediaStorage
from services.s3 import settings as s3_settings
from services.s3 import utils as s3_utils

from . import selectors

from .permissions import (
    CanEditFileInOFGA,
    CanEditFolderInOFGA,
    CanListFoldersInOFGA,
    CanListFilesInOFGA,
    CanViewFileInOFGA,
    CanViewFolderInOFGA,
)
from .serializers import (
    FileWriteSerializer,
    FileReadSerializer,
    FolderWriteSerializer,
    FolderReadSerializer,
)


class FolderViewSet(viewsets.ModelViewSet):
    PERMISSION_MAP = {
        "list": [CanListFoldersInOFGA],
        "retrieve": [IsAdminUser | CanViewFolderInOFGA],
        "create": [IsAuthenticated],
        "update": [CanEditFolderInOFGA],
        "partial_update": [CanEditFolderInOFGA],
        "destroy": [IsAdminUser | CanEditFolderInOFGA],
    }
    SERIALIZER_MAP = {
        "list": FolderReadSerializer,
        "retrieve": FolderReadSerializer,
        "create": FolderWriteSerializer,
        "update": FolderWriteSerializer,
        "partial_update": FolderWriteSerializer,
    }

    def get_queryset(self):
        return selectors.get_all_folders()

    def get_permissions(self):
        permission_classes = self.PERMISSION_MAP[self.action]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        return self.SERIALIZER_MAP[self.action]

    def list(self, request, *args, **kwargs):
        parent_id = request.query_params.get("parent")
        if parent_id:
            self.queryset = self.queryset.filter(parent_id=parent_id)
        else:
            self.queryset = self.queryset.filter(
                parent__isnull=True, owner=request.user
            )
        return super().list(request, *args, **kwargs)


class FileViewSet(viewsets.ModelViewSet):
    PERMISSION_MAP = {
        "list": [CanListFilesInOFGA],
        "retrieve": [CanViewFileInOFGA],
        "create": [IsAuthenticated],
        "update": [CanEditFileInOFGA],
        "partial_update": [CanEditFileInOFGA],
        "destroy": [CanEditFileInOFGA],
        # "presign_upload": [IsAuthenticated],
        # "download": [CanViewFileInOFGA],
    }
    SERIALIZER_MAP = {
        "list": FileReadSerializer,
        "retrieve": FileReadSerializer,
        "create": FileWriteSerializer,
        "update": FileWriteSerializer,
        "partial_update": FileWriteSerializer,
    }

    def get_queryset(self):
        return selectors.get_all_files()

    def get_permissions(self):
        permission_classes = self.PERMISSION_MAP[self.action]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        return self.SERIALIZER_MAP[self.action]

    def list(self, request, *args, **kwargs):
        folder_id = request.query_params.get("folder")
        if folder_id:
            self.queryset = self.queryset.filter(folder_id=folder_id)
        else:
            self.queryset = self.queryset.filter(
                folder__isnull=True, owner=request.user
            )
        return super().list(request, *args, **kwargs)

    # @action(detail=False, methods=["post"], url_path="presign-upload")
    # def presign_upload(self, request):
    #     filename = request.data.get("filename")
    #     content_type = request.data.get("content_type", "application/octet-stream")
    #     is_public = bool(request.data.get("is_public", False))
    #     folder_id = request.data.get("folder")

    #     if not filename:
    #         return Response({"filename": ["This field is required."]}, status=400)

    #     folder = None
    #     if folder_id:
    #         folder = Folder.objects.filter(id=folder_id, owner=request.user).first()
    #         if not folder:
    #             return Response({"folder": ["Invalid folder."]}, status=400)

    #     base_prefix = "media/public" if is_public else "media/private"
    #     owner_prefix = f"users/{request.user.id}"
    #     folder_prefix = f"folders/{folder.id}" if folder else "root"
    #     prefix = f"{base_prefix}/{owner_prefix}/{folder_prefix}"
    #     key = s3_utils.generate_object_key(prefix, filename)
    #     bucket = s3_settings.AWS_STORAGE_BUCKET_NAME
    #     acl = "public-read" if is_public else "private"
    #     presign = s3_utils.create_presigned_post(bucket, key, content_type, acl=acl)

    #     # Reserve DB record
    #     file = File.objects.create(
    #         owner=request.user,
    #         folder=folder,
    #         name=filename,
    #         bucket=bucket,
    #         key=key,
    #         content_type=content_type,
    #         is_public=is_public,
    #     )

    #     return Response(
    #         {
    #             "id": file.id,
    #             "bucket": bucket,
    #             "key": key,
    #             "is_public": is_public,
    #             "upload": presign,
    #         },
    #         status=201,
    #     )

    # @action(detail=True, methods=["get"], url_path="download")
    # def download(self, request, pk=None):
    #     file = self.get_object()

    #     if file.is_public:
    #         storage = PublicMediaStorage()
    #         url = storage.url(file.key.removeprefix(storage.location + "/"))
    #         return Response({"url": url})

    #     # private
    #     storage = PrivateMediaStorage()
    #     url = storage.url(file.key.removeprefix(storage.location + "/"))
    #     return Response({"url": url})
