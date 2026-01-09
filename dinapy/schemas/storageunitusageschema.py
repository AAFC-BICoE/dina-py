# This file holds schemas for serializing and deserializing StorageUnitUsage entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields
from marshmallow import post_load,pre_load,post_dump,ValidationError

from dinapy.entities.StorageUnitUsage import StorageUnitUsageDTO
from .customFields import SkipUndefinedField
from .BaseSchema import *
	
class StorageUnitTypeSchema(BaseSchema):
	name = SkipUndefinedField(fields.Str,attribute="attributes.name")
	createdOn = SkipUndefinedField(fields.DateTime, load_only=True,attribute="attributes.createdOn")
	createdBy = SkipUndefinedField(fields.Str, load_only=True,attribute="attributes.createdBy")
	group = SkipUndefinedField(fields.Str, required=True,attribute="attributes.grroup")
	isInseparable = SkipUndefinedField(fields.Boolean, required=True,attribute="attributes.isInseparable")
	gridLayoutDefinition = SkipUndefinedField(fields.Dict, required=True,attribute="attributes.gridLayoutDefinition")

	class Meta:
		type_ = 'storage-unit-type'

class StorageUnitSchema(BaseSchema):
	name = SkipUndefinedField(fields.Str,attribute="attributes.name")
	createdOn = SkipUndefinedField(fields.DateTime, load_only=True,attribute="attributes.createdOn")
	createdBy = SkipUndefinedField(fields.Str, load_only=True,attribute="attributes.createdBy")
	group = SkipUndefinedField(fields.Str, required=True,attribute="attributes.group")
	isGeneric = SkipUndefinedField(fields.Boolean, required=True,attribute="attributes.isGeneric")
	barcode = SkipUndefinedField(fields.Str,attribute="attributes.barcode")
	storageUnitChildren = SkipUndefinedField(fields.Dict,attribute="attributes.storageUnitChildren")

	parentStorageUnit = create_relationship("storage-unit","storage-unit","storageUnit")
	storageUnitType = create_relationship("storage-unit","storage-unit-type","storageUnitType")
	
	class Meta:
		type_ = 'storage-unit'
	
class StorageUnitUsage(Schema):
	id = fields.Str(load_only=True)
	usageType = SkipUndefinedField(fields.Str,attribute="attributes.usageType")
	wellRow = SkipUndefinedField(fields.Str,required=True,attribute="attributes.wellRow")
	wellColumn = SkipUndefinedField(fields.Int,required=True,attribute="attributes.wellColumn")
	cellNumber = SkipUndefinedField(fields.Int, load_only=True,attribute="attributes.cellNumber")
	storageUnitName = SkipUndefinedField(fields.Str, required=True,attribute="attributes.storageUnitName")
	createdOn = SkipUndefinedField(fields.DateTime, load_only=True,attribute="attributes.createdOn")
	createdBy = SkipUndefinedField(fields.Str, load_only=True,attribute="attributes.createdBy")

	storageUnit = create_relationship("storage-unit-usage","storage-unit","storageUnit")
	storageUnitType = create_relationship("storage-unit-usage","storage-unit-type","storageUnitType")
	
	@post_load
	def set_none_to_undefined(self, data, **kwargs):
		for attr in data.attributes:
			if data.attributes[attr] is None:
				data.attributes[attr] = 'undefined'
		return data
	
	@post_dump
	def remove_skipped_fields(self, data, many, **kwargs):
		# Remove fields with the special marker value
		return {key: value for key, value in data.items() if value is not SkipUndefinedField(fields.Field).SKIP_MARKER}

	@post_load
	def object_deserialization(self, data, **kwargs):
		if 'meta' in data:
			del data['meta']
		return StorageUnitUsageDTO(**data)
	
	meta = fields.DocumentMeta()

	class Meta:
		type_ = 'storage-unit-usage'

	# {
	# 	"data": {
	# 		"id": "01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe",
	# 		"type": "storage-unit-usage",
	# 		"links": {
	# 			"self": "/api/v1/storage-unit-usage/01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe"
	# 		},
	# 		"attributes": {
	# 			"wellColumn": 1,
	# 			"wellRow": "A",
	# 			"usageType": "material-sample",
	# 			"cellNumber": 1,
	# 			"storageUnitName": "Nazir-test",
	# 			"createdOn": "2024-06-18T21:24:12.320912Z",
	# 			"createdBy": "elkayssin"
	# 		},
	# 		"relationships": {
	# 			"storageUnitType": {
	# 				"links": {
	# 					"self": "/api/v1/storage-unit-usage/01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe/relationships/storageUnitType",
	# 					"related": "/api/v1/storage-unit-usage/01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe/storageUnitType"
	# 				}
	# 			},
	# 			"storageUnit": {
	# 				"links": {
	# 					"self": "/api/v1/storage-unit-usage/01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe/relationships/storageUnit",
	# 					"related": "/api/v1/storage-unit-usage/01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe/storageUnit"
	# 				}
	# 			}
	# 		}
	# 	},
	# 	"meta": {
	# 		"totalResourceCount": 1,
	# 		"moduleVersion": "0.91"
	# 	}
	# }