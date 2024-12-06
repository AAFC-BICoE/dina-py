class MetagenomicsBatchItemDTO:
    def __init__(self, id=None, type=None, attributes=None, relationships=None):
        self.id = id
        self.type = type
        self.attributes = attributes
        self.relationships = relationships

    def get_id(self):
        return self.id
    
    def get_type(self):
        return self.type

class MetagenomicsBatchItemDTOBuilder:
    def __init__(self):
        self._id = None
        self._type = 'metagenomics-batch'
        self._attributes = None
        self._relationships = None

    def set_id(self, id):
        self._id = id
        return self
    
    def set_type(self, type):
        self._type = type
        return self
    
    def set_attributes(self, attributes):
        self._attributes = attributes
        return self

    def set_relationships(self, relationships):
        self._relationships = relationships
        return self

    def build(self):
        return MetagenomicsBatchItemDTO(self._id, self._type, self._attributes, self._relationships)

class MetagenomicsBatchItemAttributesDTO:
    def __init__(self, createdBy=None, createdOn=None):
        self.createdBy = createdBy
        self.createdOn = createdOn

class MetagenomicsBatchItemAttributesDTOBuilder:
    def __init__(self):
        self._createdBy = 'undefined'
        self._createdOn = 'undefined'

    def set_createdBy(self, createdBy):
        self._createdBy = createdBy
        return self

    def set_createdOn(self, createdOn):
        self._createdOn = createdOn
        return self

    def build(self):
        return MetagenomicsBatchItemAttributesDTO(
            self._createdBy, 
            self._createdOn
        )