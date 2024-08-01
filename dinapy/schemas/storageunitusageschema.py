# This file holds schemas for serializing and deserializing StorageUnitUsage entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields

class StorageUnitTypeSchema(Schema):
	id = fields.Str(dump_only=True)
	type = fields.Str()
	
	class Meta:
		type_ = 'storage-unit-type'

class StorageUnitSchema(Schema):
	id = fields.Str(dump_only=True)
	type = fields.Str()
	
	class Meta:
		type_ = 'storage-unit'
	
class StorageUnitUsage(Schema):
	id = fields.Str(load_only=True)
	usageType = fields.Str()
	wellRow = fields.Str(required=True)
	wellColumn = fields.Int(required=True)
	cellNumber = fields.Int(dump_only=False, required=True,allow_none=True)
	storageUnitName = fields.Str(required=True,allow_none=True)
	createdOn = fields.Str(dump_only=False, required=True)
	createdBy = fields.Str(dump_only=False, required=True)

	storageUnit = fields.Relationship(
		self_url="/api/v1/storage-unit-usage/{id}/relationships/storageUnit",
		self_url_kwargs={"id": "<id>"},
		related_url="/api/v1/storage-unit-usage/{id}/storageUnit",
		related_url_kwargs={"id": "<id>"},
		include_resource_linkage=True,
		attribute="relationships.storageUnit",
		type_="storage-unit"
	)

	storageUnitType = fields.Relationship(
		self_url="/api/v1/storage-unit-usage/{id}/relationships/storageUnitType",
		self_url_kwargs={"id": "<id>"},
		related_url="/api/v1/storage-unit-usage/{id}/storageUnitType",
		related_url_kwargs={"id": "<id>"},
		include_resource_linkage=True,
		attribute="relationships.storageUnitType",
		type_="storage-unit-type"
	)

	
	class Meta:
		type_ = 'storage-unit-usage'
