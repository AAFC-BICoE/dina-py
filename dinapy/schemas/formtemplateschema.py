# This file holds schemas for serializing and deserializing FormTemplate entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields
from marshmallow import post_load,post_dump

from dinapy.entities.FormTemplate import FormTemplateDTO
from .customFields import SkipUndefinedField
from .BaseSchema import *

class FormTemplate(Schema):
	id = fields.Str(load_only=True)

	createdOn = SkipUndefinedField(fields.DateTime, load_only=True, attribute="attributes.createdOn")
	createdBy = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.createdBy")
	group = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.group")
	name = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.name")
	restrictToCreatedBy = SkipUndefinedField(fields.Bool, load_only=True, attribute="attributes.restrictToCreatedBy")
	viewConfiguration = SkipUndefinedField(fields.Dict, load_only=True, attribute="attributes.viewConfiguration")
	components = SkipUndefinedField(fields.Dict, load_only=True, attribute="attributes.components")

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
		return FormTemplateDTO(**data)
	
	meta = fields.DocumentMeta()

	class Meta:
		type_ = 'form-template'
