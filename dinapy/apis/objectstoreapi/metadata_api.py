"""Class that extracts common functionality for collecting event entity"""

from datetime import datetime
import os

from requests import HTTPError
from dinapy.apis.objectstoreapi.uploadfileapi import UploadFileAPI
from dinapy.entities.Metadata import MetadataDTOBuilder
from dinapy.entities.Relationships import RelationshipDTO
from dinapy.schemas.metadata_schema import MetadataSchema
from .objectstore_module_api import ObjectStoreModuleApi


class MetadataAPI(ObjectStoreModuleApi):
    def __init__(self, config_path: str = None, base_url: str = None) -> None:
        super().__init__(config_path, base_url)
        self.base_url += "metadata"

    def create_metadatas(self, upload_file_api: UploadFileAPI, pathlist, dina_api_config, group):
        """
		Upload a file to objectstore-api/file/bucket, then make a POST request to objecstore-api/metadata to create Metadata.

		dina_api_client: instantiated DinaApiClient object

		pathlist: Generator[Path, None, None] list of object paths to be uploaded

		dina_api_config: dict of loaded dina-api-config.yml

		group: group provided in dina-api-config.yml
		"""
  
        for path in pathlist:
            upload_file_response: dict = upload_file_api.upload(
                group, path.as_posix()
            )

            acMetadataCreator = self.get_field_from_config(
                dina_api_config,
                "objectstore-api",
                "metadata",
                "relationships",
                "acMetadataCreator",
            )
            dcCreator = self.get_field_from_config(
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
                .add_relationship("dcCreator", "person", dcCreator.get("data").get("id"))
                .build()
            )

            # Get the creation time as a float
            acDigitizationDate = os.path.getctime(path)

            # Naive datetime object
            naiveAcDigitizationDate = datetime.fromtimestamp(acDigitizationDate)

            # Convert to local time with timezone info
            localizedAcDigitizationDate = naiveAcDigitizationDate.astimezone()

            attributes = (
                dina_api_config.get("objectstore-api").get("metadata").get("attributes")
            )
            attributes["bucket"] = upload_file_response.get("bucket")
            attributes["fileIdentifier"] = upload_file_response.get("uuid")
            attributes["acDigitizationDate"] = localizedAcDigitizationDate

            dto = (
                MetadataDTOBuilder()
                .set_attributes(attributes)
                .set_relationships(relationships)
                .build()
            )

            schema = MetadataSchema()

            serialized_metadata = schema.dump(dto)

            try:
                response = self.create_entity(serialized_metadata)
                print(response.json())
            except HTTPError as e:
                print(e.response.json())
                print(serialized_metadata)

    def get_field_from_config(
        self, dina_api_config: dict, api: str, resource: str, property: str, field: str
    ):
        """
        dina_api_config: Parsed dictionary of constants from yml

        api: API field in dina_api_config. Ex: objectstore-api

        resource: Type of resource from API. Ex: metadata

        property: Property of resource. One of: relationships, attributes

        field: Field of resource. Ex: acMetadataCreator
        """
        return dina_api_config.get(api).get(resource).get(property).get(field)
