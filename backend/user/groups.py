from enum import StrEnum
from functools import partial

from django.contrib.auth.models import Group


class InitGroup(StrEnum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"