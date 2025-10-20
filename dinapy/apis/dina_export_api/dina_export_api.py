"""Defines basic Dina Export API calls"""

import time
from dinapy.dinaapi import DinaAPI

MAX_DATA_EXPORT_FETCH_RETRIES = 6
BASE_DELAY_EXPORT_FETCH_S = 2


class DinaExportApi(DinaAPI):
    def __init__(self, base_url: str = None) -> None:
        super().__init__( base_url)
        self.base_url = (
            base_url + "dina-export-api"
            if base_url
            else self.base_url + "dina-export-api"
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

    def download_object_export(self, object_export_id: str):
        """
        Method to make a request to the dina-export-api/file endpoint to download an Object Export

        data_export_response_json: The response body from the dina-export-api/data-export request
        """
        
        data_export_response = self.get_entity(
            object_export_id, "data-export"
        )

        data_export_response_json = data_export_response.json()
        
        # One of NEW, RUNNING, COMPLETED, EXPIRED, ERROR
        data_export_status = data_export_response_json["data"]["attributes"]["status"]
        fetchDataExportRetries = 0
        while data_export_status != "COMPLETED" and data_export_status != "ERROR":
            if fetchDataExportRetries <= MAX_DATA_EXPORT_FETCH_RETRIES:
                time.sleep(BASE_DELAY_EXPORT_FETCH_S * 2**fetchDataExportRetries)
                object_export_response = self.get_entity(
                    data_export_response_json["data"]["id"], "data-export"
                )
                data_export_response_json = object_export_response.json()
                data_export_status = data_export_response_json["data"]["attributes"][
                    "status"
                ]
                fetchDataExportRetries += 1
            else:
                print(f"Failed to download file. Export status: {data_export_status}")

        if data_export_status == "COMPLETED":
            data_export_name = data_export_response_json["data"]["attributes"]["name"]
            dina_export_download_response = self.get_req_dina(
                f"{self.base_url}/file/{data_export_response_json['data']['id']}",
                {"type": "DATA_EXPORT"},
            )
            if dina_export_download_response.status_code == 200:
                # Open a local file for writing the downloaded content
                with open(f"{data_export_name}.zip", "wb") as file:
                    # Write the response content in chunks
                    for chunk in dina_export_download_response.iter_content(
                        chunk_size=8192
                    ):
                        file.write(chunk)
                    print("File downloaded successfully!")
            else:
                print(
                    f"Failed to download file. Status code: {dina_export_download_response.status_code}"
                )
        else:
            print(
                f"Failed to download file. Status code: {dina_export_download_response.status_code}"
            )
