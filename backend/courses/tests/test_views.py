from functools import partial
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from enrollment.models import Enrollment, EnrollmentRole

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

    def test_my_enrollment(self):
        course = Course.objects.create(name="Test Course", description="A test course")
        course_class_1 = CourseClass.objects.create(
            course=course,
            name="Test Class",
            start_date="2023-01-01",
            end_date="2023-06-01",
            is_active=True,
            is_open=False,
        )
        course_class_2 = CourseClass.objects.create(
            course=course,
            name="Open Class",
            start_date="2023-01-01",
            end_date="2023-06-01",
            is_active=True,
            is_open=False,
        )
        Enrollment.objects.create(
            user=self.user, course_class=course_class_1, role=EnrollmentRole.TEACHER
        )
        Enrollment.objects.create(
            user=self.user, course_class=course_class_2, role=EnrollmentRole.STUDENT
        )

        make_url = partial(reverse, "course-class-my-enrollment")
        response_1 = self.client.get(make_url(args=[course_class_1.id]))
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_1.data["role"], EnrollmentRole.TEACHER.label)
        self.assertTrue(response_1.data["access"]["can_edit"])
        self.assertTrue(response_1.data["access"]["can_view"])
        response_2 = self.client.get(make_url(args=[course_class_2.id]))
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_2.data["role"], EnrollmentRole.STUDENT.label)
        self.assertFalse(response_2.data["access"]["can_edit"])
        self.assertTrue(response_2.data["access"]["can_view"])

    def test_update_course_class_forbidden(self):
        course = Course.objects.create(name="Test Course", description="A test course")
        course_class = CourseClass.objects.create(
            course=course,
            name="Test Class",
            start_date="2023-01-01",
            end_date="2023-06-01",
            is_active=True,
            is_open=True,
        )
        response = self.client.put(
            reverse("course-class-detail", args=[course_class.id]),
            data={
                "name": "Updated Class Name",
                "start_date": "2023-01-01",
                "end_date": "2023-06-01",
                "is_active": True,
                "is_open": True,
                "course": course.id,
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_my_enrollment_not_found(self):
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
            reverse("course-class-my-enrollment", args=[course_class.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_update_course_class_success(self):
        course = Course.objects.create(name="Test Course", description="A test course")
        course_class = CourseClass.objects.create(
            course=course,
            name="Test Class",
            start_date="2023-01-01",
            end_date="2023-06-01",
            is_active=True,
            is_open=True,
        )
        Enrollment.objects.create(
            user=self.user, course_class=course_class, role=EnrollmentRole.TEACHER
        )
        response = self.client.patch(
            reverse("course-class-detail", args=[course_class.id]),
            data={
                "name": "Updated Class Name",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Class Name")
