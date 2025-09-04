from openfga_sdk.client import ClientConfiguration
from openfga_sdk.credentials import Credentials, CredentialConfiguration
from os import getenv

_OPENFGA_API_URL = getenv("OPENFGA_API_URL")
_OPENFGA_STORE_ID = getenv("OPENFGA_STORE_ID")
# _OPENFGA_MODEL_ID = getenv("OPENFGA_MODEL_ID")
_OPENFGA_API_TOKEN = getenv("OPENFGA_API_TOKEN")

configuration = ClientConfiguration(
    api_url=_OPENFGA_API_URL,
    store_id=_OPENFGA_STORE_ID,
    credentials=Credentials(
        method="api_token",
        configuration=CredentialConfiguration(
            api_token=_OPENFGA_API_TOKEN,
        ),
    ),
)
