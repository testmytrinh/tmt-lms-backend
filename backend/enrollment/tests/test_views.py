from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from courses.models import Course, CourseClass

User = get_user_model()


class EnrollmentCreationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpass", is_active=True
        )
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse("enrollment-list")

    def test_enroll_to_open_class(self):
        course = Course.objects.create(name="C1", description="D")
        open_class = CourseClass.objects.create(
            name="C1-Open", course=course, is_open=True
        )
        payload = {"course_class": open_class.id}
        resp = self.client.post(self.list_url, data=payload)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["course_class"], open_class.id)

    def test_enroll_to_closed_class(self):
        course = Course.objects.create(name="C1", description="D")
        closed_class = CourseClass.objects.create(
            name="C1-Closed", course=course, is_open=False
        )
        payload = {"course_class": closed_class.id}
        resp = self.client.post(self.list_url, data=payload)
        self.assertEqual(resp.status_code, 400)
