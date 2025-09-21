from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from enrollment.models import Enrollment

from ..models import Course, CourseCategory, CourseClass

User = get_user_model()


class CourseCategoryViewTests(APITestCase):
    def test_list_course_categories(self):
        response = self.client.get(reverse("course-category-list"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data["results"], list)

    def test_retrieve_course_category(self):
        category = CourseCategory.objects.create(
            name="Test Category", description="A test category"
        )
        response = self.client.get(
            reverse("course-category-detail", args=[category.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test Category")


class CourseViewTests(APITestCase):
    def test_list_courses(self):
        response = self.client.get(reverse("course-list"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data["results"], list)

    def test_retrieve_course(self):
        course = Course.objects.create(name="Test Course", description="A test course")
        response = self.client.get(reverse("course-detail", args=[course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test Course")


class CourseClassViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpass123", is_active=True
        )
        access_token = (
            self.client.post(
                reverse("token_obtain_pair"),
                data={"email": self.user.email, "password": "testpass123"},
            )
            .json()
            .get("access")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_list_course_classes(self):
        response = self.client.get(reverse("course-class-list"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data["results"], list)

    def test_retrieve_course_class_not_found(self):
        # Not found because the class is not open & user is not enrolled
        course = Course.objects.create(name="Test Course", description="A test course")
        course_class = CourseClass.objects.create(
            course=course,
            name="Test Class",
            start_date="2023-01-01",
            end_date="2023-06-01",
            is_active=True,
            is_open=False,
        )
        response = self.client.get(
            reverse("course-class-detail", args=[course_class.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_my_course_classes(self):
        course = Course.objects.create(name="Test Course", description="A test course")
        class_1 = CourseClass.objects.create(
            course=course,
            name="Test Class 1",
            start_date="2023-01-01",
            end_date="2023-06-01",
            is_active=True,
            is_open=False,
        )
        class_2 = CourseClass.objects.create(
            course=course,
            name="Test Class 2",
            start_date="2023-01-01",
            end_date="2023-06-01",
            is_active=True,
            is_open=True,
        )
        Enrollment.objects.create(user=self.user, course_class=class_1)
        Enrollment.objects.create(user=self.user, course_class=class_2)
        response = self.client.get(reverse("course-class-me"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data["results"], list)
        self.assertEqual(len(response.data["results"]), 2)
