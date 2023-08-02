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
        full_url = self.base_url + "agent-api/person/" + uuid

        try:
            response_data = self.get_req_dina(full_url)
        except Exception as exc:
            # Handle the exception here, e.g., log the error or return a custom error message
            logging.error(f"Failed to find person with UUID {uuid}: {exc}")
            raise  # Re-raise the exception

        return response_data


class Person:
    """Class representing a Person object."""

    def __init__(
        self,
        id,
        type,
        displayName,
        email,
        createdBy,
        createdOn,
        givenNames,
        familyNames,
        webpage,
        remarks,
        aliases,
        organizations,
        identifiers,
    ):
        """Initialize a Person object.

        Parameters:
            id (str): The unique identifier of the person.
            type (str): The type of the person.
            displayName (str): The display name of the person.
            email (str): The email address of the person.
            createdBy (str): The creator of the person.
            createdOn (str): The creation date of the person.
            givenNames (str): The given names of the person.
            familyNames (str): The family names of the person.
            webpage (str): The webpage URL of the person.
            remarks (str): Any remarks or notes about the person.
            aliases (list[str]): List of aliases or alternative names of the person.
            organizations (list[dict]): List of organizations associated with the person.
            identifiers (list[dict]): List of identifiers associated with the person.
        """
        self.id = id
        self.type = type
        self.displayName = displayName
        self.email = email
        self.createdBy = createdBy
        self.createdOn = createdOn
        self.givenNames = givenNames
        self.familyNames = familyNames
        self.webpage = webpage
        self.remarks = remarks
        self.aliases = aliases
        self.organizations = organizations
        self.identifiers = identifiers


# Define the Identifier schema
class IdentifierSchema(Schema):
    id = fields.Str()
    type = fields.Str()


# Define the Organization schema
class OrganizationSchema(Schema):
    id = fields.Str()
    type = fields.Str()


# Define the Person schema
class PersonSchema(Schema):
    # ... (previous fields definition)

    @staticmethod
    def get_attribute(obj, attr):
        return getattr(obj, attr, None)

    id = fields.Str(attribute="id", dump_only=True)
    type = fields.Str(attribute="type", dump_only=True)
    displayName = fields.Str(attribute="displayName")
    email = fields.Str(attribute="email")
    createdBy = fields.Str(attribute="createdBy")
    createdOn = fields.DateTime(attribute="createdOn")
    givenNames = fields.Str(attribute="givenNames")
    familyNames = fields.Str(attribute="familyNames")
    webpage = fields.Str(attribute="webpage")
    remarks = fields.Str(attribute="remarks")
    aliases = fields.List(fields.Str, attribute="aliases")

    organizations = fields.List(
        fields.Nested(OrganizationSchema), attribute="organizations"
    )
    identifiers = fields.List(fields.Nested(IdentifierSchema), attribute="identifiers")

    class Meta:
        type_ = "person"


# Define the top-level schema for the whole JSON structure
class DataSchema(Schema):
    data = fields.Nested(PersonSchema, required=True)
