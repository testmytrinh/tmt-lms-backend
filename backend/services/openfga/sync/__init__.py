from openfga_sdk.sync import OpenFgaClient
from openfga_sdk import CreateStoreRequest, WriteAuthorizationModelRequest


from ..settings import configuration

client = OpenFgaClient(configuration)


def clone_store(name: str) -> str:
    auth_model = client.read_latest_authorization_model().authorization_model
    _old_store_id = client.get_store_id()
    new_store_id = client.create_store(CreateStoreRequest(name=name)).id
    client.set_store_id(new_store_id)
    client.write_authorization_model(
        WriteAuthorizationModelRequest(
            schema_version=auth_model.schema_version,
            type_definitions=auth_model.type_definitions,
            conditions=auth_model.conditions,
        )
    )
    client.set_store_id(_old_store_id)
    return new_store_id
