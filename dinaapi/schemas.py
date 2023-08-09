from marshmallow_jsonapi import Schema, fields

class PersonSchema(Schema):
    id = fields.Str(required=True)
    displayName = fields.Str(required=True, attribute="attributes.displayName")
    email = fields.Str(required=True, attribute="attributes.email")
    createdBy = fields.Str(required=True, attribute="attributes.createdBy")
    createdOn = fields.DateTime(required=True, attribute="attributes.createdOn")
    givenNames = fields.Str(required=True, attribute="attributes.givenNames")
    familyNames = fields.Str(required=True, attribute="attributes.familyNames")
    aliases = fields.List(fields.Str(), allow_none=True, attribute="attributes.aliases")
    webpage = fields.Str(allow_none=True, attribute="attributes.webpage")
    remarks = fields.Str(allow_none=True, attribute="attributes.remarks")
    
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



# GET response for Person
# {
#     "data": {
#         "id": "bfa3c68b-8e13-4295-8e25-47dbe041cb64",
#         "type": "person",
#         "links": {"self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64"},
#         "attributes": {
#             "displayName": "testBob",
#             "email": "bob.builder@agr.gc.ca",
#             "createdBy": "cnc-su",
#             "createdOn": "2023-02-20T16:18:10.688627Z",
#             "givenNames": "Bob",
#             "familyNames": "Builder",
#             "aliases": ["Yes we can"],
#             "webpage": None,
#             "remarks": None,
#         },
#         "relationships": {
#             "identifiers": {
#                 "links": {
#                     "self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/relationships/identifiers",
#                     "related": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/identifiers",
#                 }
#             },
#             "organizations": {
#                 "links": {
#                     "self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/relationships/organizations",
#                     "related": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/organizations",
#                 }
#             },
#         },
#     },
#     "meta": {"totalResourceCount": 1, "moduleVersion": "0.24"},
# }