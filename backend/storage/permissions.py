from rest_framework.permissions import BasePermission
from types import SimpleNamespace
from openfga_sdk.client.models import ClientCheckRequest

from services.openfga.relations import UserRelation, FolderRelation, FileRelation
from services.openfga.sync import client as ofga


class CanViewFolderInOFGA(BasePermission):
    def has_object_permission(self, request, view, obj):
        subject_id = request.user.pk if request.user.is_authenticated else "*"
        subject_key = f"{UserRelation.TYPE}:{subject_id}"
        object_key = f"{FolderRelation.TYPE}:{obj.pk}"
        return ofga.check(
            ClientCheckRequest(
                user=subject_key,
                relation=FolderRelation.CAN_VIEW,
                object=object_key,
            )
        ).allowed


class CanEditFolderInOFGA(BasePermission):
    def has_object_permission(self, request, view, obj):
        subject_id = request.user.pk if request.user.is_authenticated else "*"
        subject_key = f"{UserRelation.TYPE}:{subject_id}"
        object_key = f"{FolderRelation.TYPE}:{obj.pk}"
        return ofga.check(
            ClientCheckRequest(
                user=subject_key,
                relation=FolderRelation.CAN_EDIT,
                object=object_key,
            )
        ).allowed


class CanListFoldersInOFGA(BasePermission):
    def has_permission(self, request, view):
        parent_id = request.query_params.get("parent")
        if not parent_id:
            return True  # Allow listing root folders
        return CanViewFolderInOFGA().has_object_permission(
            request, ..., SimpleNamespace(pk=parent_id)
        )


class CanViewFileInOFGA(BasePermission):
    def has_object_permission(self, request, view, obj):
        subject_id = request.user.pk if request.user.is_authenticated else "*"
        subject_key = f"{UserRelation.TYPE}:{subject_id}"
        object_key = f"{FileRelation.TYPE}:{obj.pk}"
        return ofga.check(
            ClientCheckRequest(
                user=subject_key,
                relation=FileRelation.CAN_VIEW,
                object=object_key,
            )
        ).allowed


class CanEditFileInOFGA(BasePermission):
    def has_object_permission(self, request, view, obj):
        subject_id = request.user.pk if request.user.is_authenticated else "*"
        subject_key = f"{UserRelation.TYPE}:{subject_id}"
        object_key = f"{FileRelation.TYPE}:{obj.pk}"
        return ofga.check(
            ClientCheckRequest(
                user=subject_key,
                relation=FileRelation.CAN_EDIT,
                object=object_key,
            )
        ).allowed


class CanListFilesInOFGA(BasePermission):
    def has_permission(self, request, view):
        folder_id = request.query_params.get("folder")
        if not folder_id:
            return True  # Allow listing root files
        return CanViewFolderInOFGA().has_object_permission(
            request, ..., SimpleNamespace(pk=folder_id)
        )
