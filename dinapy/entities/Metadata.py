class MetadataDTO:
    def __init__(
        self, id=None, type="metadata", attributes=None, relationships="undefined"
    ):
        self.id = id
        self.type = type
        self.attributes = attributes
        self.relationships = relationships

    def get_id(self):
        return self.id

    def get_type(self):
        return self.type


class MetadataDTOBuilder:
    def __init__(self):
        self._id = None
        self._type = "metadata"
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
        return MetadataDTO(self._id, self._type, self._attributes, self._relationships)


class MetadataAttributesDTO:
    def __init__(
        self,
        createdBy="undefined",
        createdOn="undefined",
        bucket="undefined",
        fileIdentifier="undefined",
        fileExtension="undefined",
        resourceExternalURL="undefined",
        dcFormat="undefined",
        dcType="undefined",
        acCaption="undefined",
        acDigitizationDate="undefined",
        xmpMetadataDate="undefined",
        xmpRightsWebStatement="undefined",
        dcRights="undefined",
        xmpRightsOwner="undefined",
        xmpRightsUsageTerms="undefined",
        orientation="undefined",
        originalFilename="undefined",
        acHashFunction="undefined",
        acHashValue="undefined",
        acTags="undefined",
        publiclyReleasable="undefined",
        notPubliclyReleasableReason="undefined",
        acSubtype="undefined",
        managedAttributes={},
        group="undefined",
    ):
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
        self._createdBy = "undefined"
        self._createdOn = "undefined"
        self._bucket = "undefined"
        self._fileIdentifier = "undefined"
        self._fileExtension = "undefined"
        self._resourceExternalURL = "undefined"
        self._dcFormat = "undefined"
        self._dcType = "undefined"
        self._acCaption = "undefined"
        self._acDigitizationDate = "undefined"
        self._xmpMetadataDate = "undefined"
        self._xmpRightsWebStatement = "undefined"
        self._dcRights = "undefined"
        self._xmpRightsOwner = "undefined"
        self._xmpRightsUsageTerms = "undefined"
        self._orientation = "undefined"
        self._originalFilename = "undefined"
        self._acHashFunction = "undefined"
        self._acHashValue = "undefined"
        self._acTags = "undefined"
        self._publiclyReleasable = "undefined"
        self._notPubliclyReleasableReason = "undefined"
        self._acSubtype = "undefined"
        self._group = "undefined"
        self._managedAttributes = "undefined"

    def set_createdBy(self, createdBy):
        self._createdBy = createdBy
        return self

    def set_createdOn(self, createdOn):
        self._createdOn = createdOn
        return self

    def set_bucket(self, bucket):
        self._bucket = bucket
        return self

    def set_fileIdentifier(self, fileIdentifier):
        self._fileIdentifier = fileIdentifier
        return self

    def set_fileExtension(self, fileExtension):
        self._fileExtension = fileExtension
        return self

    def set_resourceExternalURL(self, resourceExternalURL):
        self._resourceExternalURL = resourceExternalURL
        return self

    def set_dcFormat(self, dcFormat):
        self._dcFormat = dcFormat
        return self

    def set_dcType(self, dcType):
        self._dcType = dcType
        return self

    def set_acCaption(self, acCaption):
        self._acCaption = acCaption
        return self

    def set_acDigitizationDate(self, acDigitizationDate):
        self._acDigitizationDate = acDigitizationDate
        return self

    def set_xmpMetadataDate(self, xmpMetadataDate):
        self._xmpMetadataDate = xmpMetadataDate
        return self

    def set_xmpRightsWebStatement(self, xmpRightsWebStatement):
        self._xmpRightsWebStatement = xmpRightsWebStatement
        return self

    def set_dcRights(self, dcRights):
        self._dcRights = dcRights
        return self

    def set_xmpRightsOwner(self, xmpRightsOwner):
        self._xmpRightsOwner = xmpRightsOwner
        return self

    def set_xmpRightsUsageTerms(self, xmpRightsUsageTerms):
        self._xmpRightsUsageTerms = xmpRightsUsageTerms
        return self

    def set_orientation(self, orientation):
        self._orientation = orientation
        return self

    def set_originalFilename(self, originalFilename):
        self._originalFilename = originalFilename
        return self

    def set_acHashFunction(self, acHashFunction):
        self._acHashFunction = acHashFunction
        return self

    def set_acHashValue(self, acHashValue):
        self._acHashValue = acHashValue
        return self

    def set_acTags(self, acTags):
        self._acTags = acTags
        return self

    def set_publiclyReleasable(self, publiclyReleasable):
        self._publiclyReleasable = publiclyReleasable
        return self

    def set_notPubliclyReleasableReason(self, notPubliclyReleasableReason):
        self._notPubliclyReleasableReason = notPubliclyReleasableReason
        return self

    def set_acSubtype(self, acSubtype):
        self._acSubtype = acSubtype
        return self

    def set_group(self, group):
        self._group = group
        return self

    def set_managedAttributes(self, managedAttributes):
        self._managedAttributes = managedAttributes
        return self

    def build(self):
        return MetadataAttributesDTO(
            createdBy=self._createdBy,
            createdOn=self._createdOn,
            bucket=self._bucket,
            fileIdentifier=self._fileIdentifier,
            fileExtension=self._fileExtension,
            resourceExternalURL=self._resourceExternalURL,
            dcFormat=self._dcFormat,
            dcType=self._dcType,
            acCaption=self._acCaption,
            acDigitizationDate=self._acDigitizationDate,
            xmpMetadataDate=self._xmpMetadataDate,
            xmpRightsWebStatement=self._xmpRightsWebStatement,
            dcRights=self._dcRights,
            xmpRightsOwner=self._xmpRightsOwner,
            xmpRightsUsageTerms=self._xmpRightsUsageTerms,
            orientation=self._orientation,
            originalFilename=self._originalFilename,
            acHashFunction=self._acHashFunction,
            acHashValue=self._acHashValue,
            acTags=self._acTags,
            publiclyReleasable=self._publiclyReleasable,
            notPubliclyReleasableReason=self._notPubliclyReleasableReason,
            acSubtype=self._acSubtype,
            managedAttributes=self._managedAttributes,
            group=self._group,
        )
