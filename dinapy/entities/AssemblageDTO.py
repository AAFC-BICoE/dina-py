class AssemblageDTO:
    def __init__(self, id = None, type = "assemblage", attributes = None):
        self.id = id
        self.type = type
        self.attributes = attributes or {}

    def get_id(self):
        return self.id
    def get_type(self):
        return self.type
    def get_attributes(self):
        return self.attributes 

class AssemblageDTOBuilder:
    def __init__(self):
        self.managed_attribute = AssemblageDTO(
            id=None,
            type="assemblage",
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
        
class AssemblageAttributesDTO:
    def __init__(self, name=None, createdOn=None, createdBy=None, group=None, multilingualTitle = {}, multilingualDescription={}):
        self.name = name
        self.createdOn = createdOn
        self.createdBy = createdBy
        self.group = group
        self.multilingualTitle = multilingualTitle
        self.multilingualDescription = multilingualDescription

class AssemblageAttributesDTOBuilder:
    def __init__(self):
        self.dto = AssemblageAttributesDTO()

    def name(self, name):
        self.dto.name = name
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
    
    def multilingualTitle(self, multilingualTitle):
        self.dto.multilingualTitle = multilingualTitle
        return self

    def multilingualDescription(self, multilingualDescription):
        self.dto.multilingualDescription = multilingualDescription
        return self

    def build(self):
        return self.dto

        # {
        #     "id": "c1e66a36-bf48-40b5-885e-118e6507c2bd",
        #     "type": "assemblage",
        #     "links": {
        #         "self": "/api/v1/assemblage/c1e66a36-bf48-40b5-885e-118e6507c2bd"
        #     },
        #     "attributes": {
        #         "createdOn": "2022-11-29T13:36:56.451132Z",
        #         "createdBy": "dina-admin",
        #         "group": "aafc",
        #         "name": "assemblage test",
        #         "managedAttributes": {},
        #         "multilingualTitle": {
        #             "titles": []
        #         },
        #         "multilingualDescription": {
        #             "descriptions": []
        #         }
        #     },
        #     "relationships": {
        #         "attachment": {
        #             "links": {
        #                 "self": "/api/v1/assemblage/c1e66a36-bf48-40b5-885e-118e6507c2bd/relationships/attachment",
        #                 "related": "/api/v1/assemblage/c1e66a36-bf48-40b5-885e-118e6507c2bd/attachment"
        #             }
        #         }
        #     }
        # }