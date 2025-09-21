from django.db.models import Q, Exists, OuterRef
from django.utils import timezone
from datetime import timedelta

from .models import (
    Enrollment,
    EnrollmentRole,
)


def get_all_enrollments():
    return Enrollment.objects.all()


def count_course_class_enrollments(course_class_id):
    return Enrollment.objects.filter(course_class_id=course_class_id).count()


def get_course_class_teachers_enrollment(course_class_id):
    return Enrollment.objects.filter(
        course_class_id=course_class_id, role=EnrollmentRole.TEACHER
    )


def get_enrollments_this_month():
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return Enrollment.objects.filter(enrolled_at__gte=start_of_month)
