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
    pathlist = Path(OBJECT_UPLOAD_PATH).rglob("*.*")
    with open(DINA_API_CONFIG_TEST_PATH, "r", encoding="utf-8") as dina_api_config_file:
        dina_api_config: dict = yaml.safe_load(dina_api_config_file)
        group = dina_api_config["group"]
        object_export_payload = {
            "data": {
                "type": "object-export",
                "attributes": {
                    "fileIdentifiers": [
                        "01924e50-a569-7015-972e-2dea18b0da44",
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
