from functools import partial
import json
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from courses.models import Course, CourseClass
from courseware.models import ContentNode, Module, Lesson
from courseware.serializers import ContentNodeTreeSerializer

from ..queries import get_root_nodes_by_class_id


class ContentNodeTreeSerializerTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(name="C1", description="D")
        self.course_class = CourseClass.objects.create(name="C1-A", course=self.course)
        self.make_module_node = partial(
            ContentNode.objects.create,
            course_class=self.course_class,
            content_type=ContentType.objects.get_for_model(Module),
        )
        self.make_lesson_node = partial(
            ContentNode.objects.create,
            course_class=self.course_class,
            content_type=ContentType.objects.get_for_model(Lesson),
        )
        return super().setUp()

    def test_level0_tree(self):
        module1 = Module.objects.create(content="Module 1")
        module2 = Module.objects.create(content="Module 2")
        lesson1 = Lesson.objects.create(content="Lesson 1")

        self.make_module_node(title="Node 1", order=1, object_id=module1.id)
        self.make_module_node(title="Node 2", order=2, object_id=module2.id)
        self.make_lesson_node(title="Node 3", order=3, object_id=lesson1.id)
        nodes = get_root_nodes_by_class_id(self.course_class.id).prefetch_related(
            "children"
        )
        ser = ContentNodeTreeSerializer(nodes, many=True)
        self.assertEqual(len(ser.data), 3)
        self.assertEqual(ser.data[0]["title"], "Node 1")
        self.assertEqual(ser.data[1]["title"], "Node 2")
        self.assertEqual(ser.data[2]["title"], "Node 3")
        self.assertEqual(ser.data[0]["children"], [])
        self.assertEqual(ser.data[1]["children"], [])
        self.assertEqual(ser.data[2]["children"], [])

    def test_level1_tree(self):
        module1 = Module.objects.create(content="Module 1")
        lesson1 = Lesson.objects.create(content="Lesson 1")
        lesson2 = Lesson.objects.create(content="Lesson 2")

        parent_node = self.make_module_node(
            title="Module Node", order=1, object_id=module1.id
        )
        self.make_lesson_node(
            title="Lesson Node 1",
            order=1,
            object_id=lesson1.id,
            parent=parent_node,
        )
        self.make_lesson_node(
            title="Lesson Node 2",
            order=2,
            object_id=lesson2.id,
            parent=parent_node,
        )
        nodes = get_root_nodes_by_class_id(self.course_class.id).prefetch_related(
            "children"
        )
        ser = ContentNodeTreeSerializer(nodes, many=True)
        self.assertEqual(len(ser.data), 1)
        self.assertEqual(ser.data[0]["title"], "Module Node")
        self.assertEqual(len(ser.data[0]["children"]), 2)
        self.assertEqual(ser.data[0]["children"][0]["title"], "Lesson Node 1")
        self.assertEqual(ser.data[0]["children"][1]["title"], "Lesson Node 2")

    def test_level2_tree(self):
        module1 = Module.objects.create(content="Module 1")
        module11 = Module.objects.create(content="Module 1.1")
        lesson111 = Lesson.objects.create(content="Lesson 1.1.1")
        lesson112 = Lesson.objects.create(content="Lesson 1.1.2")
        lesson12 = Lesson.objects.create(content="Lesson 1.2")

        parent_node = self.make_module_node(
            title="Module Node", order=1, object_id=module1.id
        )
        child_node = self.make_module_node(
            title="Module Node 1.1",
            order=1,
            object_id=module11.id,
            parent=parent_node,
        )
        self.make_lesson_node(
            title="Lesson Node 1.1.1",
            order=1,
            object_id=lesson111.id,
            parent=child_node,
        )
        self.make_lesson_node(
            title="Lesson Node 1.1.2",
            order=2,
            object_id=lesson112.id,
            parent=child_node,
        )
        self.make_lesson_node(
            title="Lesson Node 1.2",
            order=2,
            object_id=lesson12.id,
            parent=parent_node,
        )
        nodes = get_root_nodes_by_class_id(self.course_class.id).prefetch_related(
            "children__children"
        )
        ser = ContentNodeTreeSerializer(nodes, many=True)
        self.assertEqual(len(ser.data), 1)
        self.assertEqual(len(ser.data[0]["children"]), 2)
        self.assertEqual(len(ser.data[0]["children"][0]["children"]), 2)
