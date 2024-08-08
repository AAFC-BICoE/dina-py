# This file holds schemas for serializing and deserializing Material Sample entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields
from marshmallow import post_dump,post_load,pre_dump
import os
import sys

from dinapy.entities.MaterialSample import MaterialSampleDTO
from .customFields import SkipUndefinedField

class CollectingEvent(Schema):
	id = fields.Str(dump_only=True,allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'collecting-event'
class Organism(Schema):
	id = fields.Str(dump_only=True, allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'organism'

class Assemblages(Schema):
	id = fields.Str(dump_only=True, allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'assemblages'

class Projects(Schema):
	id = fields.Str(dump_only=True, allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'projects'

class PreparationProtocol(Schema):
	id = fields.Str(dump_only=True, allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'preparation-protocol'

class Attachment(Schema):
	id = fields.Str(dump_only=True, allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'attachment'

class PreparedBy(Schema):
	id = fields.Str(dump_only=True, allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'prepared-by'

class ParentMaterialSample(Schema):
	id = fields.Str(dump_only=True, allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'parent-material-sample'

class PreparationMethod(Schema):
	id = fields.Str(dump_only=True, allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'preparation-method'

class PreparationType(Schema):
	id = fields.Str(dump_only=True, allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'preparation-type'

class Collection(Schema):
	id = fields.Str(dump_only=True, allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'collection'
		
class StorageUnit(Schema):
	id = fields.Str(dump_only=True,allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'storage-unit'
			
class MaterialSampleSchema(Schema):
	'''Schema for a Material Sample used for serializing and deserializing JSON.'''
	id = fields.Str(load_only=True)
	version = SkipUndefinedField(fields.Int,allow_none=True, attribute="attributes.version")
	group = SkipUndefinedField(fields.Str,required=True, attribute="attributes.group")
	createdOn = SkipUndefinedField(fields.DateTime,load_only=True, attribute="attributes.createdOn")
	createdBy = SkipUndefinedField(fields.Str,load_only=True, attribute="attributes.createdBy")
	dwcCatalogNumber = SkipUndefinedField(fields.Str,allow_none=True, attribute="attributes.dwcCatalogNumber")
	dwcOtherCatalogNumbers = SkipUndefinedField(fields.List,fields.Str,allow_none=True, attribute="attributes.dwcOtherCatalogNumbers")
	materialSampleName = SkipUndefinedField(fields.Str, attribute="attributes.materialSampleName")
	materialSampleType = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.materialSampleType")
	materialSampleChildren = SkipUndefinedField(fields.List, fields.Str, allow_none=True, attribute="attributes.materialSampleChildren")
	preparationDate = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.preparationDate")
	preservationType = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.preservationType")
	preparationFixative = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.preparationFixative")
	preparationMaterials = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.preparationMaterials")
	preparationSubstrate = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.preparationSubstrate")
	managedAttributes = SkipUndefinedField(fields.Dict, required=False, attribute="attributes.managedAttributes")
	preparationManagedAttributes = SkipUndefinedField(fields.Dict, attribute="attributes.preparationManagedAttributes")
	extensionValues = SkipUndefinedField(fields.Dict, allow_none=True, attribute="attributes.extensionValues")
	preparationRemarks = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.preparationRemarks")
	dwcDegreeOfEstablishment = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.dwcDegreeOfEstablishment")
	barcode = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.barcode")
	publiclyReleasable = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.publiclyReleasable")
	notPubliclyReleasableReason = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.notPubliclyReleasableReason")
	tags = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.tags")
	materialSampleState = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.materialSampleState")
	materialSampleRemarks = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.materialSampleRemarks")
	stateChangedOn = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.stateChangedOn")
	stateChangeRemarks = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.stateChangeRemarks")
	associations = SkipUndefinedField(fields.List,fields.Str, allow_none=True, attribute="attributes.associations")
	allowDuplicateName = SkipUndefinedField(fields.Bool, required=True, attribute="attributes.allowDuplicateName")
	restrictionFieldsExtension = SkipUndefinedField(fields.Dict, allow_none=True, attribute="attributes.restrictionFieldsExtension")
	isRestricted = SkipUndefinedField(fields.Bool, required=True, attribute="attributes.isRestricted")
	restrictionRemarks = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.restrictionRemarks")
	sourceSet = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.sourceSet")

	@post_dump
	def remove_skipped_fields(self, data, many, **kwargs):
		# Remove fields with the special marker value
		skip_marker = SkipUndefinedField(fields.Field).SKIP_MARKER

		return {key: value for key, value in data.items() if value}
	
	# def load(self, data, many=None, partial=None):
	# 	if 'relationships' in data['data']:
	# 		for relationship_name, relationship_data in data['data']['relationships'].items():
	# 			if 'data' not in relationship_data:
	# 				del(data['data']['relationships'][relationship_name])
	# 				# Handle missing data for the relationship
	# 				# relationship_data['data'] = None  # Or set to appropriate default
	# 	return super().load(data)
	

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
		return MaterialSampleDTO(**data)
	
	collection = fields.Relationship(
	self_url="/api/v1/material-sample/{id}/relationships/collection",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/material-sample/{id}/collection",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.collection",
	type_="collection"
	)
	  
	collectingEvent = fields.Relationship(
	self_url="/api/v1/material-sample/{id}/relationships/collectingEvent",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/material-sample/{id}/collectingEvent",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.collectingEvent",
	type_="collecting-event"
	)

	preparationType = fields.Relationship(
	self_url="/api/v1/material-sample/{id}/relationships/preparationType",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/material-sample/{id}/preparationType",
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.preparationType",
	type_="preparation-type",
	)

	preparationMethod = fields.Relationship(
	self_url="/api/v1/material-sample/{id}/relationships/preparationMethod",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/material-sample/{id}/preparationMethod",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.preparationMethod",
	type_="preparation-method",
	)

	parentMaterialSample = fields.Relationship(
	self_url="/api/v1/material-sample/{id}/relationships/parentMaterialSample",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/material-sample/{id}/parentMaterialSample",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.parentMaterialSample",
	type_="parent-material-sample",
	)

	preparedBy = fields.Relationship(
	self_url="/api/v1/material-sample/{id}/relationships/preparedBy",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/material-sample/{id}/preparedBy",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.preparedBy",
	type_="prepared-by",
	)

	attachment = fields.Relationship(
	self_url="/api/v1/material-sample/{id}/relationships/attachment",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/material-sample/{id}/attachment",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.attachment",
	type_="attachment",
	)

	preparationProtocol = fields.Relationship(
	self_url="/api/v1/material-sample/{id}/relationships/preparationProtocol",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/material-sample/{id}/preparationProtocol",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.preparationProtocol",
	type_="preparation-protocol",
	)

	projects = fields.Relationship(
	self_url="/api/v1/material-sample/{id}/relationships/projects",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/material-sample/{id}/projects",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.projects",
	type_="projects",
	)

	assemblages = fields.Relationship(
	self_url="/api/v1/material-sample/{id}/relationships/assemblages",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/material-sample/{id}/assemblages",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.assemblages",
	type_="assemblages",
	)

	organism = fields.Relationship(
	self_url="/api/v1/material-sample/{id}/relationships/organism",
	self_url_kwargs={"id": "<id>"},
	related_url="/api/v1/material-sample/{id}/organism",
	related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.organism",
	type_="organism",
	)

	storageUnit = fields.Relationship(
	# self_url="/api/v1/material-sample/{id}/relationships/storageUnit",
	# self_url_kwargs={"id": "<id>"},
	# related_url="/api/v1/material-sample/{id}/storageUnit",
	# related_url_kwargs={"id": "<id>"},
	allow_none=True,
	include_resource_linkage=True,
	attribute="relationships.storageUnit",
	type_="storage-unit",
	)

	meta = fields.DocumentMeta()
	
	class Meta:
		type_ = "material-sample"

		
# GET response for MaterialSample
# {
#     "data": {
#         "id": "182ed68e-7536-4ad4-868c-399c8e5d70f3",
#         "type": "material-sample",
#         "links": {
#             "self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3"
#         },
#         "attributes": {
#             "version": 1,
#             "group": "phillips-lab",
#             "createdOn": "2024-03-07T16:35:26.865646Z",
#             "createdBy": "s-seqdbsoil",
#             "dwcCatalogNumber": null,
#             "dwcOtherCatalogNumbers": [
#                 "HCC_31"
#             ],
#             "materialSampleName": "HCC-2018-05-16-HCC_31",
#             "materialSampleType": "MIXED_ORGANISMS",
#             "materialSampleChildren": [],
#             "preparationDate": null,
#             "preservationType": null,
#             "preparationFixative": null,
#             "preparationMaterials": null,
#             "preparationSubstrate": null,
#             "managedAttributes": {
#                 "treatment": "HCC_31",
#                 "pretreatment": "Yes; air dried 1 month/No; kept frozen",
#                 "date_archived": "43175",
#                 "seq_db_legacy": "{\"Mixed Specimen\":{\"id\":9229,\"mixedSpecimenNumber\":\"HCC-2018-05-16-HCC_31\",\"otherIds\":\"HCC_31\",\"replicateInfo\":\"Randomized Complete Block Design; 4 experimental replicates\",\"substrateType\":\"Soil\",\"notes\":\"Conventional; Control\",\"researchStudyNotes\":\"Replicated field trial; Grid/ Randomized 'W' pattern across plot; Temporal sampling\",\"treatment\":\"HCC_31\",\"project\":\"\",\"dateArchived\":\"43175\",\"sampleStorageLocation\":\"AAFC Harrow\",\"sampleStorageConditions\":\"Dry/-80oC\",\"amountAvailable\":\"200-300g/10g\",\"pretreatment\":\"Yes; air dried 1 month/No; kept frozen\",\"alternativeContactInfo\":\"Brent Seuradge\",\"collectionInfo\":{\"id\":1053625,\"zeroPaddedDate\":\"\",\"latLon\":\"\"},\"mixsSpecification\":{\"id\":783666},\"group\":{\"id\":458,\"defaultRead\":false,\"defaultWrite\":false,\"defaultDelete\":false,\"defaultCreate\":false},\"biologicalCollection\":{\"id\":433,\"nagoyaRestricted\":false,\"uniqueId\":433},\"lastModified\":\"2021-03-05T00:56:08.407+00:00\"}}",
#                 "amount_available": "200-300g/10g",
#                 "research_study_notes": "Replicated field trial; Grid/ Randomized 'W' pattern across plot; Temporal sampling",
#                 "sample_storage_location": "AAFC Harrow",
#                 "alternative_contact_info": "Brent Seuradge",
#                 "sample_storage_conditions": "Dry/-80oC"
#             },
#             "preparationManagedAttributes": {},
#             "extensionValues": {},
#             "preparationRemarks": "Randomized Complete Block Design; 4 experimental replicates",
#             "dwcDegreeOfEstablishment": null,
#             "barcode": null,
#             "publiclyReleasable": null,
#             "notPubliclyReleasableReason": null,
#             "tags": null,
#             "materialSampleState": null,
#             "materialSampleRemarks": "Conventional; Control",
#             "stateChangedOn": null,
#             "stateChangeRemarks": null,
#             "associations": [],
#             "allowDuplicateName": false,
#             "restrictionFieldsExtension": {},
#             "isRestricted": false,
#             "restrictionRemarks": null,
#             "sourceSet": null
#         },
#         "relationships": {
#             "parentMaterialSample": {
#                 "links": {
#                     "self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/parentMaterialSample",
#                     "related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/parentMaterialSample"
#                 }
#             },
#             "collectingEvent": {
#                 "links": {
#                     "self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/collectingEvent",
#                     "related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/collectingEvent"
#                 }
#             },
#             "preparationMethod": {
#                 "links": {
#                     "self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparationMethod",
#                     "related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparationMethod"
#                 }
#             },
#             "storageUnit": {
#                 "links": {
#                     "self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/storageUnit",
#                     "related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/storageUnit"
#                 }
#             },
#             "projects": {
#                 "links": {
#                     "self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/projects",
#                     "related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/projects"
#                 }
#             },
#             "preparedBy": {
#                 "links": {
#                     "self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparedBy",
#                     "related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparedBy"
#                 }
#             },
#             "organism": {
#                 "links": {
#                     "self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/organism",
#                     "related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/organism"
#                 }
#             },
#             "attachment": {
#                 "links": {
#                     "self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/attachment",
#                     "related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/attachment"
#                 }
#             },
#             "collection": {
#                 "links": {
#                     "self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/collection",
#                     "related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/collection"
#                 }
#             },
#             "preparationProtocol": {
#                 "links": {
#                     "self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparationProtocol",
#                     "related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparationProtocol"
#                 }
#             },
#             "preparationType": {
#                 "links": {
#                     "self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparationType",
#                     "related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparationType"
#                 }
#             },
#             "assemblages": {
#                 "links": {
#                     "self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/assemblages",
#                     "related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/assemblages"
#                 }
#             }
#         }
#     },
#     "meta": {
#         "totalResourceCount": 1,
#         "external": [
#             {
#                 "type": "person",
#                 "href": "agent/api/v1/person"
#             },
#             {
#                 "type": "metadata",
#                 "href": "objectstore/api/v1/metadata"
#             }
#         ],
#         "moduleVersion": "0.84"
#     }
# }