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

    def __init__(self, id, meta, displayName, email, createdBy, createdOn, givenNames, familyNames,
                 aliases, webpage=None, remarks=None, identifiers=None, organizations=None):
        self.id = id
        self.meta = meta
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

class PersonDTO:
    def __init__(self, id=None, type='person', attributes=None, relationships='undefined'):
        self.id = id
        self.type = type
        self.attributes = attributes
        self.relationships = relationships

    def get_id(self):
        return self.id

    def get_type(self):
        return self.type

    def get_attributes(self):
        return self.attributes

    def get_relationships(self):
        return self.relationships

class PersonDTOBuilder:
    def __init__(self):
        self._id = None
        self._type = 'person'
        self._attributes = None
        self._relationships = None

    def id(self, id):
        self._id = id
        return self

    def attributes(self, attributes):
        self._attributes = attributes
        return self

    def relationships(self, relationships):
        self._relationships = relationships
        return self

    def build(self):
        return PersonDTO(self._id, self._type, self._attributes, self._relationships)


class PersonAttributesDTO:
    def __init__(self, meta='undefined', displayName='undefined', email='undefined', createdBy='undefined',
                 createdOn='undefined', givenNames='undefined', familyNames='undefined',
                 aliases=None, webpage=None, remarks=None):
        self.meta = meta
        self.displayName = displayName
        self.email = email
        self.createdBy = createdBy
        self.createdOn = createdOn
        self.givenNames = givenNames
        self.familyNames = familyNames
        self.aliases = aliases or []
        self.webpage = webpage
        self.remarks = remarks


class PersonAttributesDTOBuilder:
    def __init__(self):
        self._meta = 'undefined'
        self._displayName = 'undefined'
        self._email = 'undefined'
        self._createdBy = 'undefined'
        self._createdOn = 'undefined'
        self._givenNames = 'undefined'
        self._familyNames = 'undefined'
        self._aliases = []
        self._webpage = None
        self._remarks = None

    def meta(self, meta):
        self._meta = meta
        return self
    
    def displayName(self, displayName):
        self._displayName = displayName
        return self

    def email(self, email):
        self._email = email
        return self

    def createdBy(self, createdBy):
        self._createdBy = createdBy
        return self

    def createdOn(self, createdOn):
        self._createdOn = createdOn
        return self

    def givenNames(self, givenNames):
        self._givenNames = givenNames
        return self

    def familyNames(self, familyNames):
        self._familyNames = familyNames
        return self

    def aliases(self, aliases):
        self._aliases = aliases
        return self

    def webpage(self, webpage):
        self._webpage = webpage
        return self

    def remarks(self, remarks):
        self._remarks = remarks
        return self

    def build(self):
        return PersonAttributesDTO(
            self._meta,
            self._displayName,
            self._email,
            self._createdBy,
            self._createdOn,
            self._givenNames,
            self._familyNames,
            self._aliases,
            self._webpage,
            self._remarks
        )