from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from openfga_sdk.client.models import ClientCheckRequest

from services.openfga.sync import client as ofga
from services.openfga.relations import CourseClassRelation, UserRelation
from enrollment.models import Enrollment


from ..models import Course, CourseClass

User = get_user_model()


class CourseClassAuthzTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpass123", is_active=True
        )

    def test_create_open_course_class_sync(self):
        course = Course.objects.create(name="Test Course", description="A test course")
        course_class = CourseClass.objects.create(
            course=course,
            name="Open Class",
            start_date="2023-01-01",
            end_date="2023-06-01",
            is_active=True,
            is_open=True,
        )
        is_open_access = ofga.check(
            ClientCheckRequest(
                user=f"{UserRelation.TYPE}:{self.user.id}",
                relation=CourseClassRelation.CAN_VIEW,
                object=f"{CourseClassRelation.TYPE}:{course_class.id}",
            )
        ).allowed
        self.assertTrue(is_open_access)

    def test_create_closed_course_class_sync(self):
        course = Course.objects.create(name="Test Course", description="A test course")
        course_class = CourseClass.objects.create(
            course=course,
            name="Closed Class",
            start_date="2023-01-01",
            end_date="2023-06-01",
            is_active=True,
            is_open=False,
        )
        is_closed_access = ofga.check(
            ClientCheckRequest(
                user=f"{UserRelation.TYPE}:{self.user.id}",
                relation=CourseClassRelation.CAN_VIEW,
                object=f"{CourseClassRelation.TYPE}:{course_class.id}",
            )
        ).allowed
        self.assertFalse(is_closed_access)

    def test_course_class_cleanup_on_delete(self):
        course = Course.objects.create(name="Test Course", description="A test course")
        course_class = CourseClass.objects.create(
            course=course,
            name="To Be Deleted Class",
            start_date="2023-01-01",
            end_date="2023-06-01",
            is_active=True,
            is_open=False,
        )
        Enrollment.objects.create(user=self.user, course_class=course_class)
        course_class_id = course_class.id
        course_class.delete()
        is_access_after_delete = ofga.check(
            ClientCheckRequest(
                user=f"{UserRelation.TYPE}:{self.user.id}",
                relation=CourseClassRelation.CAN_VIEW,
                object=f"{CourseClassRelation.TYPE}:{course_class_id}",
            )
        ).allowed
        self.assertFalse(is_access_after_delete)
