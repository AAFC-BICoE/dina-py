class ManagedAttributesDTO:
    def __init__(self, id = None, type = "managed-attribute", attributes = None):
        self.id = id
        self.type = type
        self.attributes = attributes or {}

    def get_id(self):
        return self.id
    def get_type(self):
        return self.type
    def get_attributes(self):
        return self.attributes 

class ManagedAttributesDTOBuilder:
    def __init__(self):
        self.managed_attribute = ManagedAttributesDTO(
            id=None,
            type="managed-attribute",
            attributes=None
        )

    def id(self, id):
        self.managed_attribute.id = id
        return self
    
    def attributes(self, attributes):
        self.managed_attribute.attributes = attributes
        return self

    def build(self):
        return self.managed_attribute

    def to_dict(self):
        return self.__dict__
        
class ManagedAttributeAttributesDTO:
    def __init__(self, name=None, key=None, vocabularyElementType=None, unit=None, managedAttributeComponent=None, acceptedValues=None, createdOn=None, createdBy=None, group=None, multilingualDescription={}):
        self.name = name
        self.key = key
        self.vocabularyElementType = vocabularyElementType
        self.unit = unit
        self.managedAttributeComponent = managedAttributeComponent
        self.acceptedValues = acceptedValues
        self.createdOn = createdOn
        self.createdBy = createdBy
        self.group = group
        self.multilingualDescription = multilingualDescription

class ManagedAttributeAttributesDTOBuilder:
    def __init__(self):
        self.dto = ManagedAttributeAttributesDTO()

    def name(self, name):
        self.dto.name = name
        return self

    def key(self, key):
        self.dto.key = key
        return self

    def vocabularyElementType(self, vocabularyElementType):
        self.dto.vocabularyElementType = vocabularyElementType
        return self

    def unit(self, unit):
        self.dto.unit = unit
        return self

    def managedAttributeComponent(self, managedAttributeComponent):
        self.dto.managedAttributeComponent = managedAttributeComponent
        return self

    def acceptedValues(self, acceptedValues):
        self.dto.acceptedValues = acceptedValues
        return self

    def createdOn(self, createdOn):
        self.dto.createdOn = createdOn
        return self

    def createdBy(self, createdBy):
        self.dto.createdBy = createdBy
        return self

    def group(self, group):
        self.dto.group = group
        return self

    def multilingualDescription(self, multilingualDescription):
        self.dto.multilingualDescription = multilingualDescription
        return self

    def build(self):
        return self.dto

# {
#             "id": "46000e84-4b86-431b-a8c4-68c629d48a5c",
#             "type": "managed-attribute",
#             "links": {
#                 "self": "/api/v1/managed-attribute/46000e84-4b86-431b-a8c4-68c629d48a5c"
#             },
#             "attributes": {
#                 "name": "bushel weight",
#                 "key": "bushel_weight",
#                 "vocabularyElementType": "DECIMAL",
#                 "unit": null,
#                 "managedAttributeComponent": "MATERIAL_SAMPLE",
#                 "acceptedValues": null,
#                 "createdOn": "2023-02-27T20:36:50.581146Z",
#                 "createdBy": "s-ltae",
#                 "group": "ltae",
#                 "multilingualDescription": {
#                     "descriptions": [
#                         {
#                             "lang": "en",
#                             "desc": "Bushel weight in pounds per bushel"
#                         },
#                         {
#                             "lang": "fr",
#                             "desc": "Poids de boisseau en livres par boisseau"
#                         }
#                     ]
#                 }
#             }
#         }