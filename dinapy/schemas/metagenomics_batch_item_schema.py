# This file holds schemas for serializing and deserializing MetagenomicsBatchItem entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields
from marshmallow import post_load,pre_load,post_dump,ValidationError

from dinapy.entities.MetagenomicsBatchItem import MetagenomicsBatchItemDTO
from .customFields import SkipUndefinedField
from .BaseSchema import *

class MetagenimicsBatchSchema(BaseSchema):
    class Meta:
        type_ = 'metagenomics-batch'

class PcrBatchItemSchema(BaseSchema):
    class Meta:
        type_ = 'pcr-batch-item'

class MolecularAnalysisRunItemSchema(BaseSchema):
    class Meta:
        type_ = 'molecular-analysis-run-item'

class NgsIndexSchema(BaseSchema):
    class Meta:
        type_ = 'ngs-index'

class MetagenomicsBatchSchema(Schema):
    id = fields.Str(load_only=True)
    createdBy = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.createdBy")
    createdOn = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.createdOn")

    metagenomicsBatch = create_relationship("metagenomics-batch-item", "metgenomics-batch", "metgenomicsBatch")
    pcrBatchItem = create_relationship("metgenomics-batch-item", "pcr-batch-item", "pcrBatchItem")
    molecularAnalysisRunItem = create_relationship("metagenomics-batch-item", "molecular-analysis-run-item", "molecularAnalysisRunItem")
    indexI5 = create_relationship("metagenomics-batch-item", "ngs-idnex", "indexI5")
    indexI7 = create_relationship("metagenomics-batch-item", "ngs-idnex", "indexI7")

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
        return MetagenomicsBatchItemDTO(**data)
	
    meta = fields.DocumentMeta()

    class Meta:
        type_ = 'metagenomics-batch-item'