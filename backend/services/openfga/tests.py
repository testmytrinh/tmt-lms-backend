from django.test import TestCase
from unittest.mock import Mock

from openfga_sdk.client.models import (
    ClientTuple,
    ClientWriteRequest,
    ClientCheckRequest,
    ClientBatchCheckRequest,
    ClientBatchCheckItem,
)
from openfga_sdk import ReadRequestTupleKey

import services.openfga.sync as fga_sync


class OpenFGAClientSmokeTestCase(TestCase):
    """Smoke tests to assert module-level client usage patterns and shapes."""

    def setUp(self):
        self.mock_sdk_client = Mock()
        # Monkeypatch module-level client used by app code
        fga_sync.client = self.mock_sdk_client

    def test_write_requests(self):
        t1 = ClientTuple(user="user:123", relation="viewer", object="file:456")
        t2 = ClientTuple(user="user:789", relation="editor", object="file:456")
        wr = ClientWriteRequest(writes=[t1, t2])
        dr = ClientWriteRequest(deletes=[t1])

        self.mock_sdk_client.write.return_value = Mock()

        fga_sync.client.write(wr)
        fga_sync.client.write(dr)

        args_w = self.mock_sdk_client.write.call_args_list[0][0][0]
        self.assertIsInstance(args_w, ClientWriteRequest)
        self.assertEqual(args_w.writes, [t1, t2])

        args_d = self.mock_sdk_client.write.call_args_list[1][0][0]
        self.assertIsInstance(args_d, ClientWriteRequest)
        self.assertEqual(args_d.deletes, [t1])

    def test_check_and_read_requests(self):
        cr = ClientCheckRequest(tuple_key={"user": "user:1", "relation": "viewer", "object": "file:1"})
        rr = ReadRequestTupleKey(user="user:1")

        mock_check_resp = Mock(allowed=True)
        self.mock_sdk_client.check.return_value = mock_check_resp
        self.mock_sdk_client.read.return_value = Mock()

        allowed_resp = fga_sync.client.check(cr)
        self.assertTrue(getattr(allowed_resp, "allowed", False))
        args_c = self.mock_sdk_client.check.call_args[0][0]
        self.assertIsInstance(args_c, ClientCheckRequest)

        fga_sync.client.read(rr)
        args_r = self.mock_sdk_client.read.call_args[0][0]
        self.assertIsInstance(args_r, ReadRequestTupleKey)

    def test_batch_check_shape(self):
        # Ensure we can build batch check requests that our views use
        items = [
            ClientBatchCheckItem(body=ClientCheckRequest(tuple_key={
                "user": "user:1", "relation": "teacher", "object": "course_class:1"
            })),
            ClientBatchCheckItem(body=ClientCheckRequest(tuple_key={
                "user": "user:1", "relation": "student", "object": "course_class:1"
            })),
        ]
        br = ClientBatchCheckRequest(items=items)
        fga_sync.client.batch_check(br)
        args_b = self.mock_sdk_client.batch_check.call_args[0][0]
        self.assertIsInstance(args_b, ClientBatchCheckRequest)

