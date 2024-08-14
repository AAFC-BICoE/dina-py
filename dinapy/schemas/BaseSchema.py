from marshmallow_jsonapi import Schema, fields
import re

class BaseSchema(Schema):
	id = fields.Str(dump_only=True,allow_none=True)
	type = fields.Str(allow_none=True)

def create_relationship(type, key=None):
	return fields.Relationship(
		self_url=f"/api/v1/material-sample/{{id}}/relationships/{key if key else type}",
		self_url_kwargs={"id": "<id>"},
		related_url=f"/api/v1/material-sample/{{id}}/{key if key else type}",
		related_url_kwargs={"id": "<id>"},
		allow_none=True,
		include_resource_linkage=True,
		attribute=f"relationships.{key if key else type}",
		type_=CamelToHyphenated(type)
	)
def CamelToHyphenated(camel_str):
	hyphenated_str = re.sub(r'(?<!^)(?=[A-Z])', '-', camel_str).lower()
	return hyphenated_str