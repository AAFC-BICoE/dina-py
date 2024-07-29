from marshmallow import fields

class Relationship(fields.Field):
    def __init__(self, many=False, type_=None, **kwargs):
        self.many = many
        self.type_ = type_
        super().__init__(**kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return {
            "data": {
                "type": value.type,
                "id": value.id
            }
        }

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        return {
            "type": value.get("data", {}).get("type"),
            "id": value.get("data", {}).get("id")
        }
