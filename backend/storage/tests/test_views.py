from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Folder, File

User = get_user_model()


class UnAuthFileViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("file-list")

    def test_list_nothing(self):
        # Should see nothing regardless of existing files
        File.objects.create(
            owner=User.objects.create_user(email="test@example.com"), name="file1"
        )
        resp = self.client.get(self.url)
        json_data = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json_data["results"], [])
        self.assertEqual(json_data["count"], 0)

    def test_list_public_files(self):
        someone = User.objects.create_user(email="someone@example.com")
        File.objects.create(owner=someone, name="file1")
        File.objects.create(owner=someone, name="file2")
