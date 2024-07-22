class CollectingEventDTO:
    def __init__(
        self, id=None, type="collecting-event", attributes=None, relationships=None
    ):
        self.id = id
        self.type = type
        self.attributes = attributes or {}
        self.relationships = relationships or {}


class CollectingEventDTOBuilder:
    def __init__(self):
        self.collecting_event = CollectingEventDTO(
            id=None, type="collecting-event", attributes=None, relationships=None
        )

    def attributes(self, attributes):
        self.collecting_event.attributes = attributes
        return self

    def relationships(self, relationships):
        self.collecting_event.relationships = relationships
        return self

    def build(self):
        return self.collecting_event


class CollectingEventAttributesDTO:
    def __init__(
        self,
        version=None,
        notPubliclyReleasableReason=None,
        dwcMaximumDepthInMeters=None,
        dwcCountry=None,
        dwcMinimumElevationInMeters=None,
        dwcCountryCode=None,
        dwcFieldNumber=None,
        dwcRecordNumber=None,
        dwcVerbatimDepth=None,
        dwcMinimumDepthInMeters=None,
        dwcMaximumElevationInMeters=None,
        dwcStateProvince=None,
        dwcVerbatimCoordinateSystem=None,
        dwcVerbatimElevation=None,
        dwcVerbatimLatitude=None,
        dwcVerbatimLongitude=None,
        otherRecordNumbers=None,
        publiclyReleasable=None,
        group=None,
        createdBy=None,
        createdOn=None,
        geoReferenceAssertions=None,
        geographicPlaceNameSource=None,
        geographicPlaceNameSourceDetail=None,
        habitat=None,
        eventGeom=None,
        extensionValues=None,
        dwcVerbatimCoordinates=None,
        dwcRecordedBy=None,
        dwcVerbatimSRS=None,
        startEventDateTime=None,
        substrate=None,
        tags=None,
        endEventDateTime=None,
        verbatimEventDateTime=None,
        dwcVerbatimLocality=None,
        host=None,
        managedAttributes={},
        remarks=None,
    ):
        self.version = version
        self.notPubliclyReleasableReason = notPubliclyReleasableReason
        self.dwcMaximumDepthInMeters = dwcMaximumDepthInMeters
        self.dwcCountry = dwcCountry
        self.dwcMinimumElevationInMeters = dwcMinimumElevationInMeters
        self.dwcCountryCode = dwcCountryCode
        self.dwcFieldNumber = dwcFieldNumber
        self.dwcRecordNumber = dwcRecordNumber
        self.dwcVerbatimDepth = dwcVerbatimDepth
        self.dwcMinimumDepthInMeters = dwcMinimumDepthInMeters
        self.dwcMaximumElevationInMeters = dwcMaximumElevationInMeters
        self.dwcStateProvince = dwcStateProvince
        self.dwcVerbatimCoordinateSystem = dwcVerbatimCoordinateSystem
        self.dwcVerbatimElevation = dwcVerbatimElevation
        self.dwcVerbatimLatitude = dwcVerbatimLatitude
        self.dwcVerbatimLongitude = dwcVerbatimLongitude
        self.otherRecordNumbers = otherRecordNumbers
        self.publiclyReleasable = publiclyReleasable
        self.group = group
        self.createdBy = createdBy
        self.createdOn = createdOn
        self.geoReferenceAssertions = geoReferenceAssertions
        self.geographicPlaceNameSource = geographicPlaceNameSource
        self.geographicPlaceNameSourceDetail = geographicPlaceNameSourceDetail
        self.habitat = habitat
        self.eventGeom = eventGeom
        self.extensionValues = extensionValues
        self.dwcVerbatimCoordinates = dwcVerbatimCoordinates
        self.dwcRecordedBy = dwcRecordedBy
        self.dwcVerbatimSRS = dwcVerbatimSRS
        self.startEventDateTime = startEventDateTime
        self.substrate = substrate
        self.tags = tags
        self.endEventDateTime = endEventDateTime
        self.verbatimEventDateTime = verbatimEventDateTime
        self.dwcVerbatimLocality = dwcVerbatimLocality
        self.host = host
        self.managedAttributes = managedAttributes
        self.remarks = remarks


class CollectingEventAttributesDTOBuilder:
    def __init__(self):
        self.dto = CollectingEventAttributesDTO()

    def version(self, version):
        self.dto.version = version
        return self

    def notPubliclyReleasableReason(self, notPubliclyReleasableReason):
        self.dto.notPubliclyReleasableReason = notPubliclyReleasableReason
        return self

    def dwcMaximumDepthInMeters(self, dwcMaximumDepthInMeters):
        self.dto.dwcMaximumDepthInMeters = dwcMaximumDepthInMeters
        return self

    def dwcCountry(self, dwcCountry):
        self.dto.dwcCountry = dwcCountry
        return self

    def dwcMinimumElevationInMeters(self, dwcMinimumElevationInMeters):
        self.dto.dwcMinimumElevationInMeters = dwcMinimumElevationInMeters
        return self

    def dwcCountryCode(self, dwcCountryCode):
        self.dto.dwcCountryCode = dwcCountryCode
        return self

    def dwcFieldNumber(self, dwcFieldNumber):
        self.dto.dwcFieldNumber = dwcFieldNumber
        return self

    def dwcRecordNumber(self, dwcRecordNumber):
        self.dto.dwcRecordNumber = dwcRecordNumber
        return self

    def dwcVerbatimDepth(self, dwcVerbatimDepth):
        self.dto.dwcVerbatimDepth = dwcVerbatimDepth
        return self

    def dwcMinimumDepthInMeters(self, dwcMinimumDepthInMeters):
        self.dto.dwcMinimumDepthInMeters = dwcMinimumDepthInMeters
        return self

    def dwcMaximumElevationInMeters(self, dwcMaximumElevationInMeters):
        self.dto.dwcMaximumElevationInMeters = dwcMaximumElevationInMeters
        return self

    def dwcStateProvince(self, dwcStateProvince):
        self.dto.dwcStateProvince = dwcStateProvince
        return self

    def dwcVerbatimCoordinateSystem(self, dwcVerbatimCoordinateSystem):
        self.dto.dwcVerbatimCoordinateSystem = dwcVerbatimCoordinateSystem
        return self

    def dwcVerbatimElevation(self, dwcVerbatimElevation):
        self.dto.dwcVerbatimElevation = dwcVerbatimElevation
        return self

    def dwcVerbatimLatitude(self, dwcVerbatimLatitude):
        self.dto.dwcVerbatimLatitude = dwcVerbatimLatitude
        return self

    def dwcVerbatimLongitude(self, dwcVerbatimLongitude):
        self.dto.dwcVerbatimLongitude = dwcVerbatimLongitude
        return self

    def otherRecordNumbers(self, otherRecordNumbers):
        self.dto.otherRecordNumbers = otherRecordNumbers
        return self

    def publiclyReleasable(self, publiclyReleasable):
        self.dto.publiclyReleasable = publiclyReleasable
        return self

    def group(self, group):
        self.dto.group = group
        return self

    def createdBy(self, createdBy):
        self.dto.createdBy = createdBy
        return self

    def createdOn(self, createdOn):
        self.dto.createdOn = createdOn
        return self

    def geoReferenceAssertions(self, geoReferenceAssertions):
        self.dto.geoReferenceAssertions = geoReferenceAssertions
        return self

    def geographicPlaceNameSource(self, geographicPlaceNameSource):
        self.dto.geographicPlaceNameSource = geographicPlaceNameSource
        return self

    def geographicPlaceNameSourceDetail(self, geographicPlaceNameSourceDetail):
        self.dto.geographicPlaceNameSourceDetail = geographicPlaceNameSourceDetail
        return self

    def habitat(self, habitat):
        self.dto.habitat = habitat
        return self

    def eventGeom(self, eventGeom):
        self.dto.eventGeom = eventGeom
        return self

    def extensionValues(self, extensionValues):
        self.dto.extensionValues = extensionValues
        return self

    def dwcVerbatimCoordinates(self, dwcVerbatimCoordinates):
        self.dto.dwcVerbatimCoordinates = dwcVerbatimCoordinates
        return self

    def dwcRecordedBy(self, dwcRecordedBy):
        self.dto.dwcRecordedBy = dwcRecordedBy
        return self

    def dwcVerbatimSRS(self, dwcVerbatimSRS):
        self.dto.dwcVerbatimSRS = dwcVerbatimSRS
        return self

    def startEventDateTime(self, startEventDateTime):
        self.dto.startEventDateTime = startEventDateTime
        return self

    def substrate(self, substrate):
        self.dto.substrate = substrate
        return self

    def tags(self, tags):
        self.dto.tags = tags
        return self

    def endEventDateTime(self, endEventDateTime):
        self.dto.endEventDateTime = endEventDateTime
        return self

    def verbatimEventDateTime(self, verbatimEventDateTime):
        self.dto.verbatimEventDateTime = verbatimEventDateTime
        return self

    def dwcVerbatimLocality(self, dwcVerbatimLocality):
        self.dto.dwcVerbatimLocality = dwcVerbatimLocality
        return self

    def host(self, host):
        self.dto.host = host
        return self

    def managedAttributes(self, managedAttributes):
        self.dto.managedAttributes = managedAttributes
        return self

    def remarks(self, remarks):
        self.dto.remarks = remarks
        return self

    def build(self):
        return self.dto
