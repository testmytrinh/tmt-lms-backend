# from django.test import TestCase
# from django.contrib.auth import get_user_model
# from django.contrib.contenttypes.models import ContentType

# from courses.models import Course, CourseClass
# from courseware.models import ContentNode, Module, Lesson
# from courseware.serializers import ContentNodeWriteSerializer


# User = get_user_model()


# class ContentNodeWriteSerializerTests(TestCase):
#     def setUp(self):
#         self.course = Course.objects.create(name="C1", description="D")
#         self.cls = CourseClass.objects.create(name="C1-A", course=self.course)

#     def test_nested_create_module_node(self):
#         payload = {
#             "title": "Module 1",
#             "course_class": self.cls.id,
#             "order": 1,
#             "content_type": "module",
#             "content_object_data": {"content": "Intro"},
#         }
#         ser = ContentNodeWriteSerializer(data=payload)
#         self.assertTrue(ser.is_valid(), ser.errors)
#         node = ser.save()
#         self.assertIsInstance(node, ContentNode)
#         self.assertEqual(node.title, "Module 1")
#         self.assertEqual(node.course_class_id, self.cls.id)
#         self.assertEqual(node.content_type.model, "module")
#         self.assertIsInstance(node.content_object, Module)
#         self.assertEqual(node.content_object.content, "Intro")

#     def test_link_existing_lesson_under_parent(self):
#         parent_module = Module.objects.create(content="Parent")
#         parent_node = ContentNode.objects.create(
#             title="Parent",
#             course_class=self.cls,
#             order=1,
#             content_type=ContentType.objects.get_for_model(Module),
#             object_id=parent_module.id,
#         )
#         lesson = Lesson.objects.create(content="L1")
#         payload = {
#             "title": "Lesson 1",
#             "course_class": self.cls.id,
#             "parent": parent_node.id,
#             "order": 1,
#             "content_type": "lesson",
#             "object_id": lesson.id,
#         }
#         ser = ContentNodeWriteSerializer(data=payload)
#         self.assertTrue(ser.is_valid(), ser.errors)
#         node = ser.save()
#         self.assertEqual(node.parent_id, parent_node.id)
#         self.assertEqual(node.content_type.model, "lesson")
#         self.assertEqual(node.object_id, lesson.id)

#     def test_update_swaps_content_object(self):
#         # create node with module
#         node = ContentNode.objects.create(
#             title="X",
#             course_class=self.cls,
#             order=1,
#             content_type=ContentType.objects.get_for_model(Module),
#             object_id=Module.objects.create(content="A").id,
#         )
#         payload = {"content_type": "lesson", "content_object_data": {"content": "B"}}
#         ser = ContentNodeWriteSerializer(instance=node, data=payload, partial=True)
#         self.assertTrue(ser.is_valid(), ser.errors)
#         node2 = ser.save()
#         self.assertEqual(node2.id, node.id)
#         self.assertEqual(node2.content_type.model, "lesson")
#         self.assertIsInstance(node2.content_object, Lesson)
#         self.assertEqual(node2.content_object.content, "B")

#     def test_validation_errors(self):
#         # missing content_type
#         ser = ContentNodeWriteSerializer(
#             data={
#                 "title": "Bad",
#                 "course_class": self.cls.id,
#                 "order": 1,
#                 "content_object_data": {"content": "X"},
#             }
#         )
#         self.assertFalse(ser.is_valid())
#         self.assertIn("content_type", ser.errors)

#         # unsupported type
#         ser = ContentNodeWriteSerializer(
#             data={
#                 "title": "Bad",
#                 "course_class": self.cls.id,
#                 "order": 1,
#                 "content_type": "file",
#                 "content_object_data": {"content": "X"},
#             }
#         )
#         self.assertFalse(ser.is_valid())
#         # error will be nested; just ensure validation fails

#         # both id and data provided
#         m = Module.objects.create(content="M")
#         ser = ContentNodeWriteSerializer(
#             data={
#                 "title": "Bad",
#                 "course_class": self.cls.id,
#                 "order": 1,
#                 "content_type": "module",
#                 "object_id": m.id,
#                 "content_object_data": {"content": "X"},
#             }
#         )
#         self.assertFalse(ser.is_valid())

#         # link to non-existent id
#         ser = ContentNodeWriteSerializer(
#             data={
#                 "title": "Bad",
#                 "course_class": self.cls.id,
#                 "order": 1,
#                 "content_type": "lesson",
#                 "object_id": 999999,
#             }
#         )
#         self.assertFalse(ser.is_valid())
#         self.assertIn("object_id", ser.errors)

#     def test_update_invalid_parent_course_class_raises(self):
#         # create root module in cls
#         node = ContentNode.objects.create(
#             title="Root",
#             course_class=self.cls,
#             order=1,
#             content_type=ContentType.objects.get_for_model(Module),
#             object_id=Module.objects.create(content="A").id,
#         )
#         # create module in other class, try to set as parent
#         other = CourseClass.objects.create(name="C1-B", course=self.course)
#         bad_parent = ContentNode.objects.create(
#             title="OtherRoot",
#             course_class=other,
#             order=1,
#             content_type=ContentType.objects.get_for_model(Module),
#             object_id=Module.objects.create(content="B").id,
#         )
#         ser = ContentNodeWriteSerializer(instance=node, data={"parent": bad_parent.id}, partial=True)
#         self.assertTrue(ser.is_valid(), ser.errors)
#         with self.assertRaises(Exception):
#             ser.save()
