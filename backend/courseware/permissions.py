from rest_framework.permissions import BasePermission
from openfga_sdk.client.models import ClientCheckRequest
from services.openfga.sync import client as fga
from services.openfga.relations import (
    ContentNodeRelation,
    UserRelation,
    CourseClassRelation,
)


class UserCanListClasssNodes(BasePermission):
    def has_permission(self, request, view):
        subject_id = request.user.pk if request.user.is_authenticated else "*"
        subject_key = f"{UserRelation.TYPE}:{subject_id}"
        object_key = f"{CourseClassRelation.TYPE}:{view.kwargs.get('class_id')}"
        return fga.check(
            ClientCheckRequest(
                user=subject_key,
                relation=CourseClassRelation.CAN_VIEW,
                object=object_key,
            )
        ).allowed


class UserCanCreateClassNodes(BasePermission):
    def has_permission(self, request, view):
        subject_id = request.user.pk if request.user.is_authenticated else "*"
        subject_key = f"{UserRelation.TYPE}:{subject_id}"
        object_key = f"{CourseClassRelation.TYPE}:{view.kwargs.get('class_id')}"
        return fga.check(
            ClientCheckRequest(
                user=subject_key,
                relation=CourseClassRelation.CAN_EDIT,
                object=object_key,
            )
        ).allowed


class UserCanViewContentNode(BasePermission):
    def has_object_permission(self, request, view, obj):
        subject_id = request.user.pk if request.user.is_authenticated else "*"
        subject_key = f"{UserRelation.TYPE}:{subject_id}"
        object_key = f"{ContentNodeRelation.TYPE}:{obj.pk}"
        relation = ContentNodeRelation.CAN_VIEW

        return fga.check(
            ClientCheckRequest(
                user=subject_key,
                relation=relation,
                object=object_key,
            )
        ).allowed


class UserCanEditContentNode(BasePermission):
    def has_object_permission(self, request, view, obj):
        subject_id = request.user.pk if request.user.is_authenticated else "*"
        subject_key = f"{UserRelation.TYPE}:{subject_id}"
        object_key = f"{ContentNodeRelation.TYPE}:{obj.pk}"
        relation = ContentNodeRelation.CAN_EDIT

        return fga.check(
            ClientCheckRequest(
                user=subject_key,
                relation=relation,
                object=object_key,
            )
        ).allowed


class UserCanModifyContentNode(BasePermission):
    def has_object_permission(self, request, view, obj):
        subject_id = request.user.pk if request.user.is_authenticated else "*"
        subject_key = f"{UserRelation.TYPE}:{subject_id}"
        object_key = f"{ContentNodeRelation.TYPE}:{obj.pk}"
        relation = ContentNodeRelation.CAN_MODIFY

        return fga.check(
            ClientCheckRequest(
                user=subject_key,
                relation=relation,
                object=object_key,
            )
        ).allowed
