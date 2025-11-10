from marshmallow import Schema, fields

class TitleSchema(Schema):
    lang = fields.String(required=True)
    title = fields.String(required=True)

class MultilingualTitleSchema(Schema):
    titles = fields.List(fields.Nested(TitleSchema), allow_none=True)

