from proxies.openfga.sync.permissions import FGABasePermission
from proxies.openfga.relations import CourseClass, User

class UserCanEditClass(FGABasePermission):
    relation = CourseClass.CAN_EDIT
    subject_type = User.TYPE
    object_type = CourseClass.TYPE

    def get_subject_id(self, request, view, obj) -> str:
        return str(request.user.id)

    def get_object_id(self, request, view, obj) -> str:
        return str(obj.id)

class UserCanViewClass(FGABasePermission):
    relation = CourseClass.CAN_VIEW
    subject_type = User.TYPE
    object_type = CourseClass.TYPE

    def get_subject_id(self, request, view, obj) -> str:
        return str(request.user.id)

    def get_object_id(self, request, view, obj) -> str:
        return str(obj.id)