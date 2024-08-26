class SplitConfigurationDTO:
	def __init__(self, id=None, type=None, attributes=None, relationships=None):
		self.id = id
		self.type = type
		self.attributes = attributes
		self.relationships = relationships

	def get_id(self):
		return self.id

	def get_type(self):
		return self.type


class SplitConfigurationDTOBuilder:
	def __init__(self):
		self._id = None
		self._type = 'split-configuration'
		self._attributes = None
		self._relationships = None

	def attributes(self, attributes):
		self._attributes = attributes
		return self
	
	def relationships(self, relationships):
		self._relationships = relationships
		return self

	def build(self):
		return SplitConfigurationDTO(self._id, self._type, self._attributes, self._relationships)


class SplitConfigurationAttributesDTO:
	def __init__(
			self, 
			createdOn=None, 
			createdBy=None,
			group=None,
			name=None,
			strategy=None,
			conditionalOnMaterialSampleTypes=None,
			characterType=None,
			separator=None,
			materialSampleTypeCreatedBySplit=None
		):
		self.createdOn = createdOn
		self.createdBy = createdBy
		self.group = group
		self.name = name
		self.strategy = strategy
		self.conditionalOnMaterialSampleTypes = conditionalOnMaterialSampleTypes
		self.characterType = characterType
		self.separator = separator
		self.materialSampleTypeCreatedBySplit = materialSampleTypeCreatedBySplit


class SplitConfigurationAttributesDTOBuilder:
	def __init__(self):
		self._createdOn = None
		self._createdBy = None
		self._group = None
		self._name = None
		self._strategy = None
		self._conditionalOnMaterialSampleTypes = None
		self._characterType = None
		self._separator = None
		self._materialSampleTypeCreatedBySplit = None

	def set_createdOn(self, createdOn):
		self._createdOn = createdOn
		return self

	def set_createdBy(self, createdBy):
		self._createdBy = createdBy
		return self

	def set_group(self, group):
			self._group = group
			return self

	def set_name(self, name):
			self._name = name
			return self

	def set_strategy(self, strategy):
			self._strategy = strategy
			return self

	def set_conditionalOnMaterialSampleTypes(self, conditionalOnMaterialSampleTypes):
			self._conditionalOnMaterialSampleTypes = conditionalOnMaterialSampleTypes
			return self

	def set_characterType(self, characterType):
			self._characterType = characterType
			return self

	def set_separator(self, separator):
			self._separator = separator
			return self

	def set_materialSampleTypeCreatedBySplit(self, materialSampleTypeCreatedBySplit):
			self._materialSampleTypeCreatedBySplit = materialSampleTypeCreatedBySplit
			return self

	def build(self):
			return SplitConfigurationAttributesDTO(
					self._createdOn,
					self._createdBy,
					self._group,
					self._name,
					self._strategy,
					self._conditionalOnMaterialSampleTypes,
					self._characterType,
					self._separator,
					self._materialSampleTypeCreatedBySplit
			)
