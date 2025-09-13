from proxies.openfga.sync.permissions import FGABasePermission
from proxies.openfga.relations import (
    CourseTemplateRelation,
    UserRelation,
    TemplateNodeRelation,
)
from .models import TemplateNode, Module, Lesson


class OFGAUserTemplate(FGABasePermission):
    subject_type = UserRelation.TYPE
    object_type = CourseTemplateRelation.TYPE

    def get_subject_id(self, request, view, obj) -> str:
        return str(request.user.id) if request.user.is_authenticated else "*"

    def get_object_id(self, request, view, obj) -> str:
        return str(obj.id)


class OFGAUserCanEditTemplate(OFGAUserTemplate):
    relation = CourseTemplateRelation.CAN_EDIT


class OFGAUserCanViewTemplate(OFGAUserTemplate):
    relation = CourseTemplateRelation.CAN_VIEW


class OFGAUserCanModifyTemplate(OFGAUserTemplate):
    relation = CourseTemplateRelation.CAN_MODIFY


class OFGAUserCanViewTemplateNodesInPath(FGABasePermission):
    relation = CourseTemplateRelation.CAN_VIEW
    subject_type = UserRelation.TYPE
    object_type = CourseTemplateRelation.TYPE

    def get_subject_id(self, request, view, obj) -> str:
        return str(request.user.id) if request.user.is_authenticated else "*"

    def get_object_id(self, request, view, obj) -> str:
        return view.kwargs.get("template_id")

    def has_permission(self, request, view):
        return self.check(
            subject_key=f"{self.subject_type}:{self.get_subject_id(request, view, None)}",
            relation=self.relation,
            object_key=f"{self.object_type}:{self.get_object_id(request, view, None)}",
        )


class OFGAUserNode(FGABasePermission):
    subject_type = UserRelation.TYPE
    object_type = TemplateNodeRelation.TYPE

    def get_subject_id(self, request, view, obj) -> str:
        return str(request.user.id) if request.user.is_authenticated else "*"

    def get_object_id(self, request, view, obj) -> str:
        return str(obj.id)


class OFGAUserCanModifyNode(OFGAUserNode):
    relation = TemplateNodeRelation.CAN_MODIFY


class OFGAUserCanViewNode(OFGAUserNode):
    relation = TemplateNodeRelation.CAN_VIEW


class OFGAUserCanEditNode(OFGAUserNode):
    relation = TemplateNodeRelation.CAN_EDIT


class OFGAUserModule(FGABasePermission):
    subject_type = UserRelation.TYPE
    object_type = TemplateNodeRelation.TYPE

    def get_subject_id(self, request, view, obj) -> str:
        return str(request.user.id) if request.user.is_authenticated else "*"

    def get_object_id(self, request, view, obj: Module) -> str:
        # Find the TemplateNode that references this Module
        node = TemplateNode.objects.get(content_type__model="module", object_id=obj.pk)
        return str(node.pk)


class OFGAUserCanEditModule(OFGAUserModule):
    relation = TemplateNodeRelation.CAN_EDIT


class OFGAUserCanViewModule(OFGAUserModule):
    relation = TemplateNodeRelation.CAN_VIEW


class OFGAUserLesson(FGABasePermission):
    subject_type = UserRelation.TYPE
    object_type = TemplateNodeRelation.TYPE

    def get_subject_id(self, request, view, obj) -> str:
        return str(request.user.id) if request.user.is_authenticated else "*"

    def get_object_id(self, request, view, obj: Lesson) -> str:
        # Find the TemplateNode that references this Lesson
        node = TemplateNode.objects.get(content_type__model="lesson", object_id=obj.pk)
        return str(node.pk)


class OFGAUserCanEditLesson(OFGAUserLesson):
    relation = TemplateNodeRelation.CAN_EDIT


class OFGAUserCanViewLesson(OFGAUserLesson):
    relation = TemplateNodeRelation.CAN_VIEW
