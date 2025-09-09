from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from institution.models import Institution


class InstitutionModelTestCase(TestCase):
    """Test cases for Institution model"""

    def setUp(self):
        """Set up test fixtures"""
        self.user = get_user_model().objects.create_user(
            email="admin@example.com",
            first_name="Admin",
            last_name="User"
        )

    def test_create_institution_success(self):
        """Test successful institution creation"""
        institution = Institution.objects.create(
            name="Test University",
            description="A test institution",
            website="https://test.edu",
            contact_email="contact@test.edu",
            address="123 Test Street",
            phone="+1234567890",
            created_by=self.user
        )

        self.assertEqual(institution.name, "Test University")
        self.assertEqual(institution.description, "A test institution")
        self.assertEqual(institution.website, "https://test.edu")
        self.assertEqual(institution.contact_email, "contact@test.edu")
        self.assertEqual(institution.address, "123 Test Street")
        self.assertEqual(institution.phone, "+1234567890")
        self.assertEqual(institution.created_by, self.user)
        self.assertIsNotNone(institution.created_at)
        self.assertIsNotNone(institution.updated_at)

    def test_institution_str_method(self):
        """Test institution string representation"""
        institution = Institution.objects.create(
            name="Test University",
            created_by=self.user
        )

        self.assertEqual(str(institution), "Test University")

    def test_institution_name_uniqueness(self):
        """Test that institution names must be unique"""
        Institution.objects.create(
            name="Unique University",
            created_by=self.user
        )

        with self.assertRaises(IntegrityError):
            Institution.objects.create(
                name="Unique University",
                created_by=self.user
            )

    def test_institution_website_validation(self):
        """Test website URL validation"""
        # Valid URLs
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://www.example.com/path",
            "http://subdomain.example.com"
        ]

        for url in valid_urls:
            institution = Institution(
                name=f"Test University {url}",
                website=url,
                created_by=self.user
            )
            # Should not raise validation error
            institution.full_clean()

        # Invalid URLs
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "example.com",  # Missing protocol
            "https://"
        ]

        for url in invalid_urls:
            institution = Institution(
                name=f"Test University {url}",
                website=url,
                created_by=self.user
            )
            with self.assertRaises(ValidationError):
                institution.full_clean()

    def test_institution_email_validation(self):
        """Test contact email validation"""
        # Valid emails
        valid_emails = [
            "contact@example.com",
            "test.email+tag@example.com",
            "user@subdomain.example.com"
        ]

        for email in valid_emails:
            institution = Institution(
                name=f"Test University {email}",
                contact_email=email,
                created_by=self.user
            )
            institution.full_clean()

        # Invalid emails
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "email@",
            "email.example.com"
        ]

        for email in invalid_emails:
            institution = Institution(
                name=f"Test University {email}",
                contact_email=email,
                created_by=self.user
            )
            with self.assertRaises(ValidationError):
                institution.full_clean()

    def test_institution_phone_validation(self):
        """Test phone number validation"""
        # Valid phone numbers
        valid_phones = [
            "+1234567890",
            "+1-234-567-8900",
            "(123) 456-7890",
            "123-456-7890"
        ]

        for phone in valid_phones:
            institution = Institution(
                name=f"Test University {phone}",
                phone=phone,
                created_by=self.user
            )
            institution.full_clean()

    def test_institution_optional_fields(self):
        """Test that description, website, contact_email, address, phone are optional"""
        institution = Institution.objects.create(
            name="Minimal University",
            created_by=self.user
        )

        self.assertEqual(institution.name, "Minimal University")
        self.assertEqual(institution.description, "")
        self.assertEqual(institution.website, "")
        self.assertEqual(institution.contact_email, "")
        self.assertEqual(institution.address, "")
        self.assertEqual(institution.phone, "")

    def test_institution_created_by_required(self):
        """Test that created_by is required"""
        with self.assertRaises(IntegrityError):
            Institution.objects.create(name="Test University")

    def test_institution_auto_timestamps(self):
        """Test automatic timestamp creation and updating"""
        institution = Institution.objects.create(
            name="Timestamp Test University",
            created_by=self.user
        )

        original_created = institution.created_at
        original_updated = institution.updated_at

        # Wait a moment and update
        import time
        time.sleep(0.001)

        institution.description = "Updated description"
        institution.save()

        institution.refresh_from_db()

        self.assertEqual(institution.created_at, original_created)
        self.assertNotEqual(institution.updated_at, original_updated)
        self.assertGreater(institution.updated_at, original_created)


class InstitutionManagerTestCase(TestCase):
    """Test cases for Institution manager methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.user1 = get_user_model().objects.create_user(
            email="admin1@example.com",
            first_name="Admin1",
            last_name="User"
        )
        self.user2 = get_user_model().objects.create_user(
            email="admin2@example.com",
            first_name="Admin2",
            last_name="User"
        )

    def test_get_by_natural_key(self):
        """Test getting institution by natural key (name)"""
        institution = Institution.objects.create(
            name="Natural Key University",
            created_by=self.user1
        )

        retrieved = Institution.objects.get_by_natural_key("Natural Key University")
        self.assertEqual(retrieved, institution)

    def test_get_by_natural_key_not_found(self):
        """Test getting institution by non-existent natural key"""
        with self.assertRaises(Institution.DoesNotExist):
            Institution.objects.get_by_natural_key("Non-existent University")

    def test_filter_by_creator(self):
        """Test filtering institutions by creator"""
        inst1 = Institution.objects.create(
            name="University 1",
            created_by=self.user1
        )
        inst2 = Institution.objects.create(
            name="University 2",
            created_by=self.user1
        )
        inst3 = Institution.objects.create(
            name="University 3",
            created_by=self.user2
        )

        user1_institutions = Institution.objects.filter(created_by=self.user1)
        self.assertEqual(user1_institutions.count(), 2)
        self.assertIn(inst1, user1_institutions)
        self.assertIn(inst2, user1_institutions)

        user2_institutions = Institution.objects.filter(created_by=self.user2)
        self.assertEqual(user2_institutions.count(), 1)
        self.assertIn(inst3, user2_institutions)


class InstitutionIntegrationTestCase(TestCase):
    """Integration tests for Institution model"""

    def setUp(self):
        """Set up test fixtures"""
        self.user = get_user_model().objects.create_user(
            email="admin@example.com",
            first_name="Admin",
            last_name="User"
        )

    def test_complete_institution_workflow(self):
        """Test complete institution creation and management workflow"""
        # Create institution
        institution = Institution.objects.create(
            name="Complete Workflow University",
            description="Testing complete workflow",
            website="https://workflow.test.edu",
            contact_email="contact@workflow.test.edu",
            address="456 Workflow Avenue",
            phone="+1987654321",
            created_by=self.user
        )

        # Verify creation
        self.assertEqual(Institution.objects.count(), 1)

        # Update institution
        institution.description = "Updated description"
        institution.phone = "+1111111111"
        institution.save()

        institution.refresh_from_db()
        self.assertEqual(institution.description, "Updated description")
        self.assertEqual(institution.phone, "+1111111111")

        # Delete institution
        institution.delete()
        self.assertEqual(Institution.objects.count(), 0)

    def test_bulk_institution_creation(self):
        """Test creating multiple institutions efficiently"""
        institutions_data = [
            {
                "name": f"Bulk University {i}",
                "description": f"Description for university {i}",
                "created_by": self.user
            }
            for i in range(10)
        ]

        institutions = [Institution(**data) for data in institutions_data]
        Institution.objects.bulk_create(institutions)

        self.assertEqual(Institution.objects.count(), 10)

        # Verify all institutions were created with correct data
        for i in range(10):
            institution = Institution.objects.get(name=f"Bulk University {i}")
            self.assertEqual(institution.description, f"Description for university {i}")
            self.assertEqual(institution.created_by, self.user)
