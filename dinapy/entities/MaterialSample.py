class MaterialSampleDTO:
	def __init__(self, id = None, type = 'material-sample', attributes = None, relationships = 'undefined'):
		self.id = id
		self.type = type
		self.attributes = attributes
		self.relationships = relationships

	def get_id(self):
		return self.id

	def get_type(self):
		return self.type

class MaterialSampleDTOBuilder:
	def __init__(self):
		self._id = None
		self._type = 'material-sample'
		self._attributes = None
		self._relationships = None

	def id(self, id):
		self._id = id
		return self
	
	def attributes(self, attributes):
		self._attributes = attributes
		return self

	def relationships(self, relationships):
		self._relationships = relationships
		return self

	def build(self):
		return MaterialSampleDTO(self._id, self._type, self._attributes, self._relationships)


class MaterialSampleAttributesDTO:
	def __init__(self, version='undefined', group='undefined', createdOn='undefined', createdBy='undefined', dwcCatalogNumber='undefined', dwcOtherCatalogNumbers='undefined', materialSampleName='undefined', materialSampleType='undefined', materialSampleChildren='undefined', preparationDate='undefined', preservationType='undefined', preparationFixative='undefined', preparationMaterials='undefined', preparationSubstrate='undefined', managedAttributes={}, preparationManagedAttributes={}, extensionValues='undefined', preparationRemarks='undefined', dwcDegreeOfEstablishment='undefined', barcode='undefined', publiclyReleasable='undefined', notPubliclyReleasableReason='undefined', tags='undefined', materialSampleState='undefined', materialSampleRemarks='undefined', stateChangedOn='undefined', stateChangeRemarks='undefined', associations='undefined', allowDuplicateName=False, restrictionFieldsExtension='undefined', isRestricted=False, restrictionRemarks='undefined', sourceSet='undefined'):
		self.version = version
		self.group = group
		self.createdOn = createdOn
		self.createdBy = createdBy
		self.dwcCatalogNumber = dwcCatalogNumber
		self.dwcOtherCatalogNumbers = dwcOtherCatalogNumbers
		self.materialSampleName = materialSampleName
		self.materialSampleType = materialSampleType
		self.materialSampleChildren = materialSampleChildren
		self.preparationDate = preparationDate
		self.preservationType = preservationType
		self.preparationFixative = preparationFixative
		self.preparationMaterials = preparationMaterials
		self.preparationSubstrate = preparationSubstrate
		self.managedAttributes = managedAttributes
		self.preparationManagedAttributes = preparationManagedAttributes
		self.extensionValues = extensionValues
		self.preparationRemarks = preparationRemarks
		self.dwcDegreeOfEstablishment = dwcDegreeOfEstablishment
		self.barcode = barcode
		self.publiclyReleasable = publiclyReleasable
		self.notPubliclyReleasableReason = notPubliclyReleasableReason
		self.tags = tags
		self.materialSampleState = materialSampleState
		self.materialSampleRemarks = materialSampleRemarks
		self.stateChangedOn = stateChangedOn
		self.stateChangeRemarks = stateChangeRemarks
		self.associations = associations
		self.allowDuplicateName = allowDuplicateName
		self.restrictionFieldsExtension = restrictionFieldsExtension
		self.isRestricted = isRestricted
		self.restrictionRemarks = restrictionRemarks
		self.sourceSet = sourceSet
	
class MaterialSampleAttributesDTOBuilder:
	def __init__(self):
		self._version = 'undefined'
		self._group = 'undefined'
		self._createdOn = 'undefined'
		self._createdBy = 'undefined'
		self._dwcCatalogNumber = 'undefined'
		self._dwcOtherCatalogNumbers = 'undefined'
		self._materialSampleName = 'undefined'
		self._materialSampleType = 'undefined'
		self._materialSampleChildren = 'undefined'
		self._preparationDate = 'undefined'
		self._preservationType = 'undefined'
		self._preparationFixative = 'undefined'
		self._preparationMaterials = 'undefined'
		self._preparationSubstrate = 'undefined'
		self._managedAttributes = 'undefined'
		self._preparationManagedAttributes = 'undefined'
		self._extensionValues = 'undefined'
		self._preparationRemarks = 'undefined'
		self._dwcDegreeOfEstablishment = 'undefined'
		self._barcode = 'undefined'
		self._publiclyReleasable = 'undefined'
		self._notPubliclyReleasableReason = 'undefined'
		self._tags = 'undefined'
		self._materialSampleState = 'undefined'
		self._materialSampleRemarks = 'undefined'
		self._stateChangedOn = 'undefined'
		self._stateChangeRemarks = 'undefined'
		self._associations = 'undefined'
		self._allowDuplicateName = 'undefined'
		self._restrictionFieldsExtension = 'undefined'
		self._isRestricted = 'undefined'
		self._restrictionRemarks = 'undefined'
		self._sourceSet = 'undefined'
	def version(self, version):
		self._version = version
		return self

	def group(self, group):
		self._group = group
		return self

	def createdOn(self, createdOn):
		self._createdOn = createdOn
		return self

	def createdBy(self, createdBy):
		self._createdBy = createdBy
		return self

	def dwcCatalogNumber(self, dwcCatalogNumber):
		self._dwcCatalogNumber = dwcCatalogNumber
		return self

	def dwcOtherCatalogNumbers(self, dwcOtherCatalogNumbers):
		self._dwcOtherCatalogNumbers = dwcOtherCatalogNumbers
		return self

	def materialSampleName(self, materialSampleName):
		self._materialSampleName = materialSampleName
		return self

	def materialSampleType(self, materialSampleType):
		self._materialSampleType = materialSampleType
		return self

	def materialSampleChildren(self, materialSampleChildren):
		self._materialSampleChildren = materialSampleChildren
		return self

	def preparationDate(self, preparationDate):
		self._preparationDate = preparationDate
		return self

	def preservationType(self, preservationType):
		self._preservationType = preservationType
		return self

	def preparationFixative(self, preparationFixative):
		self._preparationFixative = preparationFixative
		return self

	def preparationMaterials(self, preparationMaterials):
		self._preparationMaterials = preparationMaterials
		return self

	def preparationSubstrate(self, preparationSubstrate):
		self._preparationSubstrate = preparationSubstrate
		return self

	def managedAttributes(self, managedAttributes):
		self._managedAttributes = managedAttributes
		return self

	def preparationManagedAttributes(self, preparationManagedAttributes):
		self._preparationManagedAttributes = preparationManagedAttributes
		return self

	def extensionValues(self, extensionValues):
		self._extensionValues = extensionValues
		return self

	def preparationRemarks(self, preparationRemarks):
		self._preparationRemarks = preparationRemarks
		return self

	def dwcDegreeOfEstablishment(self, dwcDegreeOfEstablishment):
		self._dwcDegreeOfEstablishment = dwcDegreeOfEstablishment
		return self

	def barcode(self, barcode):
		self._barcode = barcode
		return self

	def publiclyReleasable(self, publiclyReleasable):
		self._publiclyReleasable = publiclyReleasable
		return self

	def notPubliclyReleasableReason(self, notPubliclyReleasableReason):
		self._notPubliclyReleasableReason = notPubliclyReleasableReason
		return self

	def tags(self, tags):
		self._tags = tags
		return self

	def materialSampleState(self, materialSampleState):
		self._materialSampleState = materialSampleState
		return self

	def materialSampleRemarks(self, materialSampleRemarks):
		self._materialSampleRemarks = materialSampleRemarks
		return self

	def stateChangedOn(self, stateChangedOn):
		self._stateChangedOn = stateChangedOn
		return self

	def stateChangeRemarks(self, stateChangeRemarks):
		self._stateChangeRemarks = stateChangeRemarks
		return self

	def associations(self, associations):
		self._associations = associations
		return self

	def allowDuplicateName(self, allowDuplicateName):
		self._allowDuplicateName = allowDuplicateName
		return self

	def restrictionFieldsExtension(self, restrictionFieldsExtension):
		self._restrictionFieldsExtension = restrictionFieldsExtension
		return self

	def isRestricted(self, isRestricted):
		self._isRestricted = isRestricted
		return self

	def restrictionRemarks(self, restrictionRemarks):
		self._restrictionRemarks = restrictionRemarks
		return self

	def sourceSet(self, sourceSet):
		self._sourceSet = sourceSet
		return self

	def build(self):
		return MaterialSampleAttributesDTO(self._version, self._group, self._createdOn, self._createdBy, self._dwcCatalogNumber, self._dwcOtherCatalogNumbers, self._materialSampleName, self._materialSampleType, self._materialSampleChildren, self._preparationDate, self._preservationType, self._preparationFixative, self._preparationMaterials, self._preparationSubstrate, self._managedAttributes, self._preparationManagedAttributes, self._extensionValues, self._preparationRemarks, self._dwcDegreeOfEstablishment, self._barcode, self._publiclyReleasable, self._notPubliclyReleasableReason, self._tags, self._materialSampleState, self._materialSampleRemarks, self._stateChangedOn, self._stateChangeRemarks, self._associations, self._allowDuplicateName, self._restrictionFieldsExtension, self._isRestricted, self._restrictionRemarks, self._sourceSet)


