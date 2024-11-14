# This file holds schemas for serializing and deserializing MolecularAnalysisRunItem entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields
from marshmallow import post_load,pre_load,post_dump,ValidationError

from dinapy.entities.MolecularAnalysisRunItem import MolecularAnalysisRunItemDTO
from .customFields import SkipUndefinedField
from .BaseSchema import *

class MolecularAnalysisRunSchema(BaseSchema):
    class Meta:
        type_ = 'molecular-analysis-run'

class MolecularAnalysisResultSchema(BaseSchema):
    class Meta:
        type_ = 'molecular-analysis-result'

class MolecularAnalysisRunItemSchema(Schema):
    id = fields.Str(load_only=True)
    createdBy = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.createdBy")
    createdOn = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.createdOn")

    run = create_relationship("molecular-analysis-run-item", "run")
    result = create_relationship("molecular-analysis-run-item", "result")

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
        return MolecularAnalysisRunItemDTO(**data)
	
    meta = fields.DocumentMeta()

    class Meta:
        type_ = 'molecular-analysis-run-item'
    