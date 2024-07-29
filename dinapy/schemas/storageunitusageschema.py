# This file holds schemas for serializing and deserializing Person entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields
from marshmallow import pre_dump

from dinapy.schemas.custom_schema_fields import Relationship

class StorageUnitUsage(Schema):
	'''Schema for a Person used for serializing and deserializing JSON.'''
	id = fields.Str(dump_only=False)
	usageType = fields.Str(attribute="attributes.usageType")
	wellRow = fields.Str(required=True, attribute="attributes.wellRow")
	wellColumn = fields.Int(required=True, attribute="attributes.wellColumn")
	cellNumber = fields.Int(dump_only=False, required=True,allow_none=True, attribute="attributes.cellNumber")
	storageUnitName = fields.Str(required=True,allow_none=True, attribute="attributes.storageUnitName")
	createdOn = fields.Str(dump_only=False, required=True,allow_none=True, attribute="attributes.createdOn")
	createdBy = fields.Str(dump_only=False, required=True,allow_none=True, attribute="attributes.createdBy")

	storageUnit = Relationship(attribute="relationships.storageUnit", allow_none=True)
	storageUnitType = Relationship(attribute="relationships.storageUnitType", allow_none=True)

	meta = fields.DocumentMeta()
	
	class Meta:
		type_ = "storage-unit-usage"
		strict = True

	@pre_dump
	def prepare_relationships(self, obj, many, **kwargs):
		if hasattr(obj, 'relationships'):
			obj.relationships = {
				"storageUnit": obj.relationships.get("storageUnit"),
				"storageUnitType": obj.relationships.get("storageUnitType")
			}
		return obj