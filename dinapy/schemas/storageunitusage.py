# This file holds schemas for serializing and deserializing Person entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields

class StorageUnitUsage(Schema):
    '''Schema for a Person used for serializing and deserializing JSON.'''
    id = fields.Str(dump_only=False)
    usageType = fields.Int(allow_none=True, attribute="attributes.usageType")
    wellRow = fields.Str(required=True, attribute="attributes.wellRow")
    wellColumn = fields.Str(required=True,allow_none=True, attribute="attributes.wellColumn")
    cellNumber = fields.Str(required=True,allow_none=True, attribute="attributes.cellNumber")
    storageUnitName = fields.Str(required=True,allow_none=True, attribute="attributes.storageUnitName")
    createdOn = fields.Str(required=True,allow_none=True, attribute="attributes.createdOn")
    createdBy = fields.Str(required=True,allow_none=True, attribute="attributes.createdBy")


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