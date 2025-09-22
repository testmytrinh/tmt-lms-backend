from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from enrollment.models import Enrollment, EnrollmentRole
from courses.models import Course, CourseClass

from ..models import ContentNode

User = get_user_model()


class ContentNodeViewTests(APITestCase):
    def setUp(self):
        # user and auth
        self.user = User.objects.create_user(
            email="u@example.com", password="pass123", is_active=True
        )
        self.client.force_authenticate(self.user)

        # course and classes
        self.course = Course.objects.create(name="C1", description="D")
        self.cls = CourseClass.objects.create(name="C1-A", course=self.course)
        # teacher role to allow create/edit
        Enrollment.objects.create(
            user=self.user, course_class=self.cls, role=EnrollmentRole.TEACHER
        )

        self.list_url = reverse("content-node-list", args=[self.cls.id])
        self.tree_url = reverse("content-node-tree", args=[self.cls.id])

    def tearDown(self):
        self.client.force_authenticate(None)

    def test_list_and_tree_empty(self):
        # list
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["results"], [])

        # tree
        resp = self.client.get(self.tree_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

    def test_create_module_node(self):
        payload = {
            "title": "Module 1",
            "course_class": self.cls.id,
            "order": 1,
            "content_type": "module",
            "content_object_data": {"content": "Intro"},
        }
        resp = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        data = resp.json()
        self.assertEqual(data["title"], "Module 1")
        self.assertEqual(data["content_type"], "module")
        self.assertIn("content_object", data)
        self.assertEqual(data["content_object"]["content"], "Intro")

    def test_link_lesson_under_module_and_tree(self):
        # create parent module node
        mod_payload = {
            "title": "Module 1",
            "course_class": self.cls.id,
            "order": 1,
            "content_type": "module",
            "content_object_data": {"content": "Intro"},
        }
        mod_resp = self.client.post(self.list_url, mod_payload, format="json")
        self.assertEqual(mod_resp.status_code, 201)
        parent_id = mod_resp.json()["id"]

        # create a lesson node under the module
        lesson_payload = {
            "title": "Lesson 1",
            "course_class": self.cls.id,
            "parent": parent_id,
            "order": 1,
            "content_type": "lesson",
            "content_object_data": {"content": "L1"},
        }
        resp = self.client.post(self.list_url, lesson_payload, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)

        # list
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 2)

        # tree should show parent with a child
        resp = self.client.get(self.tree_url)
        self.assertEqual(resp.status_code, 200)
        tree = resp.json()
        self.assertEqual(len(tree), 1)
        self.assertEqual(len(tree[0]["children"]), 1)
        self.assertEqual(tree[0]["children"][0]["title"], "Lesson 1")

    def test_update_content_and_delete(self):
        # create module node
        mod_payload = {
            "title": "Module 1",
            "course_class": self.cls.id,
            "order": 1,
            "content_type": "module",
            "content_object_data": {"content": "Intro"},
        }
        mod_resp = self.client.post(self.list_url, mod_payload, format="json")
        self.assertEqual(mod_resp.status_code, 201)
        node_id = mod_resp.json()["id"]

        # update: modify module content (same content_type)
        patch_payload = {
            "content_type": "module",
            "content_object_data": {"content": "Intro 2"},
        }
        resp = self.client.patch(
            self.list_url + f"{node_id}/", patch_payload, format="json"
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        data = resp.json()
        self.assertEqual(data["content_type"], "module")
        self.assertIn("content_object", data)
        self.assertEqual(data["content_object"]["content"], "Intro 2")

        # delete
        resp = self.client.delete(self.list_url + f"{node_id}/")
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(ContentNode.objects.filter(id=node_id).exists())

    def test_create_node_not_enrolled_forbidden(self):
        new_class = CourseClass.objects.create(name="C2", course=self.course)
        payload = {
            "title": "Module 1",
            "course_class": new_class.id,
            "order": 1,
            "content_type": "module",
            "content_object_data": {"content": "Intro"},
        }
        url = reverse("content-node-list", args=[new_class.id])
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_create_node_enrolled_as_student_forbidden(self):
        new_class = CourseClass.objects.create(name="C2", course=self.course)
        Enrollment.objects.create(
            user=self.user, course_class=new_class, role=EnrollmentRole.STUDENT
        )
        payload = {
            "title": "Module 1",
            "course_class": new_class.id,
            "order": 1,
            "content_type": "module",
            "content_object_data": {"content": "Intro"},
        }
        url = reverse("content-node-list", args=[new_class.id])
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 403)
