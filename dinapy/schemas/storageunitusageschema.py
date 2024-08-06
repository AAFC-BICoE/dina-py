# This file holds schemas for serializing and deserializing StorageUnitUsage entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields
from marshmallow import post_load,pre_load

from dinapy.entities.StorageUnitUsage import StorageUnitUsageDTO

class StorageUnitTypeSchema(Schema):
	id = fields.Str(dump_only=True,allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'storage-unit-type'

class StorageUnitSchema(Schema):
	id = fields.Str(dump_only=True,allow_none=True)
	type = fields.Str(allow_none=True)
	
	class Meta:
		type_ = 'storage-unit'
	
class StorageUnitUsage(Schema):
	id = fields.Str(load_only=True)
	usageType = fields.Str(required=True,attribute="attributes.usageType")
	wellRow = fields.Str(required=True,attribute="attributes.wellRow")
	wellColumn = fields.Int(required=True,attribute="attributes.wellColumn")
	cellNumber = fields.Int(load_only=True,attribute="attributes.cellNumber")
	storageUnitName = fields.Str(required=True,attribute="attributes.storageUnitName")
	createdOn = fields.DateTime(load_only=True,attribute="attributes.createdOn")
	createdBy = fields.Str(load_only=True,attribute="attributes.createdBy")

	storageUnit = fields.Relationship(
		self_url="/api/v1/storage-unit-usage/{id}/relationships/storageUnit",
		self_url_kwargs={"id": "<id>"},
		related_url="/api/v1/storage-unit-usage/{id}/storageUnit",
		related_url_kwargs={"id": "<id>"},
		allow_none=True,
		include_resource_linkage=True,
		attribute="relationships.storageUnit",
		type_="storage-unit"
	)

	storageUnitType = fields.Relationship(
		self_url="/api/v1/storage-unit-usage/{id}/relationships/storageUnitType",
		self_url_kwargs={"id": "<id>"},
		related_url="/api/v1/storage-unit-usage/{id}/storageUnitType",
		related_url_kwargs={"id": "<id>"},
		allow_none=True,
		include_resource_linkage=True,
		attribute="relationships.storageUnitType",
		type_="storage-unit-type"
	)

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