# This file contains the PersonAPI class used for performing requests on the Person entity.


import logging

from ...dinaapi import DinaAPI
from dinapy.apis.agentapi.schemas.personschema import PersonSchema

class PersonAPI(DinaAPI):
    """Class for handling person DINA API requests."""

    def __init__(self, config_path: str = None, base_url: str = None) -> None:
        """Creates a PersonAPI instance for handling person DINA API requests.

        Parameters:
            config_path (str, optional): Path to a config file (default: None).
            base_url (str, optional): URL to the URL to perform the API requests against. If not
                provided then local deployment URL is used. Should end with a forward slash.
        """
        super().__init__(config_path, base_url)
        self.base_url += "agent-api/person/"

    # TODO: return deserialized object or return response or model (Person object)?
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
    
    # TODO: everything below is untested

    def find_many(self, search_query: str = None, sort_order: str = None, offset: int = None, limit: int = None) -> list:
        """Retrieves a list of persons based on filters, sorting, and paging.

        Parameters:
            search_query (str, optional): Search string for looking up persons (default: None).
            sort_order (str, optional): Sort order string, such as descending ("-") (default: None).
            offset (int, optional): Number of records to skip when paging (default: None).
            limit (int, optional): Maximum number of records to return when paging (default: None).

        Returns:
            list: List of deserialized objects representing persons.
        """
        full_url = self.base_url
        params = {}

        if search_query:
            params['filter[rsql]'] = search_query

        if sort_order:
            params['sort'] = sort_order

        if offset is not None:
            params['page[offset]'] = offset

        if limit is not None:
            params['page[limit]'] = limit

        try:
            response_data = self.get_req_dina(full_url, params=params)
        except Exception as exc:
            logging.error(f"Failed to get persons with filters {params}: {exc}")
            raise  # Re-raise the exception

        persons = response_data['data']
        person_schema = PersonSchema()
        deserialized_persons = [person_schema.load(person) for person in persons]

        return deserialized_persons

    def create(self, json_data: dict) -> dict:
        """Creates a new person by sending a POST request.

        Parameters:
            json_data (dict): JSON data for creating a person.

        Returns:
            dict: A deserialized object of the POST response.
        """
        full_url = self.base_url

        try:
            response_data = self.post_req_dina(full_url, json_data)
        except Exception as exc:
            logging.error(f"Failed to create person: {exc}")
            raise  # Re-raise the exception

        person_schema = PersonSchema()
        deserialized_data = person_schema.load(response_data.json())

        return deserialized_data

    def delete(self, uuid: str) -> None:
        """Deletes a person with the given UUID.

        Parameters:
            uuid (str): The UUID of the person to delete.
        """
        full_url = self.base_url + uuid

        try:
            response_data = self.delete_req_dina(full_url)
        except Exception as exc:
            logging.error(f"Failed to delete person with UUID {uuid}: {exc}")
            raise  # Re-raise the exception

        return response_data

    def update(self, uuid: str, json_data: dict) -> dict:
        """Updates a person with the given UUID using a PATCH request.

        Parameters:
            uuid (str): The UUID of the person to update.
            json_data (dict): JSON data for updating the person.

        Returns:
            dict: A deserialized object of the PATCH response.
        """
        full_url = self.base_url + uuid

        try:
            response_data = self.patch_req_dina(full_url, json_data)
        except Exception as exc:
            logging.error(f"Failed to update person with UUID {uuid}: {exc}")
            raise  # Re-raise the exception

        person_schema = PersonSchema()
        deserialized_data = person_schema.load(response_data.json())

        return deserialized_data