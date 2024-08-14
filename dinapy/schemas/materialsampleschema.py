# This file holds schemas for serializing and deserializing Material Sample entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields
from marshmallow import post_dump,post_load,pre_dump

from dinapy.entities.MaterialSample import MaterialSampleDTO
from .customFields import SkipUndefinedField
from .BaseSchema import *

class CollectingEvent(BaseSchema):
	class Meta:
		type_ = 'collecting-event'
class Organism(BaseSchema):
	class Meta:
		type_ = 'organism'

class Assemblages(BaseSchema):
	class Meta:
		type_ = 'assemblages'

class Projects(BaseSchema):
	class Meta:
		type_ = 'projects'

class PreparationProtocol(BaseSchema):
	class Meta:
		type_ = 'preparation-protocol'

class Attachment(BaseSchema):
	class Meta:
		type_ = 'attachment'

class PreparedBy(BaseSchema):
	class Meta:
		type_ = 'prepared-by'

class ParentMaterialSample(BaseSchema):	
	class Meta:
		type_ = 'parent-material-sample'

class PreparationMethod(BaseSchema):	
	class Meta:
		type_ = 'preparation-method'

class PreparationType(BaseSchema):
	class Meta:
		type_ = 'preparation-type'

class Collection(BaseSchema):
	class Meta:
		type_ = 'collection'
		
class StorageUnit(BaseSchema):
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
	materialSampleName = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.materialSampleName")
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
	publiclyReleasable = SkipUndefinedField(fields.Bool, allow_none=True, attribute="attributes.publiclyReleasable")
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
		return {key: value for key, value in data.items() if value is not SkipUndefinedField(fields.Field).SKIP_MARKER}
	
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
	
	collection = create_relationship("collection")
	collectingEvent = create_relationship("collectingEvent")
	preparationType = create_relationship("preparationType")
	preparationMethod = create_relationship("preparationMethod")
	parentMaterialSample = create_relationship("parentMaterialSample")
	preparedBy = create_relationship("preparedBy")
	attachment = create_relationship("attachment")
	preparationProtocol = create_relationship("preparationProtocol")
	projects = create_relationship("projects")
	assemblages = create_relationship("assemblages")
	organism = create_relationship("organism")
	storageUnit = create_relationship("storageUnit")
	
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