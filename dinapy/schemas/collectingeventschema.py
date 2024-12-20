# This file holds schemas for serializing and deserializing CollectingEvent entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow import post_load
from marshmallow_jsonapi import Schema, fields
from dinapy.schemas.materialsampleschema import *
from dinapy.entities.CollectingEvent import *
from .customFields import SkipUndefinedField
from .BaseSchema import *

class Protocol(BaseSchema):

	class Meta:
		type_ = 'protocol'

class CollectionMethod(BaseSchema):

	class Meta:
		type_ = 'collection-method'

class Collectors(BaseSchema):

	class Meta:
		type_ = 'collectors'

class Attachment(BaseSchema):

	class Meta:
		type_ = 'attachment'
	
class CollectingEventSchema(Schema):
	'''Schema for a Collecting Event used for serializing and deserializing JSON.'''
	id = fields.Str(load_only=True)
	version = SkipUndefinedField(fields.Int,attribute="attributes.version")
	notPubliclyReleasableReason = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.notPubliclyReleasableReason")
	dwcMaximumDepthInMeters = SkipUndefinedField(fields.Float,allow_none=True, attribute="attributes.dwcMaximumDepthInMeters")
	dwcCountry = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcCountry")
	dwcMinimumElevationInMeters = SkipUndefinedField(fields.Float,allow_none=True, attribute="attributes.dwcMinimumElevationInMeters")
	dwcCountryCode = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcCountryCode")
	dwcFieldNumber = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcFieldNumber")
	dwcRecordNumber = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcRecordNumber")
	dwcVerbatimDepth = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcVerbatimDepth")
	dwcMinimumDepthInMeters = SkipUndefinedField(fields.Float,allow_none=True, attribute="attributes.dwcMinimumDepthInMeters")
	dwcMaximumElevationInMeters = SkipUndefinedField(fields.Float,allow_none=True, attribute="attributes.dwcMaximumElevationInMeters")
	dwcStateProvince = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcStateProvince")
	dwcVerbatimCoordinateSystem = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcVerbatimCoordinateSystem")
	dwcVerbatimElevation = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcVerbatimElevation")
	dwcVerbatimLatitude = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcVerbatimLatitude")
	dwcVerbatimLongitude = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcVerbatimLongitude")
	otherRecordNumbers = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.otherRecordNumbers")
	publiclyReleasable = SkipUndefinedField(fields.Bool,allow_none=True,attribute="attributes.publiclyReleasable")
	group = SkipUndefinedField(fields.Str,attribute="attributes.group")
	createdBy = SkipUndefinedField(fields.Str,attribute="attributes.createdBy")
	createdOn = SkipUndefinedField(fields.DateTime,attribute="attributes.createdOn")
	geoReferenceAssertions = SkipUndefinedField(fields.List,fields.Dict(), allow_none=True, required=False, attribute="attributes.geoReferenceAssertions")
	geographicPlaceNameSource = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.geographicPlaceNameSource")
	geographicPlaceNameSourceDetail = SkipUndefinedField(fields.Str,allow_none=True, attribute= "attributes.geographicPlaceNameSourceDetail")
	habitat = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.habitat")
	eventGeom = SkipUndefinedField(fields.Dict,allow_none=True, attribute="attributes.eventGeom")
	extensionValues = SkipUndefinedField(fields.Dict,allow_none=True, attribute="attributes.extensionValues")
	dwcVerbatimCoordinates = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcVerbatimCoordinates")
	dwcRecordedBy = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcRecordedBy")
	dwcVerbatimSRS = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcVerbatimSRS")
	startEventDateTime = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.startEventDateTime")
	substrate = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.substrate")
	tags = SkipUndefinedField(fields.List,fields.Str(), allow_none=True, required=False, attribute="attributes.tags")
	endEventDateTime = SkipUndefinedField(fields.DateTime,allow_none=True, attribute="attributes.endEventDateTime")
	verbatimEventDateTime = SkipUndefinedField(fields.DateTime,allow_none=True, attribute="attributes.verbatimEventDateTime")
	dwcVerbatimLocality = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcVerbatimLocality")
	host = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.host")
	managedAttributes = SkipUndefinedField(fields.Dict,attribute="attributes.managedAttributes")
	remarks = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.remarks")

	collectionMethod = create_relationship("collecting-event","collection-method","collectionMethod")
	protocol = create_relationship("collecting-event","protocol","protocol")
	collectors = create_relationship("collecting-event","person","collectors")
	attachment = create_relationship("collecting-event","metadata","attachment")

	meta = fields.DocumentMeta()

	class Meta:
		type_ = "collecting-event"
		#self_url = "/api/v1/collecting-event/{id}" or None
		#self_url_kwargs = {"id": "<id>"}
		strict = True

	@post_dump
	def remove_skipped_fields(self, data, many, **kwargs):
		# Remove fields with the special marker value
		return {key: value for key, value in data.items() if value is not SkipUndefinedField(fields.Field).SKIP_MARKER}
	
	@post_dump
	def remove_meta(self, data, many, **kwargs):
		if 'meta' in data:
			del(data['meta'])
		return data
	
	@post_load
	def set_none_to_undefined(self, data, **kwargs):
		for attr in data.attributes:
			if data.attributes[attr] is None:
				data.attributes[attr] = 'undefined'
		return data

	@post_load
	def object_deserialization(self, data, **kwargs):
		if 'meta' in data:
			del data['meta']
		return CollectingEventDTO(**data)

	def dump(self, obj, many=None, *args, **kwargs):
		data = super().dump(obj, many=many, *args, **kwargs)
		if 'meta' in data:
			del data['meta']
		return data

# {
#     "data": {
#         "id": "f08516e5-add2-4baa-89bc-5b8abd0ec8ba",
#         "type": "collecting-event",
#         "links": {
#             "self": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba"
#         },
#         "attributes": {
#             "version": 0,
#             "dwcFieldNumber": null,
#             "dwcRecordNumber": null,
#             "otherRecordNumbers": null,
#             "group": "phillips-lab",
#             "createdBy": "s-seqdbsoil",
#             "createdOn": "2024-01-26T17:09:33.932301Z",
#             "geoReferenceAssertions": [
#                 {
#                     "dwcDecimalLatitude": 44.2,
#                     "dwcDecimalLongitude": -80.7,
#                     "dwcCoordinateUncertaintyInMeters": null,
#                     "createdOn": "2024-01-26T17:09:33.931468083Z",
#                     "dwcGeoreferencedDate": null,
#                     "georeferencedBy": null,
#                     "literalGeoreferencedBy": null,
#                     "dwcGeoreferenceProtocol": null,
#                     "dwcGeoreferenceSources": null,
#                     "dwcGeoreferenceRemarks": null,
#                     "dwcGeodeticDatum": null,
#                     "isPrimary": true,
#                     "dwcGeoreferenceVerificationStatus": null
#                 }
#             ],
#             "eventGeom": {
#                 "type": "Point",
#                 "crs": {
#                     "type": "name",
#                     "properties": {
#                         "name": "EPSG:4326"
#                     }
#                 },
#                 "coordinates": [
#                     -80.7,
#                     44.2
#                 ]
#             },
#             "dwcVerbatimCoordinates": "44.2 -80.7",
#             "dwcRecordedBy": null,
#             "startEventDateTime": "2017-08-07",
#             "endEventDateTime": null,
#             "verbatimEventDateTime": null,
#             "dwcVerbatimLocality": null,
#             "host": null,
#             "managedAttributes": {
#                 "site_codes": "BS",
#                 "cover_crops": "Yes; Annual Ryegrass",
#                 "seq_db_legacy": "{\"Collection Info\":{\"id\":1053400,\"latitude\":\"44.2\",\"longitude\":\"-80.7\",\"year\":\"2017\",\"month\":\"08\",\"day\":\"07\",\"zeroPaddedDate\":\"2017-008-007\",\"notes\":\"Blocks of soil kept intact and on ice until transport back to lab\",\"elevation\":384.0,\"depth\":\"0-0.15\",\"lastModified\":\"2021-02-18T22:57:53.120+00:00\",\"latLon\":\"44.2 -80.7\",\"siteCodes\":\"BS\",\"protocol\":{\"id\":224,\"type\":\"COLLECTION_EVENT\",\"name\":\"Phillips_OMAFRA_SYU_SampleCollectionProtocol.docx\",\"version\":\"\",\"description\":\"\",\"steps\":\"\",\"notes\":\"\",\"reference\":\"\",\"equipment\":\"\",\"forwardPrimerConcentration\":\"\",\"reversePrimerConcentration\":\"\",\"reactionMixVolume\":\"\",\"reactionMixVolumePerTube\":\"\",\"group\":{\"id\":458,\"groupName\":\"GI_Phillips\",\"description\":\"\",\"defaultRead\":false,\"defaultWrite\":false,\"defaultDelete\":false,\"defaultCreate\":false,\"lastModified\":\"2021-01-15T16:25:33.348+00:00\"},\"reactionComponents\":[{\"reactionComponentId\":1016,\"name\":\"\",\"concentration\":\"\",\"lastModified\":\"2021-02-17T18:29:31.605+00:00\",\"id\":1016}],\"lastModified\":\"2021-02-17T18:29:31.479+00:00\"}},\"MIxS Specifications\":{\"id\":783441,\"envPackage\":\"Soil\",\"dnaStorageConditions\":\"neg 80oC; up to 6 months\",\"sampVolWeDnaExt\":\"0.25g\",\"calcium\":\"2440\",\"magnesium\":\"250\",\"orgMatter\":\"4\",\"ph\":7.4,\"potassium\":\"69\",\"sodium\":\"14\",\"waterContent\":\"0.2281041792852818\",\"curLandUse\":\"farmstead\",\"curVegetation\":\"corn\",\"cropRotation\":\"Yes; Corn-Hay/cereal forage\",\"tillage\":\"Conventional\",\"horizon\":\"A horizon\",\"waterContentSoilMeth\":\"Gravimetric\",\"poolDnaExtracts\":\"Yes; 2 x 0.25g\",\"storeCond\":\"6months/-20oC\",\"linkClimateInfo\":\"https://climate.weather.gc.ca/climate_normals/index_e.html\",\"annualSeasonTemp\":\"6.6\",\"linkClassInfo\":\"https://sis.agr.gc.ca/cansis/soils/on/DYK/~~~~~/A/description.html\",\"faoClass\":\"Orthic Gray Brown Luvisol\",\"texture\":\"sandy loam\",\"coverCrops\":\"Yes; Annual Ryegrass\",\"growingDegreeDays\":\"2004.5\",\"cationExchangeCapacity\":\"14.5\",\"availablePhosphorus\":\"25\",\"aggregateStability\":\"-14.528593500000001\",\"lastModified\":\"2021-02-18T22:57:53.123+00:00\"}}",
#                 "available_phosp": "25",
#                 "aggregate_stability": "-14.528593500000001",
#                 "growing_degree_days": "2004.5",
#                 "cation_exchange_capacity": "14.5"
#             },
#             "dwcVerbatimLatitude": "44.2",
#             "dwcVerbatimLongitude": "-80.7",
#             "dwcVerbatimCoordinateSystem": null,
#             "dwcVerbatimSRS": null,
#             "dwcVerbatimElevation": null,
#             "dwcVerbatimDepth": null,
#             "dwcCountry": null,
#             "dwcCountryCode": null,
#             "dwcStateProvince": null,
#             "habitat": null,
#             "dwcMinimumElevationInMeters": 384,
#             "dwcMinimumDepthInMeters": 0,
#             "dwcMaximumElevationInMeters": null,
#             "dwcMaximumDepthInMeters": 0.15,
#             "substrate": "Soil",
#             "remarks": "Blocks of soil kept intact and on ice until transport back to lab",
#             "publiclyReleasable": null,
#             "notPubliclyReleasableReason": null,
#             "tags": null,
#             "geographicPlaceNameSource": null,
#             "geographicPlaceNameSourceDetail": null,
#             "extensionValues": {
#                 "mixs_soil_v4": {
#                     "ph": "7.4",
#                     "horizon": "A horizon",
#                     "texture": "sandy loam",
#                     "tillage": "Conventional",
#                     "fao_class": "Orthic Gray Brown Luvisol",
#                     "store_cond": "6months/-20oC",
#                     "env_package": "Soil",
#                     "cur_land_use": "farmstead",
#                     "crop_rotation": "Yes; Corn-Hay/cereal forage",
#                     "water_content": "0.2281041792852818",
#                     "cur_vegetation": "corn",
#                     "link_class_info": "https://sis.agr.gc.ca/cansis/soils/on/DYK/~~~~~/A/description.html",
#                     "link_climate_info": "https://climate.weather.gc.ca/climate_normals/index_e.html",
#                     "pool_dna_extracts": "Yes; 2 x 0.25g",
#                     "annual_season_temp": "6.6",
#                     "samp_vol_we_dna_ext": "0.25g",
#                     "water_content_soil_meth": "Gravimetric"
#                 },
#                 "mixs_soil_v5": {
#                     "dna_storage_conditons": "neg 80oC; up to 6 months"
#                 },
#                 "mixs_sediment_v4": {
#                     "sodium": "14",
#                     "calcium": "2440",
#                     "magnesium": "250",
#                     "potassium": "69",
#                     "org_matter": "4"
#                 }
#             }
#         },
#         "relationships": {
#             "collectionMethod": {
#                 "links": {
#                     "self": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/relationships/collectionMethod",
#                     "related": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/collectionMethod"
#                 }
#             },
#             "protocol": {
#                 "links": {
#                     "self": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/relationships/protocol",
#                     "related": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/protocol"
#                 }
#             },
#             "collectors": {
#                 "links": {
#                     "self": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/relationships/collectors",
#                     "related": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/collectors"
#                 }
#             },
#             "attachment": {
#                 "links": {
#                     "self": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/relationships/attachment",
#                     "related": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/attachment"
#                 }
#             }
#         }
#     },
#     "meta": {
#         "totalResourceCount": 1,
#         "external": [
#             {
#                 "href": "agent/api/v1/person",
#                 "type": "person"
#             },
#             {
#                 "href": "objectstore/api/v1/metadata",
#                 "type": "metadata"
#             }
#         ],
#         "moduleVersion": "0.84"
#     }
# }