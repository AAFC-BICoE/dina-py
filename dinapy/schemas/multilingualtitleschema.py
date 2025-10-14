from marshmallow_jsonapi import Schema, fields

class TitleSchema(Schema):
    lang = fields.String(required=True)
    title = fields.String(required=True)

class TitleListSchema(Schema):
    titles = fields.List(fields.Nested(TitleSchema))

class MultilingualTitleSchema(Schema):
    multilingualTitle = fields.Nested(TitleListSchema)
