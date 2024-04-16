from marshmallow import Schema, fields

class DescriptionSchema(Schema):
    lang = fields.String(required=True)
    desc = fields.String(required=True)

class MultilingualDescriptionSchema(Schema):
    descriptions = fields.List(fields.Nested(DescriptionSchema), allow_none=True, required=True)
