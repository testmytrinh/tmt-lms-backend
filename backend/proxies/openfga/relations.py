from enum import StrEnum


class UserRelation(StrEnum):
    """User object type and relations"""

    TYPE = "user"


class GroupRelation(StrEnum):
    """Group object type and relations"""

    TYPE = "group"
    MEMBER = "member"


class CourseClassRelation(StrEnum):
    """Course Class object type and relations"""

    TYPE = "course_class"
    TEACHER = "teacher"
    STUDENT = "student"
    GUEST = "guest"
    CAN_EDIT = "can_edit"
    CAN_VIEW = "can_view"

    @staticmethod
    def get_all_relations():
        return [
            CourseClassRelation.TEACHER,
            CourseClassRelation.STUDENT,
            CourseClassRelation.GUEST,
            CourseClassRelation.CAN_EDIT,
            CourseClassRelation.CAN_VIEW,
        ]


class CourseTemplateRelation(StrEnum):
    """Course Template object type and relations"""

    TYPE = "course_template"
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"
    COURSE_CLASS = "course_class"
    CAN_MODIFY = "can_modify"
    CAN_EDIT = "can_edit"
    CAN_VIEW = "can_view"


class TemplateNodeRelation(StrEnum):
    """Template Node object type and relations"""

    TYPE = "template_node"
    TEMPLATE = "template"
    PARENT_NODE = "parent_node"
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"
    CAN_MODIFY = "can_modify"
    CAN_EDIT = "can_edit"
    CAN_VIEW = "can_view"


class FolderRelation(StrEnum):
    """Folder object type and relations"""

    TYPE = "folder"
    OWNER = "owner"
    PARENT = "parent"
    EDITOR = "editor"
    VIEWER = "viewer"
    CAN_EDIT = "can_edit"
    CAN_VIEW = "can_view"


class FileRelation(StrEnum):
    """File object type and relations"""

    TYPE = "file"
    OWNER = "owner"
    PARENT = "parent"
    EDITOR = "editor"
    VIEWER = "viewer"
    CAN_EDIT = "can_edit"
    CAN_VIEW = "can_view"
