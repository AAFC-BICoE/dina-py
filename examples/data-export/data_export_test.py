import sys
import os

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
    
    # Get metadata record by uuid
    # metadatas_response = dina_api_client.objectstore_module_api.get_entity("01924e45-ec28-7e52-a85a-da93864d94f1")
    
    # Get metadata records by simple filters
    metadatas_response = dina_api_client.objectstore_module_api.get_entity_by_param(
        {
            "filter[originalFilename]": "object_upload - Copy.png",
        },
        "metadata",
    )
    metadatas_response_json = metadatas_response.json()

    metadata_fileIdentifier = metadatas_response_json["data"][0]["attributes"][
        "fileIdentifier"
    ]

    # Create an object export request
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
    post_object_export_response = dina_api_client.objectstore_module_api.create_entity(
        object_export_payload, "object-export"
    )

    post_object_export_response_json = post_object_export_response.json()

    # Download an export
    dina_api_client.dina_export_api.download_object_export(post_object_export_response_json["data"]["id"])

if __name__ == "__main__":
    main()
