from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from courses.models import Course, CourseClass
from enrollment.models import Enrollment, EnrollmentRole

User = get_user_model()


class EnrollmentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="pass123", is_active=True
        )
        self.course = Course.objects.create(name="C1", description="D")
        self.course_class = CourseClass.objects.create(name="C1-A", course=self.course)

    def test_default_role_is_guest(self):
        e = Enrollment.objects.create(user=self.user, course_class=self.course_class)
        self.assertEqual(e.role, EnrollmentRole.GUEST.value)

    def test_unique_enrollment_per_user_per_class(self):
        Enrollment.objects.create(user=self.user, course_class=self.course_class)
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(user=self.user, course_class=self.course_class)
