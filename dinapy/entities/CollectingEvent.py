class CollectingEventDTO:
	def __init__(self, id = None, type = 'collecting-event', attributes = None, relationships = 'undefined'):
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
	
class CollectingEventDTOBuilder:
	def __init__(self):
		self._id = None
		self._type = 'collecting-event'
		self._attributes = None
		self._relationships = None

	def attributes(self, attributes):
		self._attributes = attributes.to_dict()
		return self

	def relationships(self, relationships):
		self._relationships = relationships
		return self

	def build(self):
		return CollectingEventDTO(self._id, self._type, self._attributes, self._relationships)


class CollectingEventAttributesDTO:
	def __init__(self, version='undefined', notPubliclyReleasableReason='undefined', dwcMaximumDepthInMeters='undefined', dwcCountry='undefined', dwcMinimumElevationInMeters='undefined', dwcCountryCode='undefined', dwcFieldNumber='undefined', dwcRecordNumber='undefined', dwcVerbatimDepth='undefined', dwcMinimumDepthInMeters='undefined', dwcMaximumElevationInMeters='undefined', dwcStateProvince='undefined', dwcVerbatimCoordinateSystem='undefined', dwcVerbatimElevation='undefined', dwcVerbatimLatitude='undefined', dwcVerbatimLongitude='undefined', otherRecordNumbers='undefined', publiclyReleasable='undefined', group='undefined', createdBy='undefined', createdOn='undefined', geoReferenceAssertions='undefined', geographicPlaceNameSource='undefined', geographicPlaceNameSourceDetail='undefined', geographicThesaurus='undefined', habitat='undefined', eventGeom='undefined', extensionValues='undefined', dwcVerbatimCoordinates='undefined', dwcRecordedBy='undefined', dwcVerbatimSRS='undefined', startEventDateTime='undefined', substrate='undefined', tags='undefined', endEventDateTime='undefined', verbatimEventDateTime='undefined', dwcVerbatimLocality='undefined', host='undefined', managedAttributes={}, remarks='undefined'):
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
		self.geographicThesaurus = geographicThesaurus
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

	def to_dict(self):
		return self.__dict__
	
class CollectingEventAttributesDTOBuilder:
	def __init__(self):
		self._version = 'undefined'
		self._notPubliclyReleasableReason = 'undefined'
		self._dwcMaximumDepthInMeters = 'undefined'
		self._dwcCountry = 'undefined'
		self._dwcMinimumElevationInMeters = 'undefined'
		self._dwcCountryCode = 'undefined'
		self._dwcFieldNumber = 'undefined'
		self._dwcRecordNumber = 'undefined'
		self._dwcVerbatimDepth = 'undefined'
		self._dwcMinimumDepthInMeters = 'undefined'
		self._dwcMaximumElevationInMeters = 'undefined'
		self._dwcStateProvince = 'undefined'
		self._dwcVerbatimCoordinateSystem = 'undefined'
		self._dwcVerbatimElevation = 'undefined'
		self._dwcVerbatimLatitude = 'undefined'
		self._dwcVerbatimLongitude = 'undefined'
		self._otherRecordNumbers = 'undefined'
		self._publiclyReleasable = 'undefined'
		self._group = 'undefined'
		self._createdBy = 'undefined'
		self._createdOn = 'undefined'
		self._geoReferenceAssertions = 'undefined'
		self._geographicPlaceNameSource = 'undefined'
		self._geographicPlaceNameSourceDetail = 'undefined'
		self._geographicThesaurus = 'undefined'
		self._habitat = 'undefined'
		self._eventGeom = 'undefined'
		self._extensionValues = 'undefined'
		self._dwcVerbatimCoordinates = 'undefined'
		self._dwcRecordedBy = 'undefined'
		self._dwcVerbatimSRS = 'undefined'
		self._startEventDateTime = 'undefined'
		self._substrate = 'undefined'
		self._tags = 'undefined'
		self._endEventDateTime = 'undefined'
		self._verbatimEventDateTime = 'undefined'
		self._dwcVerbatimLocality = 'undefined'
		self._host = 'undefined'
		self._managedAttributes = 'undefined'
		self._remarks = 'undefined'
	def version(self, version):
		self._version = version
		return self

	def notPubliclyReleasableReason(self, notPubliclyReleasableReason):
		self._notPubliclyReleasableReason = notPubliclyReleasableReason
		return self

	def dwcMaximumDepthInMeters(self, dwcMaximumDepthInMeters):
		self._dwcMaximumDepthInMeters = dwcMaximumDepthInMeters
		return self

	def dwcCountry(self, dwcCountry):
		self._dwcCountry = dwcCountry
		return self

	def dwcMinimumElevationInMeters(self, dwcMinimumElevationInMeters):
		self._dwcMinimumElevationInMeters = dwcMinimumElevationInMeters
		return self

	def dwcCountryCode(self, dwcCountryCode):
		self._dwcCountryCode = dwcCountryCode
		return self

	def dwcFieldNumber(self, dwcFieldNumber):
		self._dwcFieldNumber = dwcFieldNumber
		return self

	def dwcRecordNumber(self, dwcRecordNumber):
		self._dwcRecordNumber = dwcRecordNumber
		return self

	def dwcVerbatimDepth(self, dwcVerbatimDepth):
		self._dwcVerbatimDepth = dwcVerbatimDepth
		return self

	def dwcMinimumDepthInMeters(self, dwcMinimumDepthInMeters):
		self._dwcMinimumDepthInMeters = dwcMinimumDepthInMeters
		return self

	def dwcMaximumElevationInMeters(self, dwcMaximumElevationInMeters):
		self._dwcMaximumElevationInMeters = dwcMaximumElevationInMeters
		return self

	def dwcStateProvince(self, dwcStateProvince):
		self._dwcStateProvince = dwcStateProvince
		return self

	def dwcVerbatimCoordinateSystem(self, dwcVerbatimCoordinateSystem):
		self._dwcVerbatimCoordinateSystem = dwcVerbatimCoordinateSystem
		return self

	def dwcVerbatimElevation(self, dwcVerbatimElevation):
		self._dwcVerbatimElevation = dwcVerbatimElevation
		return self

	def dwcVerbatimLatitude(self, dwcVerbatimLatitude):
		self._dwcVerbatimLatitude = dwcVerbatimLatitude
		return self

	def dwcVerbatimLongitude(self, dwcVerbatimLongitude):
		self._dwcVerbatimLongitude = dwcVerbatimLongitude
		return self

	def otherRecordNumbers(self, otherRecordNumbers):
		self._otherRecordNumbers = otherRecordNumbers
		return self

	def publiclyReleasable(self, publiclyReleasable):
		self._publiclyReleasable = publiclyReleasable
		return self

	def group(self, group):
		self._group = group
		return self

	def createdBy(self, createdBy):
		self._createdBy = createdBy
		return self

	def createdOn(self, createdOn):
		self._createdOn = createdOn
		return self

	def geoReferenceAssertions(self, geoReferenceAssertions):
		self._geoReferenceAssertions = geoReferenceAssertions
		return self

	def geographicPlaceNameSource(self, geographicPlaceNameSource):
		self._geographicPlaceNameSource = geographicPlaceNameSource
		return self

	def geographicPlaceNameSourceDetail(self, geographicPlaceNameSourceDetail):
		self._geographicPlaceNameSourceDetail = geographicPlaceNameSourceDetail
		return self

	def geographicThesaurus(self, geographicThesaurus):
		self._geographicThesaurus = geographicThesaurus
		return self
	
	def habitat(self, habitat):
		self._habitat = habitat
		return self

	def eventGeom(self, eventGeom):
		self._eventGeom = eventGeom
		return self

	def extensionValues(self, extensionValues):
		self._extensionValues = extensionValues
		return self

	def dwcVerbatimCoordinates(self, dwcVerbatimCoordinates):
		self._dwcVerbatimCoordinates = dwcVerbatimCoordinates
		return self

	def dwcRecordedBy(self, dwcRecordedBy):
		self._dwcRecordedBy = dwcRecordedBy
		return self

	def dwcVerbatimSRS(self, dwcVerbatimSRS):
		self._dwcVerbatimSRS = dwcVerbatimSRS
		return self

	def startEventDateTime(self, startEventDateTime):
		self._startEventDateTime = startEventDateTime
		return self

	def substrate(self, substrate):
		self._substrate = substrate
		return self

	def tags(self, tags):
		self._tags = tags
		return self

	def endEventDateTime(self, endEventDateTime):
		self._endEventDateTime = endEventDateTime
		return self

	def verbatimEventDateTime(self, verbatimEventDateTime):
		self._verbatimEventDateTime = verbatimEventDateTime
		return self

	def dwcVerbatimLocality(self, dwcVerbatimLocality):
		self._dwcVerbatimLocality = dwcVerbatimLocality
		return self

	def host(self, host):
		self._host = host
		return self

	def managedAttributes(self, managedAttributes):
		self._managedAttributes = managedAttributes
		return self

	def remarks(self, remarks):
		self._remarks = remarks
		return self

	def build(self):
		return CollectingEventAttributesDTO(
			self._version,
			self._notPubliclyReleasableReason,
			self._dwcMaximumDepthInMeters,
			self._dwcCountry,
			self._dwcMinimumElevationInMeters,
			self._dwcCountryCode,
			self._dwcFieldNumber,
			self._dwcRecordNumber,
			self._dwcVerbatimDepth,
			self._dwcMinimumDepthInMeters,
			self._dwcMaximumElevationInMeters,
			self._dwcStateProvince,
			self._dwcVerbatimCoordinateSystem,
			self._dwcVerbatimElevation,
			self._dwcVerbatimLatitude,
			self._dwcVerbatimLongitude,
			self._otherRecordNumbers,
			self._publiclyReleasable,
			self._group,
			self._createdBy,
			self._createdOn,
			self._geoReferenceAssertions,
			self._geographicPlaceNameSource,
			self._geographicPlaceNameSourceDetail,
			self._geographicThesaurus,
			self._habitat,
			self._eventGeom,
			self._extensionValues,
			self._dwcVerbatimCoordinates,
			self._dwcRecordedBy,
			self._dwcVerbatimSRS,
			self._startEventDateTime,
			self._substrate,
			self._tags,
			self._endEventDateTime,
			self._verbatimEventDateTime,
			self._dwcVerbatimLocality,
			self._host,
			self._managedAttributes,
			self._remarks
		)

