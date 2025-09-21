from django.test import TestCase

from ..models import User


class UserCreationTestCase(TestCase):
    def test_create_user_success(self):
        email = "test@example.com"
        password = "testpass123"

        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_active)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")

    def test_create_superuser_success(self):
        email = "admin@example.com"
        password = "adminpass123"

        user = User.objects.create_superuser(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser_without_superuser_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com", password="adminpass123", is_superuser=False
            )
