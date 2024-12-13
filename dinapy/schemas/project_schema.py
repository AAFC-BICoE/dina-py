# This file holds schemas for serializing and deserializing Project entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow import post_load
from marshmallow_jsonapi import Schema, fields
from dinapy.schemas.materialsampleschema import *
from dinapy.entities.Project import ProjectDTO
from .customFields import SkipUndefinedField
from .BaseSchema import *

class Attachment(BaseSchema):
    class Meta:
        type_ = 'attachment'

class ProjectSchema(Schema):
    id = fields.Str(load_only=True)
    createdBy = SkipUndefinedField(fields.Str,attribute="attributes.createdBy")
    createdOn = SkipUndefinedField(fields.DateTime,load_only=True,attribute="attributes.createdOn")
    group = SkipUndefinedField(fields.Str,attribute="attributes.group")
    name = SkipUndefinedField(fields.Str,required=True,attribute="attributes.name")
    startDate = SkipUndefinedField(fields.DateTime,allow_none=True,attribute="attributes.startDate")
    endDate = SkipUndefinedField(fields.DateTime,allow_none=True,attribute="attributes.endDate")
    multilingualDescription = SkipUndefinedField(fields.Str,allow_none=True,attribute="attributes.multilingualDescription")
    extensionValues = SkipUndefinedField(fields.Dict,allow_none=True,attribute="attributes.extensionValues")

    attachment = create_relationship("collecting-event","attachment")

    meta = fields.DocumentMeta()

    class Meta: 
        type_ = "project"
        #self_url = "/api/v1/collecting-event/{id}" or None
        #self_url_kwargs = {"id": "<id>"}
        strict = True

    @post_dump
    def remove_skipped_fields(self, data, many, **kwargs):
        # Remove fields with the special marker value
        return {key: value for key, value in data.items() if value is not SkipUndefinedField(fields.Field).SKIP_MARKER}
	
    @post_dump
    def remove_meta(self, data, many, **kwargs):
        if 'meta' in data:
            del(data['meta'])
        return data
	
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
        return ProjectDTO(**data)

    def dump(self, obj, many=None, *args, **kwargs):
        data = super().dump(obj, many=many, *args, **kwargs)
        if 'meta' in data:
            del data['meta']
        return data
