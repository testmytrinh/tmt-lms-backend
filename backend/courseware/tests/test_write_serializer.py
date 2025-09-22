from rest_framework import serializers
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from courses.models import Course, CourseClass
from courseware.models import ContentNode, Module, Lesson
from courseware.serializers import ContentNodeWriteSerializer


class ContentNodeWriteSerializerTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(name="C1", description="D")
        self.cls = CourseClass.objects.create(name="C1-A", course=self.course)

    def test_create_module_node(self):
        payload = {
            "title": "Module 1",
            "course_class": self.cls.id,
            "order": 1,
            "content_type": "module",
            "content_object_data": {"content": "Intro"},
        }
        ser = ContentNodeWriteSerializer(data=payload)
        self.assertTrue(ser.is_valid(), ser.errors)
        node = ser.save()
        self.assertIsInstance(node, ContentNode)
        self.assertEqual(node.title, "Module 1")
        self.assertEqual(node.course_class_id, self.cls.id)
        self.assertEqual(node.content_type.model, "module")
        self.assertIsInstance(node.content_object, Module)
        self.assertEqual(node.content_object.content, "Intro")

    def test_create_lesson_node(self):
        parent_module = Module.objects.create(content="Parent")
        parent_node = ContentNode.objects.create(
            title="Parent module",
            course_class=self.cls,
            order=1,
            content_type=ContentType.objects.get_for_model(Module),
            object_id=parent_module.id,
        )
        payload = {
            "title": "Lesson 1",
            "course_class": self.cls.id,
            "parent": parent_node.id,
            "order": 1,
            "content_type": "lesson",
            "content_object_data": {"content": "Lesson content"},
        }
        ser = ContentNodeWriteSerializer(data=payload)
        self.assertTrue(ser.is_valid(), ser.errors)
        node = ser.save()
        self.assertEqual(node.parent_id, parent_node.id)
        self.assertEqual(parent_node.children.count(), 1)
        self.assertIsInstance(node.content_object, Lesson)
        self.assertTrue(Lesson.objects.filter(content="Lesson content").exists())

    def test_update_swaps_content_object_fail(self):
        # create node with module
        node = ContentNode.objects.create(
            title="X",
            course_class=self.cls,
            order=1,
            content_type=ContentType.objects.get_for_model(Module),
            object_id=Module.objects.create(content="A").id,
        )
        payload = {"content_type": "lesson", "content_object_data": {"content": "B"}}
        ser = ContentNodeWriteSerializer(instance=node, data=payload, partial=True)
        with self.assertRaises(serializers.ValidationError) as ctx:
            ser.is_valid(raise_exception=True)
            ser.save()
        self.assertIn("Changing content type is not allowed", str(ctx.exception))

    def test_validation_errors(self):
        # missing content_type
        ser = ContentNodeWriteSerializer(
            data={
                "title": "Bad",
                "course_class": self.cls.id,
                "order": 1,
                "content_object_data": {"content": "X"},
            }
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("content_type", ser.errors)

        # unsupported type
        ser = ContentNodeWriteSerializer(
            data={
                "title": "Bad",
                "course_class": self.cls.id,
                "order": 1,
                "content_type": "file",
                "content_object_data": {"content": "X"},
            }
        )
        self.assertFalse(ser.is_valid())

    def test_update_lesson_content(self):
        # create node with lesson
        node = ContentNode.objects.create(
            title="Y",
            course_class=self.cls,
            order=1,
            content_type=ContentType.objects.get_for_model(Lesson),
            object_id=Lesson.objects.create(content="A").id,
        )
        payload = {"content_object_data": {"content": "B"}}
        ser = ContentNodeWriteSerializer(instance=node, data=payload, partial=True)
        self.assertTrue(ser.is_valid(), ser.errors)
        node2 = ser.save()
        self.assertEqual(node2.id, node.id)
        self.assertEqual(node2.content_type.model, "lesson")
        self.assertIsInstance(node2.content_object, Lesson)
        self.assertEqual(node2.content_object.content, "B")

    def test_update_invalid_parent_course_class_raises(self):
        # create root module in cls
        node = ContentNode.objects.create(
            title="Root",
            course_class=self.cls,
            order=1,
            content_type=ContentType.objects.get_for_model(Module),
            object_id=Module.objects.create(content="A").id,
        )
        # create module in other class, try to set as parent
        other = CourseClass.objects.create(name="C1-B", course=self.course)
        bad_parent = ContentNode.objects.create(
            title="OtherRoot",
            course_class=other,
            order=1,
            content_type=ContentType.objects.get_for_model(Module),
            object_id=Module.objects.create(content="B").id,
        )
        ser = ContentNodeWriteSerializer(
            instance=node, data={"parent": bad_parent.id}, partial=True
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        with self.assertRaises(Exception) as ctx:
            ser.save()
        self.assertIn("Parent node", str(ctx.exception))

    def test_update_node_fields(self):
        # create root module in cls
        node = ContentNode.objects.create(
            title="Root",
            course_class=self.cls,
            order=1,
            content_type=ContentType.objects.get_for_model(Module),
            object_id=Module.objects.create(content="A").id,
        )
        new_course_class = CourseClass.objects.create(name="C1-C", course=self.course)
        payload = {
            "title": "NewTitle",
            "course_class": new_course_class.id,
            "order": 2,
            "content_object_data": {"content": "NewMod"},
        }
        ser = ContentNodeWriteSerializer(instance=node, data=payload, partial=True)
        self.assertTrue(ser.is_valid(), ser.errors)
        node2 = ser.save()
        self.assertEqual(node2.id, node.id)
        self.assertEqual(node2.title, "NewTitle")
        self.assertEqual(node2.course_class_id, new_course_class.id)
        self.assertEqual(node2.order, 2)
        self.assertIsInstance(node2.content_object, Module)
        self.assertEqual(node2.content_object.content, "NewMod")
