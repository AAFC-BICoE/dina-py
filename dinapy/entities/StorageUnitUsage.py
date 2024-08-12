class StorageUnitUsageDTO:
	def __init__(self, id=None, type=None, attributes=None, relationships=None):
		self.id = id
		self.type = type
		self.attributes = attributes
		self.relationships = relationships

	def get_id(self):
		return self.id

	def get_type(self):
		return self.type

class StorageUnitUsageDTOBuilder:
	def __init__(self):
		self._id = None
		self._type = 'storage-unit-usage'
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
		return StorageUnitUsageDTO(self._id, self._type, self._attributes, self._relationships)

class StorageUnitUsageAttributesDTO:
	def __init__(self, usageType=None, wellRow=None, wellColumn=None,cellNumber=None,storageUnitName=None,createdOn=None,createdBy=None):
		self.usageType = usageType
		self.wellRow = wellRow
		self.wellColumn = wellColumn
		self.cellNumber = cellNumber
		self.storageUnitName = storageUnitName
		self.createdOn = createdOn
		self.createdBy = createdBy


class StorageUnitUsageAttributesDTOBuilder:
	def __init__(self):
		self._usageType = 'undefined'
		self._wellRow = 'undefined'
		self._wellColumn = 'undefined'
		self._cellNumber = 'undefined'
		self._storageUnitName = 'undefined'
		self._createdOn = 'undefined'
		self._createdBy = 'undefined'

	def set_usageType(self, usageType):
		self._usageType = usageType
		return self
	
	def set_wellRow(self, wellRow):
		self._wellRow = wellRow
		return self
	
	def set_wellColumn(self, wellColumn):
		self._wellColumn = wellColumn
		return self
	
	def set_cellNumber(self, cellNumber):
		self._cellNumber = cellNumber
		return self

	def set_storageUnitName(self,storageUnitName):
		self._storageUnitName = storageUnitName
		return self
	
	def set_createdOn(self, createdOn):
		self._createdOn = createdOn
		return self

	def set_createdBy(self, createdBy):
		self._createdBy = createdBy
		return self
	
	def build(self):
		return StorageUnitUsageAttributesDTO(self._usageType, self._wellRow, self._wellColumn,self._cellNumber, self._storageUnitName,self._createdOn, self._createdBy)
