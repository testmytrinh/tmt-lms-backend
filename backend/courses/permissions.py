from proxies.openfga.sync.permissions import FGABasePermission
from proxies.openfga.relations import CourseClassRelation, UserRelation


class UserCanEditCourseClass(FGABasePermission):
    relation = CourseClassRelation.CAN_EDIT
    subject_type = UserRelation.TYPE
    object_type = CourseClassRelation.TYPE

    def get_subject_id(self, request, view, obj) -> str:
        return str(request.user.id)

    def get_object_id(self, request, view, obj) -> str:
        return str(obj.id)


class UserCanViewCourseClass(FGABasePermission):
    relation = CourseClassRelation.CAN_VIEW
    subject_type = UserRelation.TYPE
    object_type = CourseClassRelation.TYPE

    def get_subject_id(self, request, view, obj) -> str:
        return str(request.user.id)

    def get_object_id(self, request, view, obj) -> str:
        return str(obj.id)
