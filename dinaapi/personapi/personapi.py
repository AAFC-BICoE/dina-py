import requests
import logging

from marshmallow_jsonapi import Schema, fields

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


class IdentifierSchema(Schema):
    class Meta:
        type_ = "identifier"

    id = fields.Str(required=True)

class OrganizationSchema(Schema):
    class Meta:
        type_ = "organization"

    id = fields.Str(required=True)

class PersonSchema(Schema):
    class Meta:
        type_ = "person"
        self_view = "/api/v1/person/{id}"
        # self_view_many = "person_list"

    id = fields.Str(required=True)
    displayName = fields.Str(required=True, attribute="displayName")
    email = fields.Email(required=True, attribute="email")
    createdBy = fields.Str(required=True, attribute="createdBy")
    createdOn = fields.DateTime(required=True, attribute="createdOn")
    givenNames = fields.Str(required=True, attribute="givenNames")
    familyNames = fields.Str(required=True, attribute="familyNames")
    webpage = fields.Url(required=True, attribute="webpage")
    remarks = fields.Str(required=True, attribute="remarks")
    aliases = fields.List(fields.Str(), required=True, attribute="aliases")

    # Define relationships using .nested
    organizations = fields.Relationship(
        type_="organization", attribute="organizations", many=True, include_resource_linkage=True, nested="OrganizationSchema"
    )
    identifiers = fields.Relationship(
        type_="identifier", attribute="identifiers", many=True, include_resource_linkage=True, nested="IdentifierSchema"
    )