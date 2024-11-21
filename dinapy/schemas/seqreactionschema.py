# This file holds schemas for serializing and deserializing SeqReaction entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields
from marshmallow import post_load,pre_load,post_dump,ValidationError

from dinapy.entities.SeqReaction import SeqReactionDTO
from .customFields import SkipUndefinedField
from .BaseSchema import *

class SeqBatchSchema(BaseSchema):
    class Meta:
        type_ = 'seq-batch'

class PcrBatchItemSchema(BaseSchema):
    class Meta:
        type_ = 'pcr-batch-item'

class PcrPrimerSchema(BaseSchema):
    class Meta:
        type_ = 'pcr-primer'

class MolecularAnalysisRunItemSchema(BaseSchema):
    class Meta:
        type_ = 'molecular-analysis-run-item'

class StorageUnitUsageSchema(BaseSchema):
    class Meta:
        type_ = 'storage-unit-usage'

class SeqReactionSchema(Schema):
    id = fields.Str(load_only=True)
    createdBy = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.createdBy")
    createdOn = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.createdOn")
    group = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.group")

    seqBatch = create_relationship("seq-reaction", "seq-batch")
    pcrBatchItem = create_relationship("seq-reaction", "pcr-batch-item")
    pcrPrimer = create_relationship("seq-reaction", "pcr-primer")
    molecularAnalysisRunItem = create_relationship("seq-reaction", "molecular-analysis-run-item")
    storageUnitUsage = create_relationship("seq-reaction", "storage-unit-usage")

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
        return SeqReactionDTO(**data)
	
    meta = fields.DocumentMeta()

    class Meta:
        type_ = 'seq-reaction'