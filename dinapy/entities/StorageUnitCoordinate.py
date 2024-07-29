class StorageUnitCoordinateDTO:
    def __init__(self, id = None, type = "storage-unit-usage", attributes = None, relationships = None):
        self.id = id
        self.type = type
        self.attributes = attributes or {}
        self.relationships = relationships or {}

    def get_id(self):
        return self.id

    def get_type(self):
        return self.type

    def get_attributes(self):
        return self.attributes

    def get_relationships(self):
        return self.relationships
    
class StorageUnitCoordinateDTOBuilder:
    def __init__(self):
        self.dto = StorageUnitCoordinateDTO(
            id=None,
            type="storage-unit-usage",
            attributes=None,
            relationships=None
        )

    def attributes(self, attributes):
        self.dto.attributes = attributes
        return self

    def relationships(self, relationships):
        self.dto.relationships = relationships
        return self

    def build(self):
        return self.dto

class StorageUnitCoordinateAttributesDTO:
    def __init__(self, usageType=None, wellRow=None, wellColumn=None, createdOn=None, createdBy=None):
        self.usageType = usageType
        self.wellRow = wellRow
        self.wellColumn = wellColumn
        self.createdOn = createdOn
        self.createdBy = createdBy

class StorageUnitCoordinateAttributesDTOBuilder:
    def __init__(self):
        self.dto = StorageUnitCoordinateAttributesDTO()

    def usageType(self, usageType):
        self.dto.usageType = usageType
        return self

    def wellRow(self, wellRow):
        self.dto.wellRow = wellRow
        return self
    
    def wellColumn(self, wellColumn):
        self.dto.wellColumn = wellColumn
        return self

    def createdBy(self, createdBy):
        self.dto.createdBy = createdBy
        return self

    def createdOn(self, createdOn):
        self.dto.createdOn = createdOn
        return self

    def build(self):
        return self.dto

