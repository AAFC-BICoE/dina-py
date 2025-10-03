from marshmallow import post_load, post_dump
from marshmallow_jsonapi import Schema, fields
from .customFields import SkipUndefinedField
from dinapy.entities.Person import PersonDTO

class PersonSchema(Schema):
    '''Schema for a Person used for serializing and deserializing JSON.'''
    id = fields.Str(allow_none=True)
    personMeta = SkipUndefinedField(fields.Dict, allow_none=True, attribute="attributes.meta",data_key="meta")
    displayName = SkipUndefinedField(fields.Str, required=True, attribute="attributes.displayName")
    email = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.email")
    createdBy = SkipUndefinedField(fields.Str, load_only=True, attribute="attributes.createdBy")
    createdOn = SkipUndefinedField(fields.DateTime, load_only=True, attribute="attributes.createdOn")
    givenNames = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.givenNames")
    familyNames = SkipUndefinedField(fields.Str, required=True, attribute="attributes.familyNames")
    aliases = SkipUndefinedField(fields.List, fields.Str(), allow_none=True, required=False, attribute="attributes.aliases")
    webpage = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.webpage")
    remarks = SkipUndefinedField(fields.Str, allow_none=True, attribute="attributes.remarks")
    
    identifiers = fields.Relationship(
        self_url="/api/v1/person/{id}/relationships/identifiers",
        self_url_kwargs={"id": "<id>"},
        related_url="/api/v1/person/{id}/identifiers",
        related_url_kwargs={"id": "<id>"},
        many=True,
        type_="identifiers",
    )
    
    organizations = fields.Relationship(
        self_url="/api/v1/person/{id}/relationships/organizations",
        self_url_kwargs={"id": "<id>"},
        related_url="/api/v1/person/{id}/organizations",
        related_url_kwargs={"id": "<id>"},
        many=True,
        type_="organizations",
    )

    meta = fields.DocumentMeta()
    
    class Meta:
        type_ = "person"
        self_url = "/api/v1/person/{id}"
        self_url_kwargs = {"id": "<id>"}
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
        return PersonDTO(**data)

    def dump(self, obj, many=None, *args, **kwargs):
        data = super().dump(obj, many=many, *args, **kwargs)
        if 'meta' in data:
            del data['meta']
        return data