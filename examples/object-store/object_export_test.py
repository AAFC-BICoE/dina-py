import sys
import os
from pathlib import Path
import yaml

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.client.dina_api_client import DinaApiClient

os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

DINA_API_CONFIG_TEST_PATH = "./tests/resources/dina-api-config-test.yml"
OBJECT_UPLOAD_PATH = "./tests/resources/object-upload-test"


def main():
    dina_api_client = DinaApiClient()
    metadatas_response = dina_api_client.objectstore_module_api.get_entity_by_param(
        {
            "filter[originalFilename]": "object_upload - Copy.png",
        },
        "metadata",
    )
    metadatas_response_json = metadatas_response.json()

    # "01924e45-e991-7800-bce5-c449d05dd18d"
    metadata_fileIdentifier = metadatas_response_json["data"][0]["attributes"][
        "fileIdentifier"
    ]

    object_export_payload = {
        "data": {
            "type": "object-export",
            "attributes": {
                "fileIdentifiers": [
                    metadata_fileIdentifier,
                ],
                "name": "dina-py export",
            },
        }
    }
    response = dina_api_client.objectstore_module_api.create_entity(
        object_export_payload, "object-export"
    )
    response_json = response.json()

    print(response_json)


if __name__ == "__main__":
    main()
