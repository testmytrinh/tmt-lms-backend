from enum import StrEnum


class UserRelation(StrEnum):
    TYPE = "user"


class GroupRelation(StrEnum):
    TYPE = "group"
    MEMBER = "member"


class CourseClassRelation(StrEnum):
    TYPE = "course_class"
    TEACHER = "teacher"
    EDITOR = "editor"
    STUDENT = "student"
    GUEST = "guest"
    CAN_MODIFY = "can_modify"
    CAN_EDIT = "can_edit"
    CAN_VIEW = "can_view"


class ContentNodeRelation(StrEnum):
    TYPE = "content_node"
    COURSE_CLASS = "course_class"
    PARENT = "parent"
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"
    CAN_MODIFY = "can_modify"
    CAN_EDIT = "can_edit"
    CAN_VIEW = "can_view"


class FolderRelation(StrEnum):
    TYPE = "folder"
    OWNER = "owner"
    PARENT = "parent"
    EDITOR = "editor"
    VIEWER = "viewer"
    CAN_EDIT = "can_edit"
    CAN_VIEW = "can_view"


class FileRelation(StrEnum):
    TYPE = "file"
    OWNER = "owner"
    PARENT = "parent"
    EDITOR = "editor"
    VIEWER = "viewer"
    CAN_EDIT = "can_edit"
    CAN_VIEW = "can_view"
