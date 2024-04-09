class CollectingEventDTO:
    def __init__(self, id = None, type = "collecting-event", attributes = None, relationships = None):
        self.id = id
        self.type = type
        self.attributes = attributes or {}
        self.relationships = relationships or {}

class CollectingEventDTOBuilder:
    def __init__(self):
        self.collecting_event = CollectingEventDTO(
            id=None,
            type="collecting-event",
            attributes=None,
            relationships=None
        )

    def set_attributes(self, attributes):
        self.collecting_event.attributes = attributes
        return self

    def set_relationships(self, relationships):
        self.collecting_event.relationships = relationships
        return self

    def build(self):
        return self.collecting_event

class CollectingEventAttributesDTO:
    def __init__(self, version=None, notPubliclyReleasableReason=None, dwcMaximumDepthInMeters=None, dwcCountry=None, dwcMinimumElevationInMeters=None, dwcCountryCode=None, dwcFieldNumber=None, dwcRecordNumber=None, dwcVerbatimDepth=None, dwcMinimumDepthInMeters=None, dwcMaximumElevationInMeters=None, dwcStateProvince=None, dwcVerbatimCoordinateSystem=None, dwcVerbatimElevation=None, dwcVerbatimLatitude=None, dwcVerbatimLongitude=None, otherRecordNumbers=None, publiclyReleasable=None, group=None, createdBy=None, createdOn=None, geoReferenceAssertions=None, geographicPlaceNameSource=None, geographicPlaceNameSourceDetail=None, habitat=None, eventGeom=None, extensionValues=None, dwcVerbatimCoordinates=None, dwcRecordedBy=None, dwcVerbatimSRS=None, startEventDateTime=None, substrate=None, tags=None, endEventDateTime=None, verbatimEventDateTime=None, dwcVerbatimLocality=None, host=None, managedAttributes={}, remarks=None):
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

    def set_version(self, version):
        self.dto.version = version
        return self

    def set_notPubliclyReleasableReason(self, notPubliclyReleasableReason):
        self.dto.notPubliclyReleasableReason = notPubliclyReleasableReason
        return self

    def set_dwcMaximumDepthInMeters(self, dwcMaximumDepthInMeters):
        self.dto.dwcMaximumDepthInMeters = dwcMaximumDepthInMeters
        return self

    def set_dwcCountry(self, dwcCountry):
        self.dto.dwcCountry = dwcCountry
        return self

    def set_dwcMinimumElevationInMeters(self, dwcMinimumElevationInMeters):
        self.dto.dwcMinimumElevationInMeters = dwcMinimumElevationInMeters
        return self

    def set_dwcCountryCode(self, dwcCountryCode):
        self.dto.dwcCountryCode = dwcCountryCode
        return self

    def set_dwcFieldNumber(self, dwcFieldNumber):
        self.dto.dwcFieldNumber = dwcFieldNumber
        return self

    def set_dwcRecordNumber(self, dwcRecordNumber):
        self.dto.dwcRecordNumber = dwcRecordNumber
        return self

    def set_dwcVerbatimDepth(self, dwcVerbatimDepth):
        self.dto.dwcVerbatimDepth = dwcVerbatimDepth
        return self

    def set_dwcMinimumDepthInMeters(self, dwcMinimumDepthInMeters):
        self.dto.dwcMinimumDepthInMeters = dwcMinimumDepthInMeters
        return self

    def set_dwcMaximumElevationInMeters(self, dwcMaximumElevationInMeters):
        self.dto.dwcMaximumElevationInMeters = dwcMaximumElevationInMeters
        return self

    def set_dwcStateProvince(self, dwcStateProvince):
        self.dto.dwcStateProvince = dwcStateProvince
        return self

    def set_dwcVerbatimCoordinateSystem(self, dwcVerbatimCoordinateSystem):
        self.dto.dwcVerbatimCoordinateSystem = dwcVerbatimCoordinateSystem
        return self

    def set_dwcVerbatimElevation(self, dwcVerbatimElevation):
        self.dto.dwcVerbatimElevation = dwcVerbatimElevation
        return self

    def set_dwcVerbatimLatitude(self, dwcVerbatimLatitude):
        self.dto.dwcVerbatimLatitude = dwcVerbatimLatitude
        return self

    def set_dwcVerbatimLongitude(self, dwcVerbatimLongitude):
        self.dto.dwcVerbatimLongitude = dwcVerbatimLongitude
        return self

    def set_otherRecordNumbers(self, otherRecordNumbers):
        self.dto.otherRecordNumbers = otherRecordNumbers
        return self

    def set_publiclyReleasable(self, publiclyReleasable):
        self.dto.publiclyReleasable = publiclyReleasable
        return self

    def set_group(self, group):
        self.dto.group = group
        return self

    def set_createdBy(self, createdBy):
        self.dto.createdBy = createdBy
        return self

    def set_createdOn(self, createdOn):
        self.dto.createdOn = createdOn
        return self

    def set_geoReferenceAssertions(self, geoReferenceAssertions):
        self.dto.geoReferenceAssertions = geoReferenceAssertions
        return self

    def set_geographicPlaceNameSource(self, geographicPlaceNameSource):
        self.dto.geographicPlaceNameSource = geographicPlaceNameSource
        return self

    def set_geographicPlaceNameSourceDetail(self, geographicPlaceNameSourceDetail):
        self.dto.geographicPlaceNameSourceDetail = geographicPlaceNameSourceDetail
        return self

    def set_habitat(self, habitat):
        self.dto.habitat = habitat
        return self

    def set_eventGeom(self, eventGeom):
        self.dto.eventGeom = eventGeom
        return self

    def set_extensionValues(self, extensionValues):
        self.dto.extensionValues = extensionValues
        return self

    def set_dwcVerbatimCoordinates(self, dwcVerbatimCoordinates):
        self.dto.dwcVerbatimCoordinates = dwcVerbatimCoordinates
        return self

    def set_dwcRecordedBy(self, dwcRecordedBy):
        self.dto.dwcRecordedBy = dwcRecordedBy
        return self

    def set_dwcVerbatimSRS(self, dwcVerbatimSRS):
        self.dto.dwcVerbatimSRS = dwcVerbatimSRS
        return self

    def set_startEventDateTime(self, startEventDateTime):
        self.dto.startEventDateTime = startEventDateTime
        return self

    def set_substrate(self, substrate):
        self.dto.substrate = substrate
        return self

    def set_tags(self, tags):
        self.dto.tags = tags
        return self

    def set_endEventDateTime(self, endEventDateTime):
        self.dto.endEventDateTime = endEventDateTime
        return self

    def set_verbatimEventDateTime(self, verbatimEventDateTime):
        self.dto.verbatimEventDateTime = verbatimEventDateTime
        return self

    def set_dwcVerbatimLocality(self, dwcVerbatimLocality):
        self.dto.dwcVerbatimLocality = dwcVerbatimLocality
        return self

    def set_host(self, host):
        self.dto.host = host
        return self

    def set_managedAttributes(self, managedAttributes):
        self.dto.managedAttributes = managedAttributes
        return self

    def set_remarks(self, remarks):
        self.dto.remarks = remarks
        return self

    def build(self):
        return self.dto

