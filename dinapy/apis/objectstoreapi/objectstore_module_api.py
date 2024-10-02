"""Defines basic Object Store Module API calls"""

import logging
from dinapy.dinaapi import DinaAPI
from dinapy.entities.Relationships import RelationshipDTO
from datetime import datetime
import os

from requests import HTTPError
from dinapy.entities.Metadata import MetadataDTOBuilder
from dinapy.schemas.metadata_schema import MetadataSchema

class ObjectStoreModuleApi(DinaAPI):
    def __init__(self, config_path: str = None, base_url: str = None) -> None:
        super().__init__(config_path, base_url)
        self.base_url = (
            base_url + "objectstore-api"
            if base_url
            else self.base_url + "objectstore-api"
        )

    def get_entity(self, entity_id, endpoint: str):
        """Retrieves an entity

        Args:
                entity_id (string): entity id

        Returns:
                json response: 'result' from the json response OR nothing if entity was not found
        """
        entity_id = str(entity_id) if isinstance(entity_id, int) else entity_id
        new_request_url = f"{self.base_url}/{endpoint}/{str(entity_id)}"
        jsn_resp = self.get_req_dina(new_request_url)
        return jsn_resp if jsn_resp else ""

    def create_entity(self, json_data, endpoint: str):
        """Creates a DINA Object Store module entity

        Args:
                json_data (json object): the request body

        Returns:
                Response: The response post request
        """
        return self.post_req_dina(f"{self.base_url}/{endpoint}", json_data)

    def get_entity_by_param(self, param, endpoint: str):
        jsn_resp = self.get_req_dina(f"{self.base_url}/{endpoint}", param)
        return jsn_resp if jsn_resp else ""

    def get_entity_by_field(self, field, value, endpoint: str):
        """Get an entity by it's name

        Args:
                value (string): value of the entity

        Returns:
                json response: a list of found entities with that value for that field
        """
        new_params = {"filter[rsql]": "{}=='{}'".format(field, value)}
        return self.get_entity_by_param(new_params, endpoint)

    def remove_entity(self, entity_id, endpoint: str):
        entity_id = str(entity_id) if isinstance(entity_id, int) else entity_id
        new_request_url = f"{self.base_url}/{endpoint}/{str(entity_id)}"
        jsn_resp = self.delete_req_dina(new_request_url)
        return jsn_resp if jsn_resp else ""

    def update_entity(self, entity_id, json_data, endpoint: str):
        """Updates an entity

        Args:
                entity_id (string): entity id

        Returns:
                json response: 'result' from the json response OR nothing if entity was not found
        """

        entity_id = str(entity_id) if isinstance(entity_id, int) else entity_id
        new_request_url = f"{self.base_url}/{endpoint}/{str(entity_id)}"
        jsn_resp = self.patch_req_dina(new_request_url, json_data)
        return jsn_resp if jsn_resp else ""

    def upload(self, bucket: str, file_path: str):
        """
        Upload a new file into the object store.

        Parameters:
            bucket (str, required): Namespace of the file described by the metadata
            file_path (str, required): Path to the file to be uploaded.
        """
        full_url = f"{self.base_url}/file/{bucket}"

        try:
            response_data = self.post_file_dina(full_url, file_path)
        except Exception as exc:
            logging.error(f"Failed to upload new file to object store: {exc}")
            raise  # Re-raise the exception

        return response_data.json()

    def get_file_info(self, bucket: str, file_name: str):
        full_url = f"{self.base_url}/file-info/{bucket}/{file_name}"
        try:
            response_data = self.get_req_dina(full_url)
        except Exception as exc:
            logging.error(f"Failed to retrieve the file info: {exc}")
            raise  # Re-raise the exception

        return response_data.json()

    def create_metadatas(self, pathlist, dina_api_config, group):
        """
        Upload a file to objectstore-api/file/bucket, then make a POST request to objecstore-api/metadata to create Metadata.

        dina_api_client: instantiated DinaApiClient object

        pathlist: Generator[Path, None, None] list of object paths to be uploaded

        dina_api_config: dict of loaded dina-api-config.yml

        group: group provided in dina-api-config.yml
        """

        for path in pathlist:
            upload_file_response: dict = self.upload(group, path.as_posix())

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
                .add_relationship(
                    "dcCreator", "person", dcCreator.get("data").get("id")
                )
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
                response = self.create_entity(serialized_metadata, "metadata")
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
