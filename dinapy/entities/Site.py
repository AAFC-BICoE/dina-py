class SiteDTO:
	def __init__(self, id = None, type = 'site', attributes = None, relationships = 'undefined'):
		self.id = id
		self.type = type
		self.attributes = attributes
		self.relationships = relationships

	def get_id(self):
		return self.id

	def get_type(self):
		return self.type

	def get_attributes(self):
		return self.attributes
	
class SiteDTOBuilder:
	def __init__(self):
		self._id = None
		self._type = 'site'
		self._attributes = None
		self._relationships = None

	def id(self, id):
		self._id = id
		return self
	
	def attributes(self, attributes):
		self._attributes = attributes.to_dict()
		return self

	def relationships(self, relationships):
		self._relationships = relationships
		return self

	def build(self):
		return SiteDTO(self._id, self._type, self._attributes, self._relationships)


class SiteAttributesDTO:
	def __init__(self, createdOn='undefined', createdBy='undefined', group='undefined', name='undefined', code='undefined', siteGeom='undefined', multilingualDescription='undefined'):
		self.createdOn = createdOn
		self.createdBy = createdBy
		self.group = group
		self.name = name
		self.code = code
		self.siteGeom = siteGeom
		self.multilingualDescription = multilingualDescription
	
	def to_dict(self):
		return self.__dict__
	
class SiteAttributesDTOBuilder:
	def __init__(self):
		self._createdOn = 'undefined'
		self._createdBy = 'undefined'
		self._group = 'undefined'
		self._name = 'undefined'
		self._code = 'undefined'
		self._siteGeom = 'undefined'
		self._multilingualDescription = 'undefined'

	def createdOn(self, createdOn):
		self._createdOn = createdOn
		return self

	def createdBy(self, createdBy):
		self._createdBy = createdBy
		return self

	def group(self, group):
		self._group = group
		return self

	def name(self, name):
		self._name = name
		return self

	def code(self, code):
		self._code = code
		return self

	def siteGeom(self, siteGeom):
		self._siteGeom = siteGeom
		return self

	def multilingualDescription(self, multilingualDescription):
		self._multilingualDescription = multilingualDescription
		return self
	
	def build(self):
		return SiteAttributesDTO(self._createdOn, self._createdBy, self._group, self._name, self._code, self._siteGeom, self._multilingualDescription)