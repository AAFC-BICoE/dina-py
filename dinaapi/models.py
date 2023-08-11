# This file contains models for representing objects and entities from Dina.
# Not currently being used by any other file, however should think about returning these objects instead of a dict
# when performing requests.


class Person:
    """
    Represents an individual person's information.

    Attributes:
        id (str): The unique identifier of the person.
        displayName (str): The display name of the person.
        email (str): The email address of the person.
        createdBy (str): The user who created the person.
        createdOn (datetime): The timestamp when the person was created.
        givenNames (str): The given (first) names of the person.
        familyNames (str): The family (last) names of the person.
        aliases (list of str): Alternate names or aliases for the person.
        webpage (str, optional): The webpage associated with the person (if available).
        remarks (str, optional): Additional remarks or notes about the person.
        identifiers (list of Identifier): List of identifiers associated with the person.
        organizations (list of Organization): List of organizations associated with the person.
    """
    def __init__(self, id, displayName, email, createdBy, createdOn, givenNames, familyNames,
                 aliases, webpage=None, remarks=None, identifiers=None, organizations=None):
        self.id = id
        self.displayName = displayName
        self.email = email
        self.createdBy = createdBy
        self.createdOn = createdOn
        self.givenNames = givenNames
        self.familyNames = familyNames
        self.aliases = aliases
        self.webpage = webpage
        self.remarks = remarks
        self.identifiers = identifiers or []
        self.organizations = organizations or []
