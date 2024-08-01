class StorageUnitUsageDTO:
	def __init__(self, id=None, type=None, usageType=None, wellRow=None, wellColumn=None, createdOn=None, createdBy=None, storageUnit=None, storageUnitType=None, relationships=None):
		self.id = id
		self.type = type
		self.usageType = usageType
		self.wellRow = wellRow
		self.wellColumn = wellColumn
		self.createdOn = createdOn
		self.createdBy = createdBy
		self.storageUnit = storageUnit
		self.storageUnitType = storageUnitType
		self.relationships = relationships

	def get_id(self):
		return self.id

	def get_type(self):
		return self.type

class StorageUnitUsageDTOBuilder:
	def __init__(self):
		self._id = None
		self._type = 'storage-unit-usage'
		self._usageType = None
		self._wellRow = None
		self._wellColumn = None
		self._createdOn = None
		self._createdBy = None
		self._storageUnit = None
		self._storageUnitType = None
		self._relationships = None

	def set_id(self, id):
		self._id = id
		return self

	def set_type(self, type):
		self._type = type
		return self

	def set_usageType(self, usageType):
		self._usageType = usageType
		return self
	
	def set_wellRow(self, wellRow):
		self._wellRow = wellRow
		return self
	
	def set_wellColumn(self, wellColumn):
		self._wellColumn = wellColumn
		return self
	
	def set_createdOn(self, createdOn):
		self._createdOn = createdOn
		return self

	def set_createdBy(self, createdBy):
		self._createdBy = createdBy
		return self
	
	def set_storageUnit(self, storageUnit):
		self._storageUnit = storageUnit
		return self
	
	def set_storageUnitType(self, storageUnitType):
		self._storageUnitType = storageUnitType
		return self
	
	def set_relationships(self, relationships):
		self._relationships = relationships
		return self

	def build(self):
		return StorageUnitUsageDTO(self._id, self._type, self._usageType, self._wellRow, self._wellColumn, self._createdOn, self._createdBy, self._storageUnit, self._storageUnitType, self._relationships)
