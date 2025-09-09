from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from config.models import Config


class ConfigModelTestCase(TestCase):
    """Test cases for Config model"""

    def test_create_config_success(self):
        """Test successful config creation"""
        config = Config.objects.create(
            key="test_key",
            value="test_value"
        )

        self.assertEqual(config.key, "test_key")
        self.assertEqual(config.value, "test_value")
        self.assertIsNotNone(config.id)

    def test_config_str_method(self):
        """Test config string representation"""
        config = Config.objects.create(
            key="app_name",
            value="My LMS App"
        )

        self.assertEqual(str(config), "app_name: My LMS App")

    def test_config_key_uniqueness(self):
        """Test that config keys must be unique"""
        Config.objects.create(key="unique_key", value="first_value")

        with self.assertRaises(IntegrityError):
            Config.objects.create(key="unique_key", value="second_value")

    def test_config_key_max_length(self):
        """Test config key maximum length validation"""
        # Valid key (within limit)
        config = Config(key="a" * 255, value="test")
        config.full_clean()  # Should not raise error

        # Invalid key (exceeds limit)
        config = Config(key="a" * 256, value="test")
        with self.assertRaises(ValidationError):
            config.full_clean()

    def test_config_value_can_be_empty(self):
        """Test that config value can be empty"""
        config = Config.objects.create(key="empty_value", value="")
        self.assertEqual(config.value, "")

    def test_config_value_long_text(self):
        """Test config with very long text value"""
        long_value = "A" * 10000  # 10KB of text
        config = Config.objects.create(key="long_text", value=long_value)

        config.refresh_from_db()
        self.assertEqual(config.value, long_value)
        self.assertEqual(len(config.value), 10000)

    def test_config_key_case_sensitivity(self):
        """Test that config keys are case sensitive"""
        Config.objects.create(key="TestKey", value="value1")
        Config.objects.create(key="testkey", value="value2")

        # Both should exist
        self.assertEqual(Config.objects.filter(key="TestKey").count(), 1)
        self.assertEqual(Config.objects.filter(key="testkey").count(), 1)
        self.assertEqual(Config.objects.count(), 2)

    def test_config_update_value(self):
        """Test updating config value"""
        config = Config.objects.create(key="updatable", value="original")

        config.value = "updated"
        config.save()

        config.refresh_from_db()
        self.assertEqual(config.value, "updated")


class ConfigManagerTestCase(TestCase):
    """Test cases for Config manager methods"""

    def setUp(self):
        """Set up test fixtures"""
        Config.objects.create(key="setting1", value="value1")
        Config.objects.create(key="setting2", value="value2")
        Config.objects.create(key="app.debug", value="true")
        Config.objects.create(key="app.version", value="1.0.0")

    def test_get_config_value(self):
        """Test getting config value by key"""
        value = Config.objects.get(key="setting1").value
        self.assertEqual(value, "value1")

    def test_get_config_value_not_found(self):
        """Test getting config value for non-existent key"""
        with self.assertRaises(Config.DoesNotExist):
            Config.objects.get(key="nonexistent")

    def test_filter_by_key_pattern(self):
        """Test filtering configs by key pattern"""
        app_configs = Config.objects.filter(key__startswith="app.")
        self.assertEqual(app_configs.count(), 2)

        debug_configs = Config.objects.filter(key__contains="debug")
        self.assertEqual(debug_configs.count(), 1)

    def test_bulk_config_operations(self):
        """Test bulk operations on configs"""
        # Bulk create
        configs_data = [
            Config(key=f"bulk_key_{i}", value=f"bulk_value_{i}")
            for i in range(5)
        ]
        Config.objects.bulk_create(configs_data)

        self.assertEqual(Config.objects.filter(key__startswith="bulk_key_").count(), 5)

        # Bulk update
        Config.objects.filter(key__startswith="bulk_key_").update(value="updated_bulk_value")

        updated_configs = Config.objects.filter(key__startswith="bulk_key_")
        for config in updated_configs:
            self.assertEqual(config.value, "updated_bulk_value")


class ConfigIntegrationTestCase(TestCase):
    """Integration tests for Config model"""

    def test_config_workflow(self):
        """Test complete config management workflow"""
        # Create configs
        configs = [
            Config(key="database.host", value="localhost"),
            Config(key="database.port", value="5432"),
            Config(key="cache.enabled", value="true"),
            Config(key="cache.ttl", value="3600")
        ]

        Config.objects.bulk_create(configs)
        self.assertEqual(Config.objects.count(), 4)

        # Read configs
        db_host = Config.objects.get(key="database.host")
        self.assertEqual(db_host.value, "localhost")

        # Update configs
        cache_ttl = Config.objects.get(key="cache.ttl")
        cache_ttl.value = "7200"
        cache_ttl.save()

        cache_ttl.refresh_from_db()
        self.assertEqual(cache_ttl.value, "7200")

        # Delete configs
        Config.objects.filter(key__startswith="cache.").delete()
        self.assertEqual(Config.objects.count(), 2)

        remaining_keys = [config.key for config in Config.objects.all()]
        self.assertIn("database.host", remaining_keys)
        self.assertIn("database.port", remaining_keys)

    def test_config_as_settings_store(self):
        """Test using Config as a simple key-value settings store"""
        # Simulate application settings
        settings = {
            "site.name": "My Learning Platform",
            "site.description": "An online learning management system",
            "features.enrollment.enabled": "true",
            "features.grading.enabled": "true",
            "features.certificates.enabled": "false",
            "limits.max_students_per_course": "100",
            "email.smtp.host": "smtp.example.com",
            "email.smtp.port": "587"
        }

        # Create settings
        config_objects = [Config(key=k, value=v) for k, v in settings.items()]
        Config.objects.bulk_create(config_objects)

        # Verify all settings were created
        self.assertEqual(Config.objects.count(), len(settings))

        # Query settings by category
        site_settings = Config.objects.filter(key__startswith="site.")
        self.assertEqual(site_settings.count(), 2)

        feature_settings = Config.objects.filter(key__startswith="features.")
        self.assertEqual(feature_settings.count(), 3)

        email_settings = Config.objects.filter(key__startswith="email.")
        self.assertEqual(email_settings.count(), 2)

        # Get specific setting values
        site_name = Config.objects.get(key="site.name").value
        self.assertEqual(site_name, "My Learning Platform")

        max_students = Config.objects.get(key="limits.max_students_per_course").value
        self.assertEqual(max_students, "100")

        # Update a setting
        cert_enabled = Config.objects.get(key="features.certificates.enabled")
        cert_enabled.value = "true"
        cert_enabled.save()

        cert_enabled.refresh_from_db()
        self.assertEqual(cert_enabled.value, "true")
