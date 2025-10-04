from django.test.runner import DiscoverRunner
from django.utils import timezone
from django.conf import settings

from services.s3 import s3_client
from services.openfga.sync import client, clone_store


def cleanup_s3_folder(prefix):
    bucket = s3_client.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    bucket.objects.filter(Prefix=prefix).delete()


class MyCustomTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        print("Setting up test environment with a fresh OpenFGA store...\n\n")
        test_store_name = f"test_store{timezone.now().strftime('%d%m%Y-%H%M%S')}"
        new_store_id = clone_store(test_store_name)
        client.set_store_id(new_store_id)
        settings.AWS_LOCATION = "test"
        return super().setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs):
        print("Tearing down test environment and deleting test OpenFGA store...\n\n")
        client.delete_store()
        print("Deleted test OpenFGA store.\n\n")
        cleanup_s3_folder("test/")
        print("Cleaned up S3 test folder.\n\n")

        return super().teardown_test_environment(**kwargs)
