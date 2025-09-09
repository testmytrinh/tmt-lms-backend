from django.db.models import Q, Exists, OuterRef

from .models import (
    CourseClass,
    Enrollment,
    StudyGroup,
)
