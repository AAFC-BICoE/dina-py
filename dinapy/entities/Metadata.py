class MetadataDTO:
    def __init__(self, id=None, type="metadata", attributes=None, relationships=None):
        self.id = id
        self.type = type
        self.attributes = attributes or {}
        self.relationships = relationships or {}


class MetadataDTOBuilder:
    def __init__(self):
        self.metadata = MetadataDTO(
            id=None, type="metadata", attributes=None, relationships=None
        )

    def attributes(self, attributes):
        self.metadata.attributes = attributes
        return self

    def relationships(self, relationships):
        self.metadata.relationships = relationships
        return self

    def build(self):
        return self.metadata


class MetadataAttributesDTO:
    def __init__(
        self,
        version=None,
        createdBy=None,
        createdOn=None,
        bucket=None,
        fileIdentifier=None,
        fileExtension=None,
        resourceExternalURL=None,
        dcFormat=None,
        dcType=None,
        acCaption=None,
        acDigitizationDate=None,
        xmpMetadataDate=None,
        xmpRightsWebStatement=None,
        dcRights=None,
        xmpRightsOwner=None,
        xmpRightsUsageTerms=None,
        orientation=None,
        originalFilename=None,
        acHashFunction=None,
        acHashValue=None,
        acTags=None,
        publiclyReleasable=None,
        notPubliclyReleasableReason=None,
        acSubtype=None,
        managedAttributes={},
        group=None,
    ):
        self.version = version
        self.createdBy = createdBy
        self.createdOn = createdOn
        self.bucket = bucket
        self.fileIdentifier = fileIdentifier
        self.fileExtension = fileExtension
        self.resourceExternalURL = resourceExternalURL
        self.dcFormat = dcFormat
        self.dcType = dcType
        self.acCaption = acCaption
        self.acDigitizationDate = acDigitizationDate
        self.xmpMetadataDate = xmpMetadataDate
        self.xmpRightsWebStatement = xmpRightsWebStatement
        self.dcRights = dcRights
        self.xmpRightsOwner = xmpRightsOwner
        self.xmpRightsUsageTerms = xmpRightsUsageTerms
        self.orientation = orientation
        self.originalFilename = originalFilename
        self.acHashFunction = acHashFunction
        self.acHashValue = acHashValue
        self.acTags = acTags
        self.publiclyReleasable = publiclyReleasable
        self.notPubliclyReleasableReason = notPubliclyReleasableReason
        self.acSubtype = acSubtype
        self.group = group
        self.managedAttributes = managedAttributes

class MetadataAttributesDTOBuilder:
    def __init__(self):
        self.dto = MetadataAttributesDTO()

    def version(self, version):
        self.dto.version = version
        return self
    
    def createdBy(self, createdBy):
        self.dto.createdBy = createdBy
        return self

    def createdOn(self, createdOn):
        self.dto.createdOn = createdOn
        return self

    def bucket(self, bucket):
        self.dto.bucket = bucket
        return self
    
    def fileIdentifier(self, fileIdentifier):
        self.dto.fileIdentifier = fileIdentifier
        return self
    
    def fileExtension(self, fileExtension):
        self.dto.fileExtension = fileExtension
        return self
    
    def resourceExternalURL(self, resourceExternalURL):
        self.dto.resourceExternalURL = resourceExternalURL
        return self
    
    def dcFormat(self, dcFormat):
        self.dto.dcFormat = dcFormat
        return self
    
    def dcType(self, dcType):
        self.dto.dcType = dcType
        return self
    
    def acCaption(self, acCaption):
        self.dto.acCaption = acCaption
        return self
    
    def acDigitizationDate(self, acDigitizationDate):
        self.dto.acDigitizationDate = acDigitizationDate
        return self
    
    def xmpMetadataDate(self, xmpMetadataDate):
        self.dto.xmpMetadataDate = xmpMetadataDate
        return self
    
    def xmpRightsWebStatement(self, xmpRightsWebStatement):
        self.dto.xmpRightsWebStatement = xmpRightsWebStatement
        return self
    
    def dcRights(self, dcRights):
        self.dto.dcRights = dcRights
        return self
    
    def xmpRightsOwner(self, xmpRightsOwner):
        self.dto.xmpRightsOwner = xmpRightsOwner
        return self
    
    def xmpRightsUsageTerms(self, xmpRightsUsageTerms):
        self.dto.xmpRightsUsageTerms = xmpRightsUsageTerms
        return self
    
    def orientation(self, orientation):
        self.dto.orientation = orientation
        return self
    
    def originalFilename(self, originalFilename):
        self.dto.originalFilename = originalFilename
        return self
    
    def acHashFunction(self, acHashFunction):
        self.dto.acHashFunction = acHashFunction
        return self
    
    def acHashValue(self, acHashValue):
        self.dto.acHashValue = acHashValue
        return self
    
    def acTags(self, acTags):
        self.dto.acTags = acTags
        return self

    def publiclyReleasable(self, publiclyReleasable):
        self.dto.publiclyReleasable = publiclyReleasable
        return self
    
    def notPubliclyReleasableReason(self, notPubliclyReleasableReason):
        self.dto.notPubliclyReleasableReason = notPubliclyReleasableReason
        return self
    
    def acSubtype(self, acSubtype):
        self.dto.acSubtype = acSubtype
        return self

    def group(self, group):
        self.dto.group = group
        return self

    def managedAttributes(self, managedAttributes):
        self.dto.managedAttributes = managedAttributes
        return self

    def build(self):
        return self.dto
