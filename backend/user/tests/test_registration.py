from rest_framework.test import APITestCase, APIClient
from django.urls import reverse

from ..models import User


class UserRegistrationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.request_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        # cuz list and create use the same endpoint
        self.url = reverse("user-list")

    def test_register_user_success(self):
        response = self.client.post(self.url, data=self.request_data)
        self.assertEqual(response.status_code, 201)

        user = User.objects.get(email=self.request_data["email"])
        self.assertEqual(user.first_name, self.request_data["first_name"])
        self.assertEqual(user.last_name, self.request_data["last_name"])
        self.assertFalse(user.is_active)  # Default value

    def test_register_user_duplicate_email_fails(self):
        User.objects.create_user(
            email=self.request_data["email"], password="anotherpass123"
        )

        response = self.client.post(self.url, data=self.request_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json())


class UserAccActivationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", is_active=False
        )
        self.build_activate_url = lambda token: reverse(
            "user-activate", kwargs={"token": token}
        )

    def test_activate_user_success(self):
        token = self.user.generate_activation_token()
        url = self.build_activate_url(token)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activate_user_invalid_token_fails(self):
        url = self.build_activate_url("kkkkk")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
