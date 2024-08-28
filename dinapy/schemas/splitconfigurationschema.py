# This file holds schemas for serializing and deserializing SplitConfiguration entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields
from marshmallow import post_load,post_dump

from dinapy.entities.SplitConfiguration import SplitConfigurationDTO
from .customFields import SkipUndefinedField
from .BaseSchema import *

class SplitConfigurationSchema(Schema):
	id = fields.Str(load_only=True)

	createdBy = SkipUndefinedField(fields.Str, attribute="attributes.createdBy")
	createdOn = SkipUndefinedField(fields.DateTime, attribute="attributes.createdOn")
	group = SkipUndefinedField(fields.Str, attribute="attributes.group")
	name = SkipUndefinedField(fields.Str, attribute="attributes.name")
	strategy = SkipUndefinedField(fields.Str, attribute="attributes.strategy")
	conditionalOnMaterialSampleTypes = SkipUndefinedField(fields.List, fields.Str(), allow_none=True, required=False, attribute="attributes.conditionalOnMaterialSampleTypes")
	characterType = SkipUndefinedField(fields.Str, attribute="attributes.characterType")
	separator = SkipUndefinedField(fields.Str, attribute="attributes.separator")
	materialSampleTypeCreatedBySplit = SkipUndefinedField(fields.Str, attribute="attributes.materialSampleTypeCreatedBySplit")

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
		return SplitConfigurationDTO(**data)
	
	meta = fields.DocumentMeta()

	class Meta:
		type_ = 'split-configuration'

# {
#   "data": {
#     "id": "01918f0d-4261-770d-8fce-e240799cceb8",
#     "type": "split-configuration",
#     "attributes": {
#       "createdOn": "2024-08-26T14:18:17.030325Z",
#       "createdBy": "dina-admin",
#       "group": "aafc",
#       "name": "test-split-configuration",
#       "strategy": "DIRECT_PARENT",
#       "conditionalOnMaterialSampleTypes": ["WHOLE_ORGANISM"],
#       "characterType": "LOWER_LETTER",
#       "separator": "SPACE",
#       "materialSampleTypeCreatedBySplit": "WHOLE_ORGANISM"
#     }
#   },
#   "meta": {
#     "totalResourceCount": 1,
#     "moduleVersion": "0.94"
#   }
# }
