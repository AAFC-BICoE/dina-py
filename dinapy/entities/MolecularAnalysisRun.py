class MolecularAnalysisRunDTO:
	def __init__(self, id=None, type=None, attributes=None, relationships=None):
		self.id = id
		self.type = type
		self.attributes = attributes
		self.relationships = relationships

	def get_id(self):
		return self.id

	def get_type(self):
		return self.type

class MolecularAnalysisRunDTOBuilder:
	def __init__(self):
		self._id = None
		self._type = 'molecular-analysis-run'
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
		return MolecularAnalysisRunDTO(self._id, self._type, self._attributes, self._relationships)

class MolecularAnalysisRunAttributesDTO:
	def __init__(self, createdBy=None, createdOn=None, group=None, name=None, sequenceNumber=None):
		self.createdBy = createdBy
		self.createdOn = createdOn
		self.group = group
		self.name = name
		self.sequenceNumber = sequenceNumber
	
class MolecularAnalysisRunAttributesDTOBuilder:
	def __init__(self):
		self._createdBy = 'undefined'
		self._createdOn = 'undefined'
		self._group = 'undefined'
		self._name = 'undefined'
		self._sequenceNumber = 'undefined'

	def set_createdBy(self, createdBy):
		self._createdBy = createdBy
		return self

	def set_createdOn(self, createdOn):
		self._createdOn = createdOn
		return self
	
	def set_group(self, group):
		self._group = group
		return self
	
	def set_name(self, name):
		self._name = name
		return self
	
	def set_sequenceNumber(self, sequenceNumber):
		self._sequenceNumber = sequenceNumber
		return self
	
	def build(self):
		return MolecularAnalysisRunAttributesDTO(self._createdBy, self._createdOn, self._group, self._name, self._sequenceNumber)