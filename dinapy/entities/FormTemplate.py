class FormTemplateDTO:
	def __init__(self, id=None, type=None, attributes=None, relationships=None):
		self.id = id
		self.type = type
		self.attributes = attributes
		self.relationships = relationships

	def get_id(self):
		return self.id

	def get_type(self):
		return self.type

class FormTemplateDTOBuilder:
	def __init__(self):
		self._id = None
		self._type = 'form-template'
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
		return FormTemplateDTO(self._id, self._type, self._attributes, self._relationships)

class FormTemplateAttributesDTO:
	def __init__(
			self, 
			createdOn=None, 
			createdBy=None,
			group=None,
			name=None,
			restrictToCreatedBy=None,
			viewConfiguration=None,
			components=None
		):
		self.createdOn = createdOn
		self.createdBy = createdBy
		self.group = group
		self.name = name
		self.restrictToCreatedBy = restrictToCreatedBy
		self.viewConfiguration = viewConfiguration
		self.components = components

class FormTemplateAttributesDTOBuilder:
	def __init__(self):
		self._createdOn = 'undefined'
		self._createdBy = 'undefined'
		self._group = 'undefined'
		self._name = 'undefined'
		self._restrictToCreatedBy = 'undefined'
		self._viewConfiguration = 'undefined'
		self._components = 'undefined'

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
	
	def set_restrictToCreatedBy(self, restrictToCreatedBy):
			self._restrictToCreatedBy = restrictToCreatedBy
			return self

	def set_viewConfiguration(self, viewConfiguration):
			self._viewConfiguration = viewConfiguration
			return self

	def set_components(self, components):
			self._components = components
			return self

	def build(self):
			return FormTemplateAttributesDTO(
					self._createdOn,
					self._createdBy,
					self._group,
					self._name,
					self._restrictToCreatedBy,
					self._viewConfiguration,
					self._components
			)