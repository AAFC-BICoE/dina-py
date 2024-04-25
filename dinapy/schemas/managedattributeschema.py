from marshmallow_jsonapi import Schema, fields

from .multilingualDescription import MultilingualDescriptionSchema

class ManagedAttributesSchema(Schema):
    id = fields.Str(dump_only=False)
    name = fields.Str(attribute="attributes.name")
    key = fields.Str(allow_none=True, attribute="attributes.key")
    vocabularyElementType = fields.Str(attribute="attributes.vocabularyElementType")
    unit = fields.Str(allow_none=True, attribute="attributes.unit")
    managedAttributeComponent = fields.Str(allow_none=True, attribute="attributes.managedAttributeComponent")
    acceptedValues = fields.List(fields.Raw(),allow_none=True, attribute="attributes.acceptedValues")
    createdOn = fields.DateTime(allow_none=True, attribute="attributes.createdOn")
    createdBy = fields.Str(allow_none=True, attribute="attributes.createdBy")
    group = fields.Str(allow_none=True, attribute="attributes.group")
    multilingualDescription = fields.Nested(MultilingualDescriptionSchema,allow_none=True,attribute="attributes.multilingualDescription")

    meta = fields.DocumentMeta()

    class Meta:
        type_ = "managed-attribute"
        strict = False
        #exclude = ("meta",)  # Exclude the 'meta' field
