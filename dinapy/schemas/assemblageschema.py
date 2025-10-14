from marshmallow import post_load, post_dump
from marshmallow_jsonapi import Schema, fields
from .customFields import SkipUndefinedField
from dinapy.entities.Assemblage import AssemblageDTO
from dinapy.schemas.multilingualDescription import MultilingualDescriptionSchema
from dinapy.schemas.multilingualtitleschema import MultilingualTitleSchema

class AssemblageSchema(Schema):
    '''Schema for an Assemblage used for serializing and deserializing JSON.'''
    id = fields.Str(allow_none=True)
    createdBy = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.createdBy")
    group = SkipUndefinedField(fields.Str, attribute="attributes.group")
    createdOn = SkipUndefinedField(fields.DateTime, load_only=True, attribute="attributes.createdOn")
    name = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.name")
    managedAttributes = SkipUndefinedField(fields.Dict, required=False, attribute="attributes.managedAttributes")
    multilingualTitle = SkipUndefinedField(
        fields.Nested, MultilingualTitleSchema, allow_none=True, attribute="attributes.multilingualTitle"
    )
    multilingualDescription = SkipUndefinedField(
        fields.Nested, MultilingualDescriptionSchema, allow_none=True, attribute="attributes.multilingualDescription"
    )
    familyNames = SkipUndefinedField(fields.Str, required=True, attribute="attributes.familyNames")
    aliases = SkipUndefinedField(fields.List, fields.Str(), allow_none=True, required=False, attribute="attributes.aliases")
    webpage = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.webpage")
    remarks = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.remarks")
    
    attachments = fields.Relationship(
        self_url="/api/v1/assemblage/{id}/relationships/attachments",
        self_url_kwargs={"id": "<id>"},
        related_url="/api/v1/assemblage/{id}/attachments",
        related_url_kwargs={"id": "<id>"},
        many=True,
        type_="attachments",
    )
    
    meta = fields.DocumentMeta()
    
    class Meta:
        type_ = "assemblage"
        strict = True

    @post_dump
    def remove_skipped_fields(self, data, many, **kwargs):
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
        return AssemblageDTO(**data)

    def dump(self, obj, many=None, *args, **kwargs):
        data = super().dump(obj, many=many, *args, **kwargs)
        if 'meta' in data:
            del data['meta']
        return data