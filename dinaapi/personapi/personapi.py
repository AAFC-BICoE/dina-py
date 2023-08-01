import requests
from ..dinaapi import DinaAPI


class PersonAPI(DinaAPI):
    def __init__(self, config_path: str = None) -> None:
        """Creates a PersonAPI instance for handling person DINA API requests.
        Takes an optional path to a config_path"""

        super.__init__(config_path)
        self.base_url += "agent-api/person/"

    def find(self, uuid: str) -> requests.Response:
        """Returns the GET response of a person with the given UUID."""
        full_url = self.base_url + uuid

        return self.get_req_dina(full_url)
