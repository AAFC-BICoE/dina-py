# This file contains the UploadFileAPI class used for uploading files to the Object Store API.
import logging

from ...dinaapi import DinaAPI

class UploadFileAPI(DinaAPI):
    """
    Class for handling object store uploading related DINA API requests.
    """

    def __init__(self, config_path: str = None, base_url: str = None) -> None:
        """
        Creates a UploadFileAPI instance for handling file uploading DINA Object Store API requests.

        Parameters:
            config_path (str, optional): Path to a config file (default: None).
            base_url (str, optional): URL to the URL to perform the API requests against. If not
                provided then local deployment URL is used. Should end with a forward slash.
        """
        super().__init__(config_path, base_url)
        self.base_url += "objectstore-api/"

    def upload(self, bucket: str, file_path: str ):
        """
        Upload a new file into the object store.

        Parameters:
            bucket (str, required): Namespace of the file described by the metadata
            file_path (str, required): Path to the file to be uploaded.
        """
        full_url = self.base_url + "file/" + bucket

        try:
            response_data = self.post_file_dina(full_url, file_path)
        except Exception as exc:
            logging.error(f"Failed to upload new file to object store: {exc}")
            raise  # Re-raise the exception

        return response_data.json()
    
    def get_file_info(self, bucket: str, file_name: str):
        full_url = self.base_url + "file-info/" + bucket + "/" + file_name
        try:
            response_data = self.get_req_dina(full_url)
        except Exception as exc:
            logging.error(f"Failed to retrieve the file info: {exc}")
            raise  # Re-raise the exception
        
        return response_data.json()