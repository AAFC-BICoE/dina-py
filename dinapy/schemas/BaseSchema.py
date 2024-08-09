from marshmallow_jsonapi import Schema, fields
import re

class BaseSchema(Schema):
	id = fields.Str(dump_only=True,allow_none=True)
	type = fields.Str(allow_none=True)

def create_relationship(type):
	return fields.Relationship(
		self_url=f"/api/v1/material-sample/{{id}}/relationships/{type}",
		self_url_kwargs={"id": "<id>"},
		related_url=f"/api/v1/material-sample/{{id}}/{type}",
		related_url_kwargs={"id": "<id>"},
		allow_none=True,
		include_resource_linkage=True,
		attribute=f"relationships.{type}",
		type_=CamelToHyphenated(type)
	)
def CamelToHyphenated(camel_str):
	hyphenated_str = re.sub(r'(?<!^)(?=[A-Z])', '-', camel_str).lower()
	return hyphenated_str