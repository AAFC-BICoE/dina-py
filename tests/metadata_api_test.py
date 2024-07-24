import sys
import os
from pathlib import Path
import yaml

from dinapy.client.dina_api_client import DinaApiClient
from dinapy.entities.Metadata import (
    MetadataAttributesDTO,
    MetadataAttributesDTOBuilder,
    MetadataDTO,
    MetadataDTOBuilder,
)

from dinapy.schemas.metadata_schema import MetadataSchema
from dinapy.utils import get_dina_records_by_field

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# TODO: Convert this into proper unit test.
os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

DINA_API_CONFIG_TEST_PATH = "./tests/resources/dina-api-config-test.yml"
OBJECT_UPLOAD_PATH = "./tests/resources/object-upload-test"
TEST_GROUP = ""


def main():
    dina_api_client = DinaApiClient()
    pathlist = Path(OBJECT_UPLOAD_PATH).rglob("*.*")
    with open(DINA_API_CONFIG_TEST_PATH, "r", encoding="utf-8") as dina_api_config_file:
        dina_api_config = yaml.safe_load(dina_api_config_file)
        TEST_GROUP = dina_api_config["group"]
        for path in pathlist:
            response_json: dict = dina_api_client.upload_file_api.upload(
                TEST_GROUP, path.as_posix()
            )

            metadata_attributes_config = dina_api_config["objectstore-api"]["metadata"][
                "attributes"
            ]
            metadata_attributes_config["fileIdentifier"] = response_json.get("uuid")
            metadata_attributes_config["bucket"] = TEST_GROUP
            metadata_dto = (
                MetadataDTOBuilder()
                .attributes(metadata_attributes_config)
                .build()
            )
            metadata_schema = MetadataSchema()
            serialized_metadata = metadata_schema.dump(metadata_dto)
            serialized_metadata["data"]["relationships"] = dina_api_config["objectstore-api"][
                "metadata"
            ]["relationships"]
            response = dina_api_client.metadata_api.create_entity(serialized_metadata)
            print(response.json())


if __name__ == "__main__":
    main()
