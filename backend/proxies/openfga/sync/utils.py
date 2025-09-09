from openfga_sdk import ReadRequestTupleKey
from openfga_sdk.client.models import (
    ClientWriteRequest,
    ClientTuple,
)

from . import client


def flush_all_tuples():
    read_response = client.read(ReadRequestTupleKey())
    todelete_tuples = []

    for tuple_obj in read_response.tuples:
        key = tuple_obj.key
        todelete_tuples.append(
            ClientTuple(user=key.user, relation=key.relation, object=key.object)
        )

    if todelete_tuples:
        delete_request = ClientWriteRequest(deletes=todelete_tuples)
        return client.write(delete_request)
    return