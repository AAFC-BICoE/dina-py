import argparse
import yaml
from dinapy.apis.objectstoreapi.metadata_api import MetadataAPI
from dinapy.apis.objectstoreapi.uploadfileapi import UploadFileAPI
from pathlib import Path

from dinapy.client.utils import get_field_from_config
from dinapy.entities.Metadata import MetadataAttributesDTOBuilder, MetadataDTOBuilder
from dinapy.entities.Relationships import RelationshipDTO
from dinapy.schemas.metadata_schema import MetadataSchema

DINA_API_CONFIG_PATH = "./dina-api-config.yml"
GROUP = ""


class DinaApiClient:
    """
    Class for handling making requests to DINA APIs
    """

    def __init__(self, config_path: str = None, base_url: str = None) -> None:
        self.upload_file_api = UploadFileAPI(config_path, base_url)
        self.metadata_api = MetadataAPI(config_path, base_url)


def create_parser():
    """
    Create command line parser.
    """
    parser = argparse.ArgumentParser(
        prog="Dina API Client", description="A client to make requests to DINA APIs."
    )
    parser.add_argument(
        "-upload_file",
        metavar="<file_path> : (str) = Path to the file to be uploaded.",
        help="Upload a file to Object Store. Argument: file_path",
    )
    parser.add_argument(
        "-upload_dir",
        metavar="<dir_path> : (str) = Path to the directory to be uploaded.",
        help="Upload all files in a directory to Object Store",
    )

    parser.add_argument(
        "-verbose",
        help="Verbosity of logs. Primarily for debugging.",
        action="store_true",
    )
    parser.add_argument(
        "-create_metadatas",
        metavar="<dir_path> : (str) = Path to the directory to be uploaded.",
        help="Upload all files in a directory to Object Store and create metadatas according to constants defined in ./dina-api-config.yml",
    )
    return parser


def upload_file(args: argparse.Namespace, dina_api_client: DinaApiClient, path: Path):
    response_json: dict = dina_api_client.upload_file_api.upload(GROUP, path.as_posix())
    log_response: dict = {
        "originalFilename": response_json.get("originalFilename"),
        "uuid": response_json.get("uuid"),
        "warnings": response_json.get("meta").get("warnings"),
    }
    print(log_response)

    if args.verbose:
        print(response_json)


def create_metadatas(args: argparse.Namespace, dina_api_client: DinaApiClient):
    pathlist = Path(args.create_metadatas).rglob("*.*")
    with open(DINA_API_CONFIG_PATH, "r", encoding="utf-8") as dina_api_config_file:
        dina_api_config = yaml.safe_load(dina_api_config_file)
        for path in pathlist:
            upload_file_response: dict = dina_api_client.upload_file_api.upload(
                GROUP, path.as_posix()
            )

            acMetadataCreator = get_field_from_config(
                dina_api_config,
                "objectstore-api",
                "metadata",
                "relationships",
                "acMetadataCreator",
            )
            dcCreator = get_field_from_config(
                dina_api_config,
                "objectstore-api",
                "metadata",
                "relationships",
                "dcCreator",
            )
            relationships = (
                RelationshipDTO.Builder()
                .add_relationship(
                    "acMetadataCreator",
                    "person",
                    acMetadataCreator.get("data").get("id"),
                )
                .add_relationship(
                    "dcCreator", "person", dcCreator.get("data").get("id")
                )
                .build()
            )

            attributes = (
                dina_api_config.get("objectstore-api").get("metadata").get("attributes")
            )
            attributes["bucket"] = upload_file_response.get("bucket")
            attributes["fileIdentifier"] = upload_file_response.get("uuid")

            dto = (
                MetadataDTOBuilder()
                .set_attributes(attributes)
                .set_relationships(relationships)
                .build()
            )

            schema = MetadataSchema()

            serialized_metadata = schema.dump(dto)

            response = dina_api_client.metadata_api.create_entity(serialized_metadata)
            print(response.json())


def main():
    # Initialize argparse
    parser = create_parser()
    args = parser.parse_args()

    dina_api_client = DinaApiClient()
    with open(DINA_API_CONFIG_PATH, "r", encoding="utf-8") as dina_api_config_file:
        dina_api_config = yaml.safe_load(dina_api_config_file)
        global GROUP
        GROUP = dina_api_config["group"]
    if args.upload_file:
        # Use Path object instead of just str to handle Windows paths and Posix (Unix) paths
        path = Path(args.upload_file)
        upload_file(args, dina_api_client, path)
    elif args.upload_dir:
        # .rglob recognizes file patterns
        pathlist = Path(args.upload_dir).rglob("*.*")
        for path in pathlist:
            upload_file(args, dina_api_client, path)
    elif args.create_metadatas:
        create_metadatas(args, dina_api_client)
    else:
        raise Exception("Incorrect arguments.")


if __name__ == "__main__":
    main()
