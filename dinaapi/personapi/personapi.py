import requests
import logging


from ..dinaapi import DinaAPI
from ..schemas import PersonSchema


class PersonAPI(DinaAPI):
    """Class for handling person DINA API requests."""

    def __init__(self, config_path: str = None) -> None:
        """Creates a PersonAPI instance for handling person DINA API requests.

        Parameters:
            config_path (str, optional): Path to a config file (default: None).
        """
        super().__init__(config_path)
        self.base_url += "agent-api/person/"

    def find(self, uuid: str) -> dict:
        """Returns the deserialized GET response of a person with the given UUID.

        Parameters:
            uuid (str): The UUID of the person to find.

        Returns:
            dict: A deserialized object of the Person GET response.
        """
        full_url = self.base_url + uuid

        try:
            response_data = self.get_req_dina(full_url)
        except Exception as exc:
            logging.error(f"Failed to find person with UUID {uuid}: {exc}")
            raise  # Re-raise the exception

        person_schema = PersonSchema()
        deserialized_data = person_schema.load(response_data.json())

        return deserialized_data
