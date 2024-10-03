import argparse
import yaml
import os
import sys
from dinapy.apis.dina_export_api.dina_export_api import DinaExportApi
from dinapy.apis.objectstoreapi.objectstore_api import ObjectStoreApi
from dinapy.apis.collectionapi.formtemplateapi import FormTemplateAPI
from dinapy.apis.collectionapi.splitconfigurationapi import SplitConfigurationAPI
from pathlib import Path
from dinapy.entities.FormTemplate import (
    FormTemplateAttributesDTOBuilder,
    FormTemplateDTOBuilder,
)
from dinapy.entities.SplitConfiguration import (
    SplitConfigurationAttributesDTOBuilder,
    SplitConfigurationDTOBuilder,
)
from dinapy.schemas.splitconfigurationschema import SplitConfigurationSchema
from dinapy.schemas.formtemplateschema import FormTemplateSchema

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


DINA_API_CONFIG_PATH = "./dina-api-config.yml"


class DinaApiClient:
    """
    Class for handling making requests to DINA APIs
    """

    def __init__(self, config_path: str = None, base_url: str = None) -> None:
        self.objectstore_module_api = ObjectStoreApi(config_path, base_url)
        self.form_template_api = FormTemplateAPI(config_path, base_url)
        self.split_configuration_api = SplitConfigurationAPI(config_path, base_url)
        self.dina_export_api = DinaExportApi(config_path, base_url)


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
    parser.add_argument(
        "-create_form_template",
        metavar="<file_path> : (str) = Path to the file to be parsed and created.",
        help="Create a form template according to specs defined in a yaml file such as ./form-template-sample.yml",
    )
    parser.add_argument(
        "-create_split_configuration",
        metavar="<file_path> : (str) = Path to the file to be parsed and created.",
        help="Create a split configuration according to specs defined in a yaml file such as ./split-configuration-sample.yml",
    )
    return parser


def upload_file(
    args: argparse.Namespace, dina_api_client: DinaApiClient, path: Path, group
):
    response_json: dict = dina_api_client.objectstore_module_api.upload(group, path.as_posix())
    log_response: dict = {
        "originalFilename": response_json.get("originalFilename"),
        "uuid": response_json.get("uuid"),
        "warnings": response_json.get("meta").get("warnings"),
    }
    print(log_response)

    if args.verbose:
        print(response_json)


def create_split_configuration(dina_api_client: DinaApiClient, path: Path):
    split_configuration_config_path = path.as_posix()
    with open(
        split_configuration_config_path, "r", encoding="utf-8"
    ) as split_configuration_config_file:
        split_configuration_config = yaml.safe_load(split_configuration_config_file)
        split_configuration_attributes = split_configuration_config["attributes"]
        split_configuration_attributes_dto = (
            SplitConfigurationAttributesDTOBuilder()
            .set_strategy(split_configuration_attributes["strategy"])
            .set_conditionalOnMaterialSampleTypes(
                split_configuration_attributes["conditionalOnMaterialSampleTypes"]
            )
            .set_characterType(split_configuration_attributes["characterType"])
            .set_group(split_configuration_attributes["group"])
            .set_separator(split_configuration_attributes["separator"])
            .set_name(split_configuration_attributes["name"])
            .set_materialSampleTypeCreatedBySplit(
                split_configuration_attributes["materialSampleTypeCreatedBySplit"]
            )
            .build()
        )
        split_configuration_dto = (
            SplitConfigurationDTOBuilder()
            .set_attributes(split_configuration_attributes_dto)
            .build()
        )

        schema = SplitConfigurationSchema()

        serialized_split_configuration = schema.dump(split_configuration_dto)
        response = dina_api_client.split_configuration_api.create_entity(
            serialized_split_configuration
        )
        print(response.json())


def create_form_template(dina_api_client: DinaApiClient, path: Path):
    form_template_config_path = path.as_posix()
    with open(
        form_template_config_path, "r", encoding="utf-8"
    ) as form_template_config_file:
        form_template_config = yaml.safe_load(form_template_config_file)
        form_template_attributes = form_template_config["attributes"]
        form_template_attributes_dto = (
            FormTemplateAttributesDTOBuilder()
            .set_components(form_template_attributes["components"])
            .set_viewConfiguration(form_template_attributes["viewConfiguration"])
            .set_restrictToCreatedBy(form_template_attributes["restrictToCreatedBy"])
            .set_group(form_template_attributes["group"])
            .set_name(form_template_attributes["name"])
            .build()
        )
        form_template_dto = (
            FormTemplateDTOBuilder()
            .set_attributes(form_template_attributes_dto)
            .build()
        )

        schema = FormTemplateSchema()

        serialized_form_template = schema.dump(form_template_dto)
        response = dina_api_client.form_template_api.create_entity(
            serialized_form_template
        )
        print(response.json())


def main():
    # Initialize argparse
    parser = create_parser()
    args = parser.parse_args()
    print(args)
    dina_api_client = DinaApiClient()
    with open(DINA_API_CONFIG_PATH, "r", encoding="utf-8") as dina_api_config_file:
        dina_api_config = yaml.safe_load(dina_api_config_file)
        group = dina_api_config["group"]
    if args.upload_file:
        # Use Path object instead of just str to handle Windows paths and Posix (Unix) paths
        path = Path(args.upload_file)
        upload_file(args, dina_api_client, path, group)
    elif args.upload_dir:
        # .rglob recognizes file patterns
        pathlist = Path(args.upload_dir).rglob("*.*")
        for path in pathlist:
            upload_file(args, dina_api_client, path)
    elif args.create_metadatas:
        pathlist = Path(args.create_metadatas).rglob("*.*")
        dina_api_client.objectstore_module_api.create_metadatas(pathlist, dina_api_config, group)
    elif args.create_form_template:
        path = Path(args.create_form_template)
        create_form_template(dina_api_client, path)
    elif args.create_split_configuration:
        path = Path(args.create_split_configuration)
        create_split_configuration(dina_api_client, path)
    else:
        raise Exception("Incorrect arguments.")


if __name__ == "__main__":
    main()
