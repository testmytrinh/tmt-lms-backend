from enum import Enum
from functools import partial

from django.contrib.auth.models import Group


class InitGroup(Enum):
    ADMIN = partial(lambda: Group.objects.get_or_create(name="Admin")[0])
    TEACHER = partial(lambda: Group.objects.get_or_create(name="Teacher")[0])
    STUDENT = partial(lambda: Group.objects.get_or_create(name="Student")[0])
    GUEST = partial(lambda: Group.objects.get_or_create(name="Guest")[0])
