class MolecularAnalysisResultDTO:
	def __init__(self, id=None, type=None, attributes=None, relationships=None):
		self.id = id
		self.type = type
		self.attributes = attributes
		self.relationships = relationships

	def get_id(self):
		return self.id

	def get_type(self):
		return self.type

class MolecularAnalysisResultDTOBuilder:
	def __init__(self):
		self._id = None
		self._type = 'molecular-analysis-result'
		self._attributes = None
		self._relationships = None

	def set_id(self, id):
		self._id = id
		return self

	def set_type(self, type):
		self._type = type
		return self

	def set_attributes(self, attributes):
		self._attributes = attributes.to_dict()
		return self

	def set_relationships(self, relationships):
		self._relationships = relationships
		return self

	def build(self):
		return MolecularAnalysisResultDTO(self._id, self._type, self._attributes, self._relationships)

class MolecularAnalysisResultAttributesDTO:
	def __init__(self, group=None, createdBy=None, createdOn=None):
		self.group = group
		self.createdBy = createdBy
		self.createdOn = createdOn
	
	def to_dict(self):
		return self.__dict__
	
class MolecularAnalysisResultAttributesDTOBuilder:
	def __init__(self):
		self._group = 'undefined'
		self._createdBy = 'undefined'
		self._createdOn = 'undefined'
	
	def set_group(self, group):
		self._group = group
		return self
	
	def set_createdBy(self, createdBy):
		self._createdBy = createdBy
		return self

	def set_createdOn(self, createdOn):
		self._createdOn = createdOn
		return self
	
	def build(self):
		return MolecularAnalysisResultAttributesDTO(
			self._group,
			self._createdBy,
			self._createdOn
		)