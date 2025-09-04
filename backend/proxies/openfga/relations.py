from enum import StrEnum


class Group(StrEnum):
    TYPE = "group"


class User(StrEnum):
    TYPE = "user"


class CourseClass(StrEnum):
    TYPE = "course_class"
    TEACHER = "teacher"
    STUDENT = "student"
    GUEST = "guest"
    CAN_EDIT = "can_edit"
    CAN_VIEW = "can_view"
