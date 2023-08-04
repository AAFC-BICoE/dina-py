import requests
import logging


from ..dinaapi import DinaAPI


class PersonAPI(DinaAPI):
    """Class for handling person DINA API requests."""

    def __init__(self, config_path: str = None) -> None:
        """Creates a PersonAPI instance for handling person DINA API requests.

        Parameters:
            config_path (str, optional): Path to a config file (default: None).
        """
        super().__init__(config_path)
        self.base_url += "agent-api/person/"

    # maybe change it to return a Person object and not a response?
    def find(self, uuid: str) -> requests.Response:
        """Returns the GET response of a person with the given UUID.

        Parameters:
            uuid (str): The UUID of the person to find.

        Returns:
            requests.Response: The response object containing the API response.
        """
        full_url = self.base_url + uuid

        try:
            response_data = self.get_req_dina(full_url)
        except Exception as exc:
            logging.error(f"Failed to find person with UUID {uuid}: {exc}")
            raise  # Re-raise the exception

        return response_data
