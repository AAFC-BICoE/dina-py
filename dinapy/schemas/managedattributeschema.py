from marshmallow import post_load, post_dump
from marshmallow_jsonapi import Schema, fields
from .customFields import SkipUndefinedField
from dinapy.entities.ManagedAttribute import ManagedAttributesDTO
from .multilingualDescription import MultilingualDescriptionSchema

class ManagedAttributesSchema(Schema):
    id = fields.Str(load_only=True)
    name = SkipUndefinedField(fields.Str, attribute="attributes.name")
    key = SkipUndefinedField(fields.Str, attribute="attributes.key")
    vocabularyElementType = SkipUndefinedField(fields.Str, attribute="attributes.vocabularyElementType")
    unit = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.unit")
    managedAttributeComponent = SkipUndefinedField(fields.Str, attribute="attributes.managedAttributeComponent")
    acceptedValues = SkipUndefinedField(fields.List, fields.Raw(), allow_none=True, attribute="attributes.acceptedValues")
    createdOn = SkipUndefinedField(fields.DateTime, allow_none=True, attribute="attributes.createdOn")
    createdBy = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.createdBy")
    group = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.group")
    multilingualDescription = SkipUndefinedField(
        fields.Nested, MultilingualDescriptionSchema, allow_none=True, attribute="attributes.multilingualDescription"
    )

    meta = fields.DocumentMeta()

    class Meta:
        type_ = "managed-attribute"
        strict = False

    @post_dump
    def remove_skipped_fields(self, data, many, **kwargs):
        return {key: value for key, value in data.items() if value is not SkipUndefinedField(fields.Field).SKIP_MARKER}

    @post_dump
    def remove_meta(self, data, many, **kwargs):
        if 'meta' in data:
            del data['meta']
        return data

    @post_load
    def set_none_to_undefined(self, data, **kwargs):
        if hasattr(data, 'attributes'):
            for attr in data.attributes:
                if data.attributes[attr] is None:
                    data.attributes[attr] = 'undefined'
        return data

    @post_load
    def object_deserialization(self, data, **kwargs):
        if 'meta' in data:
            del data['meta']
        return ManagedAttributesDTO(**data)

    def dump(self, obj, many=None, *args, **kwargs):
        data = super().dump(obj, many=many, *args, **kwargs)
        if 'meta' in data:
            del data['meta']
        return data
