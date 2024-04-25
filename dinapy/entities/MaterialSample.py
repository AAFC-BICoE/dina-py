class MaterialSampleDTO:
    def __init__(self, id = None, type = "material-sample", attributes = None, relationships = None):
        self.id = id
        self.type = type
        self.attributes = attributes or {}
        self.relationships = relationships or {}

class MaterialSampleDTOBuilder:
    def __init__(self):
        self.material_sample = MaterialSampleDTO(
            id=None,
            type="material-sample",
            attributes=None,
            relationships=None
        )

    def id(self, id):
        self.material_sample.id = id
        return self
    
    def attributes(self, attributes):
        self.material_sample.attributes = attributes
        return self

    def relationships(self, relationships):
        self.material_sample.relationships = relationships
        return self

    def build(self):
        return self.material_sample


class MaterialSampleAttributesDTO:
    def __init__(self, version=None, group=None, createdOn=None, createdBy=None, dwcCatalogNumber=None, dwcOtherCatalogNumbers=None, materialSampleName=None, materialSampleType=None, materialSampleChildren=None, preparationDate=None, preservationType=None, preparationFixative=None, preparationMaterials=None, preparationSubstrate=None, managedAttributes={}, preparationManagedAttributes={}, extensionValues=None, preparationRemarks=None, dwcDegreeOfEstablishment=None, barcode=None, publiclyReleasable=None, notPubliclyReleasableReason=None, tags=None, materialSampleState=None, materialSampleRemarks=None, stateChangedOn=None, stateChangeRemarks=None, associations=None, allowDuplicateName=False, restrictionFieldsExtension=None, isRestricted=False, restrictionRemarks=None, sourceSet=None):
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
        self.dto = MaterialSampleAttributesDTO()

    def version(self, version):
        self.dto.version = version
        return self

    def group(self, group):
        self.dto.group = group
        return self

    def createdOn(self, createdOn):
        self.dto.createdOn = createdOn
        return self

    def createdBy(self, createdBy):
        self.dto.createdBy = createdBy
        return self

    def dwcCatalogNumber(self, dwcCatalogNumber):
        self.dto.dwcCatalogNumber = dwcCatalogNumber
        return self

    def dwcOtherCatalogNumbers(self, dwcOtherCatalogNumbers):
        self.dto.dwcOtherCatalogNumbers = dwcOtherCatalogNumbers
        return self

    def materialSampleName(self, materialSampleName):
        self.dto.materialSampleName = materialSampleName
        return self

    def materialSampleType(self, materialSampleType):
        self.dto.materialSampleType = materialSampleType
        return self

    def materialSampleChildren(self, materialSampleChildren):
        self.dto.materialSampleChildren = materialSampleChildren
        return self

    def preparationDate(self, preparationDate):
        self.dto.preparationDate = preparationDate
        return self

    def preservationType(self, preservationType):
        self.dto.preservationType = preservationType
        return self

    def preparationFixative(self, preparationFixative):
        self.dto.preparationFixative = preparationFixative
        return self

    def preparationMaterials(self, preparationMaterials):
        self.dto.preparationMaterials = preparationMaterials
        return self

    def preparationSubstrate(self, preparationSubstrate):
        self.dto.preparationSubstrate = preparationSubstrate
        return self

    def managedAttributes(self, managedAttributes):
        self.dto.managedAttributes = managedAttributes
        return self

    def preparationManagedAttributes(self, preparationManagedAttributes):
        self.dto.preparationManagedAttributes = preparationManagedAttributes
        return self

    def extensionValues(self, extensionValues):
        self.dto.extensionValues = extensionValues
        return self

    def preparationRemarks(self, preparationRemarks):
        self.dto.preparationRemarks = preparationRemarks
        return self

    def dwcDegreeOfEstablishment(self, dwcDegreeOfEstablishment):
        self.dto.dwcDegreeOfEstablishment = dwcDegreeOfEstablishment
        return self

    def barcode(self, barcode):
        self.dto.barcode = barcode
        return self

    def publiclyReleasable(self, publiclyReleasable):
        self.dto.publiclyReleasable = publiclyReleasable
        return self

    def notPubliclyReleasableReason(self, notPubliclyReleasableReason):
        self.dto.notPubliclyReleasableReason = notPubliclyReleasableReason
        return self

    def tags(self, tags):
        self.dto.tags = tags
        return self

    def materialSampleState(self, materialSampleState):
        self.dto.materialSampleState = materialSampleState
        return self

    def materialSampleRemarks(self, materialSampleRemarks):
        self.dto.materialSampleRemarks = materialSampleRemarks
        return self

    def stateChangedOn(self, stateChangedOn):
        self.dto.stateChangedOn = stateChangedOn
        return self

    def stateChangeRemarks(self, stateChangeRemarks):
        self.dto.stateChangeRemarks = stateChangeRemarks
        return self

    def associations(self, associations):
        self.dto.associations = associations
        return self

    def allowDuplicateName(self, allowDuplicateName):
        self.dto.allowDuplicateName = allowDuplicateName
        return self

    def restrictionFieldsExtension(self, restrictionFieldsExtension):
        self.dto.restrictionFieldsExtension = restrictionFieldsExtension
        return self

    def isRestricted(self, isRestricted):
        self.dto.isRestricted = isRestricted
        return self

    def restrictionRemarks(self, restrictionRemarks):
        self.dto.restrictionRemarks = restrictionRemarks
        return self

    def sourceSet(self, sourceSet):
        self.dto.sourceSet = sourceSet
        return self

    def build(self):
        return self.dto



