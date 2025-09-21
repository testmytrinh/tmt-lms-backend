from django.test import TestCase
from django.db.models import signals

from ..models import Course, CourseCategory, CourseClass
from ..signals import sync_course_class_open_access, cleanup_course_class_in_ofga


class CourseCategoryModelTest(TestCase):
    def test_create_course_category(self):
        category = CourseCategory.objects.create(
            name="Mathematics", description="Math courses"
        )
        self.assertEqual(category.name, "Mathematics")
        self.assertEqual(category.description, "Math courses")


class CourseModelTest(TestCase):
    def test_create_course(self):
        course = Course.objects.create(
            name="Algebra 101", description="Basic Algebra Course", is_active=True
        )
        self.assertEqual(course.name, "Algebra 101")
        self.assertEqual(course.description, "Basic Algebra Course")
        self.assertTrue(course.is_active)


class CourseClassModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # Turn off the syncing signals for model testing
        is_disconnected = all(
            [
                signals.post_save.disconnect(
                    sync_course_class_open_access,
                    sender=CourseClass,
                    dispatch_uid="sync_course_class_open_access",
                ),
                signals.post_delete.disconnect(
                    cleanup_course_class_in_ofga,
                    sender=CourseClass,
                    dispatch_uid="cleanup_course_class_in_ofga",
                ),
            ]
        )
        assert is_disconnected, "Failed to disconnect signals"
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        # Reconnect the signals after tests
        signals.post_save.connect(
            sync_course_class_open_access,
            sender=CourseClass,
            dispatch_uid="sync_course_class_open_access",
        )
        signals.post_delete.connect(
            cleanup_course_class_in_ofga,
            sender=CourseClass,
            dispatch_uid="cleanup_course_class_in_ofga",
        )
        return super().tearDownClass()

    def test_create_course_class(self):
        course = Course.objects.create(
            name="Biology 101", description="Basic Biology Course", is_active=True
        )
        course_class = CourseClass.objects.create(
            name="Biology 101 - Fall 2024",
            description="Fall semester class",
            is_open=True,
            is_active=True,
            course=course,
        )
        self.assertEqual(course_class.name, "Biology 101 - Fall 2024")
        self.assertEqual(course_class.description, "Fall semester class")
        self.assertTrue(course_class.is_open)
        self.assertTrue(course_class.is_active)
        self.assertEqual(course_class.course, course)
