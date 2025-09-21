from django.test.runner import DiscoverRunner
from django.utils import timezone

from services.openfga.sync import client, clone_store


class MyCustomTestRunner(DiscoverRunner):
    def teardown_test_environment(self, **kwargs):
        print("Tearing down test environment and deleting test OpenFGA store...\n\n")
        client.delete_store()
        print("Deleted test OpenFGA store.\n\n")
        return super().teardown_test_environment(**kwargs)

    def setup_test_environment(self, **kwargs):
        print("Setting up test environment with a fresh OpenFGA store...\n\n")
        test_store_name = f"test_store{timezone.now().strftime('%d%m%Y-%H%M%S')}"
        new_store_id = clone_store(test_store_name)
        client.set_store_id(new_store_id)
        return super().setup_test_environment(**kwargs)
