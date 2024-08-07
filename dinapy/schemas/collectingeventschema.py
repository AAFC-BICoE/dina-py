# This file holds schemas for serializing and deserializing CollectingEvent entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow import post_load
from marshmallow_jsonapi import Schema, fields
from dinapy.schemas.materialsampleschema import *
from dinapy.entities.CollectingEvent import *
class Protocol(Schema):
	id = fields.Str(dump_only=True, allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'protocol'

class CollectingEventSchema(Schema):
	'''Schema for a Collecting Event used for serializing and deserializing JSON.'''
	id = fields.Str(load_only=True)
	version = fields.Int(attribute="attributes.version")
	notPubliclyReleasableReason = fields.Str(allow_none=True, attribute="attributes.notPubliclyReleasableReason")
	dwcMaximumDepthInMeters = fields.Float(allow_none=True, attribute="attributes.dwcMaximumDepthInMeters")
	dwcCountry = fields.Str(allow_none=True, attribute="attributes.dwcCountry")
	dwcMinimumElevationInMeters = fields.Float(allow_none=True, attribute="attributes.dwcMinimumElevationInMeters")
	dwcCountryCode = fields.Str(allow_none=True, attribute="attributes.dwcCountryCode")
	dwcFieldNumber = fields.Str(allow_none=True, attribute="attributes.dwcFieldNumber")
	dwcRecordNumber = fields.Str(allow_none=True, attribute="attributes.dwcRecordNumber")
	dwcVerbatimDepth = fields.Str(allow_none=True, attribute="attributes.dwcVerbatimDepth")
	dwcMinimumDepthInMeters = fields.Float(allow_none=True, attribute="attributes.dwcMinimumDepthInMeters")
	dwcMaximumElevationInMeters = fields.Float(allow_none=True, attribute="attributes.dwcMaximumElevationInMeters")
	dwcStateProvince = fields.Str(allow_none=True, attribute="attributes.dwcStateProvince")
	dwcVerbatimCoordinateSystem = fields.Str(allow_none=True, attribute="attributes.dwcVerbatimCoordinateSystem")
	dwcVerbatimElevation = fields.Str(allow_none=True, attribute="attributes.dwcVerbatimElevation")
	dwcVerbatimLatitude = fields.Str(allow_none=True, attribute="attributes.dwcVerbatimLatitude")
	dwcVerbatimLongitude = fields.Str(allow_none=True, attribute="attributes.dwcVerbatimLongitude")
	otherRecordNumbers = fields.Str(allow_none=True, attribute="attributes.otherRecordNumbers")
	publiclyReleasable = fields.Str(allow_none=True,attribute="attributes.publiclyReleasable")
	group = fields.Str(attribute="attributes.group")
	createdBy = fields.Str(attribute="attributes.createdBy")
	createdOn = fields.DateTime(attribute="attributes.createdOn")
	geoReferenceAssertions = fields.List(fields.Dict(), allow_none=True, required=False, attribute="attributes.geoReferenceAssertions")
	geographicPlaceNameSource = fields.Str(allow_none=True, attribute="attributes.geographicPlaceNameSource")
	geographicPlaceNameSourceDetail = fields.Str(allow_none=True, attribute= "attributes.geographicPlaceNameSourceDetail")
	habitat = fields.Str(allow_none=True, attribute="attributes.habitat")
	eventGeom = fields.Dict(allow_none=True, attribute="attributes.eventGeom")
	extensionValues = fields.Dict(allow_none=True, attribute="attributes.extensionValues")
	dwcVerbatimCoordinates = fields.Str(allow_none=True, attribute="attributes.dwcVerbatimCoordinates")
	dwcRecordedBy = fields.Str(allow_none=True, attribute="attributes.dwcRecordedBy")
	dwcVerbatimSRS = fields.Str(allow_none=True, attribute="attributes.dwcVerbatimSRS")
	startEventDateTime = fields.Str(allow_none=True, attribute="attributes.startEventDateTime")
	substrate = fields.Str(allow_none=True, attribute="attributes.substrate")
	tags = fields.List(fields.Str(), allow_none=True, required=False, attribute="attributes.tags")
	endEventDateTime = fields.DateTime(allow_none=True, attribute="attributes.endEventDateTime")
	verbatimEventDateTime = fields.DateTime(allow_none=True, attribute="attributes.verbatimEventDateTime")
	dwcVerbatimLocality = fields.Str(allow_none=True, attribute="attributes.dwcVerbatimLocality")
	host = fields.Str(allow_none=True, attribute="attributes.host")
	managedAttributes = fields.Dict(attribute="attributes.managedAttributes")
	remarks = fields.Str(allow_none=True, attribute="attributes.remarks")

	collectionMethod = fields.Relationship(
	self_url="/api/v1/collecting-event/{id}/relationships/collectionMethod",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/collecting-event/{id}/collectionMethod",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.collectionMethod",    
	type_="collection-method",
	)

	protocol = fields.Relationship(
	self_url="/api/v1/collecting-event/{id}/relationships/protocol",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/collecting-event/{id}/protocol",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.protocol",        
	type_="protocol",
	)

	collectors = fields.Relationship(
	self_url="/api/v1/collecting-event/{id}/relationships/collectors",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/collecting-event/{id}/collectors",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.collectors",
	type_="collectors",
	)

	attachment = fields.Relationship(
	self_url="/api/v1/collecting-event/{id}/relationships/attachment",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/collecting-event/{id}/attachment",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.attachment",	
	type_="attachment",
	)

	meta = fields.DocumentMeta()
		
	class Meta:
		type_ = "collecting-event"
		#self_url = "/api/v1/collecting-event/{id}" or None
		#self_url_kwargs = {"id": "<id>"}
		strict = True
		
	@post_dump
	def remove_skip_values(self, data, **kwargs):
		return {
			key: value for key, value in data.items()
			if value is not None
		}

	def load(self, data, many=None, partial=None):
		if 'relationships' in data['data']:
			for relationship_name, relationship_data in data['data']['relationships'].items():
				if 'data' not in relationship_data:
					# Handle missing data for the relationship
					relationship_data['data'] = None  # Or set to appropriate default
		return super().load(data)
	
	@post_load
	def remove_none_values(self, data, **kwargs):
		def clean_dict(d):
			if not isinstance(d, dict):
				return d
			cleaned = {k: clean_dict(v) for k, v in d.items() if v is not None}
			return cleaned if cleaned else None

		return clean_dict(data)
	
	@post_load
	def object_deserialization(self, data, **kwargs):
		if 'meta' in data:
			del data['meta']
		return CollectingEventDTO(**data)
		
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