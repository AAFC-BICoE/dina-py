# This file holds schemas for serializing and deserializing SplitConfiguration entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields
from marshmallow import post_load,pre_load,post_dump,ValidationError

from enum import Enum
from dinapy.entities.SplitConfiguration import SplitConfigurationDTO
from .customFields import SkipUndefinedField
from .validateEnums import ValidateEnums
from .BaseSchema import *

class Strategy(Enum):
		TYPE_BASED = 'TYPE_BASED'
		DIRECT_PARENT = 'DIRECT_PARENT'

class CharacterType(Enum):
		NUMBER = 'NUMBER'
		LOWER_LETTER = 'LOWER_LETTER'
		UPPER_LETTER = 'UPPER_LETTER'

class Separator(Enum):
		DASH = 'DASH'
		UNDERSCORE = 'UNDERSCORE'
		SPACE = 'SPACE'

class SplitConfigurationSchema(Schema):
	id = fields.Str(load_only=True)

	createdOn = SkipUndefinedField(fields.DateTime, load_only=True, attribute="attributes.createdOn")
	createdBy = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.createdBy")
	group = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.group")
	name = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.name")
	strategy = SkipUndefinedField(fields.Str, validate=ValidateEnums(Strategy), load_only=True, attribute="attributes.strategy")
	conditionalOnMaterialSampleTypes = SkipUndefinedField(fields.List, fields.Str(), load_only=True, attribute="attributes.conditionalOnMaterialSampleTypes")
	characterType = SkipUndefinedField(fields.Str, validate=ValidateEnums(CharacterType), load_only=True, attribute="attributes.characterType")
	separator = SkipUndefinedField(fields.Str, validate=ValidateEnums(Separator), load_only=True, attribute="attributes.separator")
	materialSampleTypeCreatedBySplit = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.materialSampleTypeCreatedBySplit")

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
