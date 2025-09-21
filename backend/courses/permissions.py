from rest_framework.permissions import BasePermission
from openfga_sdk.client.models import ClientCheckRequest

from services.openfga.relations import CourseClassRelation, UserRelation
from services.openfga.sync import client


class UserCanModifyCourseClass(BasePermission):
    def has_object_permission(self, request, view, obj):
        subject_id = request.user.pk if request.user.is_authenticated else "*"
        subject_key = f"{UserRelation.TYPE}:{subject_id}"
        object_key = f"{CourseClassRelation.TYPE}:{obj.pk}"
        return client.check(
            ClientCheckRequest(
                user=subject_key,
                relation=CourseClassRelation.CAN_MODIFY,
                object=object_key,
            )
        ).allowed


class UserCanEditCourseClass(BasePermission):
    def has_object_permission(self, request, view, obj):
        subject_id = request.user.pk if request.user.is_authenticated else "*"
        subject_key = f"{UserRelation.TYPE}:{subject_id}"
        object_key = f"{CourseClassRelation.TYPE}:{obj.pk}"
        return client.check(
            ClientCheckRequest(
                user=subject_key,
                relation=CourseClassRelation.CAN_EDIT,
                object=object_key,
            )
        ).allowed


class UserCanViewCourseClass(BasePermission):
    def has_object_permission(self, request, view, obj):
        subject_id = request.user.pk if request.user.is_authenticated else "*"
        subject_key = f"{UserRelation.TYPE}:{subject_id}"
        object_key = f"{CourseClassRelation.TYPE}:{obj.pk}"
        return client.check(
            ClientCheckRequest(
                user=subject_key,
                relation=CourseClassRelation.CAN_VIEW,
                object=object_key,
            )
        ).allowed
