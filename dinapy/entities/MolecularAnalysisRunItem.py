class MolecularAnalysisRunItemDTO:
	def __init__(self, id=None, type=None, attributes=None, relationships=None):
		self.id = id
		self.type = type
		self.attributes = attributes
		self.relationships = relationships

	def get_id(self):
		return self.id

	def get_type(self):
		return self.type

class MolecularAnalysisRunItemDTOBuilder:
	def __init__(self):
		self._id = None
		self._type = 'molecular-analysis-run-item'
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
		return MolecularAnalysisRunItemDTO(self._id, self._type, self._attributes, self._relationships)

class MolecularAnalysisRunItemAttributesDTO:
	def __init__(self, createdBy=None, createdOn=None, usageType=None):
		self.createdBy = createdBy
		self.createdOn = createdOn
		self.usageType = usageType
	
class MolecularAnalysisRunItemAttributesDTOBuilder:
	def __init__(self):
		self._createdBy = 'undefined'
		self._createdOn = 'undefined'
		self.usageType = 'undefined'

	def set_createdBy(self, createdBy):
		self._createdBy = createdBy
		return self

	def set_createdOn(self, createdOn):
		self._createdOn = createdOn
		return self

	def set_usageType(self, usageType):
		self._usageType = usageType
		return self
	
	def build(self):
		return MolecularAnalysisRunItemAttributesDTO(
			self._createdBy, 
			self._createdOn, 
			self._usageType
		)
	