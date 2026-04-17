# This file holds schemas for serializing and deserializing Site entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields
from marshmallow import post_dump, post_load, pre_dump

from dinapy.entities.Site import SiteDTO
from .customFields import SkipUndefinedField
from .BaseSchema import *

class Attachment(BaseSchema):
	class Meta:
		type_ = 'attachment'

class SiteSchema(Schema):
	'''Schema for a Site used for serializing and deserializing JSON.'''
	id = fields.Str(load_only=True)
	createdOn = SkipUndefinedField(fields.DateTime, load_only=True, attribute="attributes.createdOn")
	createdBy = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.createdBy")
	group = SkipUndefinedField(fields.Str, required=True, attribute="attributes.group")
	name = SkipUndefinedField(fields.Str, required=True, attribute="attributes.name")
	code = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.code")
	siteGeom = SkipUndefinedField(fields.Dict, allow_none=True, attribute="attributes.siteGeom")
	multilingualDescription = SkipUndefinedField(fields.Dict, allow_none=True, attribute="attributes.multilingualDescription")

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
		return SiteDTO(**data)
	
	attachment = create_relationship("site", "metadata", "attachment", many=True)

	meta = fields.DocumentMeta()
	
	class Meta:
		type_ = "site"