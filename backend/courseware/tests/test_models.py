from django.test import TestCase
from django.contrib.auth import get_user_model

from courses.models import CourseClass, Course

from ..models import ContentNode, Module, Lesson

User = get_user_model()


class ContentNodeCreationTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            name="Test Course", description="A test course"
        )
        self.course_class = CourseClass.objects.create(
            course=self.course,
            name="Test Class",
            start_date="2023-01-01",
            end_date="2023-06-01",
        )
        return super().setUp()

    def test_create_valid_content_node(self):
        module = Module.objects.create(content="Content of test module")

        content_node = ContentNode.objects.create(
            title="Module 1",
            content_object=module,
            course_class=self.course_class,
            order=1,
        )
        self.assertIsInstance(content_node, ContentNode)
        self.assertEqual(content_node.content_object, module)
        self.assertEqual(content_node.course_class, self.course_class)
        self.assertEqual(content_node.order, 1)
        self.assertIsNone(content_node.parent)
        self.assertEqual(content_node.content_type.model, "module")
        self.assertEqual(content_node.children.count(), 0)

    def test_create_invalid_content_type(self):
        with self.assertRaises(Exception) as context:
            ContentNode.objects.create(
                title="Invalid Node",
                content_object=self.course_class,  # Invalid content type
                course_class=self.course_class,
                order=1,
            )
        self.assertIn("Content type", str(context.exception))

    def test_create_with_valid_parent(self):
        module = Module.objects.create(content="Content of test module")
        parent_node = ContentNode.objects.create(
            title="Module 1",
            content_object=module,
            course_class=self.course_class,
            order=1,
        )
        lesson = Lesson.objects.create(content="Content of test lesson")
        child_node = ContentNode.objects.create(
            title="Lesson 1",
            content_object=lesson,
            course_class=self.course_class,
            parent=parent_node,
            order=1,
        )
        self.assertEqual(child_node.parent, parent_node)
        self.assertEqual(parent_node.children.count(), 1)
        self.assertTrue(parent_node.children.filter(id=child_node.id).exists())

    def test_create_with_invalid_parent_course_class(self):
        module = Module.objects.create(content="Content of test module")
        parent_node = ContentNode.objects.create(
            title="Module 1",
            content_object=module,
            course_class=self.course_class,
            order=1,
        )
        other_course_class = CourseClass.objects.create(
            course=self.course,
            name="Other Class",
            start_date="2025-02-01",
            end_date="2025-07-01",
        )
        lesson = Lesson.objects.create(content="Content of test lesson")
        with self.assertRaises(Exception) as context:
            ContentNode.objects.create(
                title="Lesson 1",
                content_object=lesson,
                course_class=other_course_class,  # Different course class
                parent=parent_node,
                order=1,
            )
        self.assertIn(
            "Parent node must belong to the same course class", str(context.exception)
        )

    def test_create_with_invalid_parent_type(self):
        lesson = Lesson.objects.create(content="Content of test lesson")
        parent_node = ContentNode.objects.create(
            title="Lesson 1",
            content_object=lesson,
            course_class=self.course_class,
            order=1,
        )
        another_lesson = Lesson.objects.create(content="Another test lesson")
        with self.assertRaises(Exception) as context:
            ContentNode.objects.create(
                title="Sub Lesson",
                content_object=another_lesson,
                course_class=self.course_class,
                parent=parent_node,  # Parent is a lesson, should be module
                order=1,
            )
        self.assertIn(
            "Parent node must be of type 'module' or None", str(context.exception)
        )

    def test_not_exceed_max_depth(self):
        root_module = ContentNode.objects.create(
            title="Module 1",
            content_object=Module.objects.create(content="Content of module 1"),
            course_class=self.course_class,
            order=1,
        )
        child1_module = ContentNode.objects.create(
            title="Module 1.1",
            content_object=Module.objects.create(content="Content of module 1.1"),
            course_class=self.course_class,
            parent=root_module,
            order=1,
        )
        child2_module = ContentNode.objects.create(
            title="Module 1.1.1",
            content_object=Module.objects.create(content="Content of module 1.1.1"),
            course_class=self.course_class,
            parent=child1_module,
            order=1,
        )
        try:
            ContentNode.objects.create(
                title="Lesson 1.1.1",
                content_object=Lesson.objects.create(content="Content of lesson 1.1.1"),
                course_class=self.course_class,
                parent=child2_module,
                order=1,
            )
        except Exception as e:
            self.fail(f"Creation failed unexpectedly: {e}")

    def test_exceed_max_depth(self):
        root_module = ContentNode.objects.create(
            title="Module 1",
            content_object=Module.objects.create(content="Content of module 1"),
            course_class=self.course_class,
            order=1,
        )
        child1_module = ContentNode.objects.create(
            title="Module 1.1",
            content_object=Module.objects.create(content="Content of module 1.1"),
            course_class=self.course_class,
            parent=root_module,
            order=1,
        )
        child2_module = ContentNode.objects.create(
            title="Module 1.1.1",
            content_object=Module.objects.create(content="Content of module 1.1.1"),
            course_class=self.course_class,
            parent=child1_module,
            order=1,
        )
        child3_module = ContentNode.objects.create(
            title="Module 1.1.1.1",
            content_object=Module.objects.create(content="Content of module 1.1.1.1"),
            course_class=self.course_class,
            parent=child2_module,
            order=1,
        )
        with self.assertRaises(Exception) as context:
            ContentNode.objects.create(
                title="Lesson 1.1.1.1",
                content_object=Lesson.objects.create(
                    content="Content of lesson 1.1.1.1"
                ),
                course_class=self.course_class,
                parent=child3_module,
                order=1,
            )
        self.assertIn("Exceeded maximum depth", str(context.exception))

    def test_duplicate_content_object(self):
        module = Module.objects.create(content="Content of test module")
        ContentNode.objects.create(
            title="Module 1",
            content_object=module,
            course_class=self.course_class,
            order=1,
        )
        with self.assertRaises(Exception) as context:
            ContentNode.objects.create(
                title="Module 1 Duplicate",
                content_object=module,  # Same content object
                course_class=self.course_class,
                order=2,
            )
        self.assertIn(
            "Content node with this Content type and Object id already exists.",
            str(context.exception),
        )
