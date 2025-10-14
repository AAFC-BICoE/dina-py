class ProjectDTO:
    def __init__(self, id = None, type = 'project', attributes = None, relationships = 'undefined'):
        self.id = id
        self.type = type
        self.attributes = attributes
        self.relationships = relationships

    def get_id(self):
        return self.id
    
    def get_type(self):
        return self.type

class ProjectDTOBuilder:
    def __init__(self):
        self._id = None
        self._type = 'project'
        self._attributes = None
        self._relationships = None

    def attributes(self, attributes):
        self._attributes = attributes.to_dict()
        return self
    
    def relationships(self, relationships):
        self._relationships = relationships
        return self
    
    def build(self):
        return ProjectDTO(self._id, self._type, self._attributes, self._relationships)
    
class ProjectAttributesDTO:
    def __init__(self, createdOn = 'undefined',
                 contributors = 'undefined', 
                 createdBy = 'undefined', 
                 group = 'undefined', 
                 name = 'undefined', 
                 startDate = 'undefined',
                 endDate = 'undefined', 
                 status = 'undefined', 
                 multilingualDescription = 'undefined', 
                 extensionValues = 'undefined'):
        self.createdOn = createdOn
        self.contributors = contributors
        self.createdBy = createdBy
        self.group = group
        self.name = name
        self.startDate = startDate
        self.endDate = endDate
        self.status = status
        self.multilingualDescription = multilingualDescription
        self.extensionValues = extensionValues

    def to_dict(self):
        return self.__dict__
        
class ProjectAttributesDTOBuilder:
    def __init__(self):
        self._createdOn = 'undefined'
        self._contributors = 'undefined'
        self._createdBy = 'undefined'
        self._group = 'undefined'
        self._name = 'undefined'
        self._startDate = 'undefined'
        self._endDate = 'undefined'
        self._status = 'undefined'
        self._multilingualDescription = 'undefined'
        self._extensionValues = 'undefined'

    def createdOn(self, createdOn):
        self._createdOn = createdOn
        return self
    
    def contributors(self, contributors):
        self._contributors = contributors
        return contributors
    
    def createdBy(self, createdBy):
        self._createdBy = createdBy
        return self
    
    def group(self, group):
        self._group = group
        return self
    
    def name(self, name):
        self._name = name
        return self
    
    def startDate(self, startDate):
        self._startDate = startDate
        return self
    
    def endDate(self, endDate):
        self._endDate = endDate
        return self
    
    def status(self, status):
        self._status = status
        return self
    
    def multilingualDescription(self, multilingualDescription):
        self._multilingualDescription = multilingualDescription
        return self

    def extensionValues(self, extensionValues):
        self._extensionValues = extensionValues
        return self
    
    def build(self):
        return ProjectAttributesDTO(
        self._createdOn,
        self._contributors,
        self._createdBy,
        self._group,
        self._name,
        self._startDate,
        self._endDate,
        self._status,
        self._multilingualDescription,
        self._extensionValues
        )