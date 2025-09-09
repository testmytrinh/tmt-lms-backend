from django.test import TestCase
from django.contrib.auth.models import Group
from django.db import IntegrityError

from .models import User
from .groups import InitGroup

class UserManagerTestCase(TestCase):
    """Test cases for custom user manager"""

    def test_create_user_success(self):
        """Test successful user creation"""
        email = "test@example.com"
        password = "testpass123"

        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_active)

    def test_create_user_without_email_raises_error(self):
        """Test that creating user without email raises ValueError"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email="", password="testpass123")

        self.assertIn("Users must have an email address", str(context.exception))

    def test_create_user_normalizes_email(self):
        """Test that email is normalized during creation"""
        email = "Test.User@EXAMPLE.COM"
        user = User.objects.create_user(email=email, password="testpass123")

        self.assertEqual(user.email, "Test.User@example.com")

    def test_create_superuser_success(self):
        """Test successful superuser creation"""
        email = "admin@example.com"
        password = "adminpass123"

        user = User.objects.create_superuser(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser_without_staff_raises_error(self):
        """Test that creating superuser without is_staff=True raises ValueError"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                is_staff=False
            )

        self.assertIn("Superuser must have is_staff=True", str(context.exception))

    def test_create_superuser_without_superuser_raises_error(self):
        """Test that creating superuser without is_superuser=True raises ValueError"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                is_superuser=False
            )

        self.assertIn("Superuser must have is_superuser=True", str(context.exception))


class UserModelTestCase(TestCase):
    """Test cases for User model"""

    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'email': 'john.doe@example.com',
            'password': 'securepass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'is_active': True
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_creation(self):
        """Test basic user creation"""
        self.assertEqual(self.user.email, self.user_data['email'])
        self.assertEqual(self.user.first_name, self.user_data['first_name'])
        self.assertEqual(self.user.last_name, self.user_data['last_name'])
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_user_str_representation(self):
        """Test string representation of user"""
        expected = f"{self.user.email}|{self.user.get_full_name()}"
        self.assertEqual(str(self.user), expected)

    def test_user_str_representation_without_names(self):
        """Test string representation when names are empty"""
        user = User.objects.create_user(
            email='noname@example.com',
            password='testpass123'
        )
        expected = f"{user.email}|"
        self.assertEqual(str(user), expected)

    def test_email_uniqueness(self):
        """Test that email field is unique"""
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email=self.user_data['email'],  # Same email
                password='differentpass123'
            )

    def test_username_field_is_email(self):
        """Test that USERNAME_FIELD is set to email"""
        self.assertEqual(User.USERNAME_FIELD, 'email')

    def test_required_fields_empty(self):
        """Test that REQUIRED_FIELDS is empty"""
        self.assertEqual(User.REQUIRED_FIELDS, [])

    def test_user_groups_assignment(self):
        """Test user group assignment"""
        # Create groups
        teacher_group = Group.objects.create(name=InitGroup.TEACHER)
        Group.objects.create(name=InitGroup.STUDENT)

        # Assign user to teacher group
        self.user.groups.add(teacher_group)
        self.assertIn(teacher_group, self.user.groups.all())

        # Check user is in teacher group
        self.assertTrue(self.user.groups.filter(name=InitGroup.TEACHER).exists())

    def test_user_avatar_field(self):
        """Test avatar field functionality"""
        avatar_path = "avatars/user_123.jpg"
        self.user.avatar = avatar_path
        self.user.save()

        self.assertEqual(self.user.avatar, avatar_path)

    def test_user_avatar_field_blank(self):
        """Test avatar field can be blank"""
        self.user.avatar = None
        self.user.save()

        self.assertIsNone(self.user.avatar)


class UserIntegrationTestCase(TestCase):
    """Integration tests for User model with related functionality"""

    def setUp(self):
        """Set up test data"""
        # Create groups
        Group.objects.create(name=InitGroup.TEACHER)
        Group.objects.create(name=InitGroup.STUDENT)

    def test_user_with_groups_creation_workflow(self):
        """Test complete user creation workflow with groups"""
        # Create user
        user = User.objects.create_user(
            email='workflow@example.com',
            password='workflow123',
            first_name='Workflow',
            last_name='Test'
        )

        # Assign to student group
        student_group = Group.objects.get(name=InitGroup.STUDENT)
        user.groups.add(student_group)

        # Verify setup
        self.assertEqual(user.email, 'workflow@example.com')
        self.assertIn(student_group, user.groups.all())
        self.assertTrue(user.groups.filter(name=InitGroup.STUDENT).exists())

    def test_bulk_user_creation(self):
        """Test creating multiple users efficiently"""
        users_data = [
            {'email': f'user{i}@example.com', 'password': f'pass{i}123'}
            for i in range(5)
        ]

        created_users = []
        for user_data in users_data:
            user = User.objects.create_user(**user_data)
            created_users.append(user)

        self.assertEqual(len(created_users), 5)
        self.assertEqual(User.objects.count(), 5)

        # Verify all users have correct properties
        for i, user in enumerate(created_users):
            self.assertEqual(user.email, f'user{i}@example.com')
            self.assertFalse(user.is_active)  # Default value
