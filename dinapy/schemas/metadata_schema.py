# This file holds schemas for serializing and deserializing Metadata entities
# Using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow import post_dump, post_load, validate
from marshmallow_jsonapi import Schema, fields

from dinapy.entities.Metadata import MetadataDTO
from dinapy.schemas.BaseSchema import BaseSchema, create_relationship
from dinapy.schemas.customFields import SkipUndefinedField


class AcMetadataCreator(BaseSchema):
    class Meta:
        type_ = "person"


class Derivatives(BaseSchema):
    class Meta:
        type_ = "derivative"


class DcCreator(BaseSchema):
    class Meta:
        type_ = "person"


class MetadataSchema(Schema):
    """Schema for a Metadata used for serializing and deserializing JSON."""

    id = fields.Str(load_only=True, )
    createdOn = SkipUndefinedField(
        fields.DateTime, load_only=True, attribute="attributes.createdOn"
    )
    createdBy = SkipUndefinedField(
        fields.Str, load_only=True, attribute="attributes.createdBy"
    )
    bucket = SkipUndefinedField(
        fields.Str, required=True, attribute="attributes.bucket"
    )
    filename = SkipUndefinedField(
        fields.Str, attribute="attributes.filename", allow_none=True
    )
    fileIdentifier = SkipUndefinedField(
        fields.UUID, attribute="attributes.fileIdentifier", allow_none=True
    )
    fileExtension = SkipUndefinedField(
        fields.Str, attribute="attributes.fileExtension", allow_none=True
    )
    resourceExternalURL = SkipUndefinedField(
        fields.Str, attribute="attributes.resourceExternalURL", allow_none=True
    )
    dcFormat = SkipUndefinedField(
        fields.Str, attribute="attributes.dcFormat", allow_none=True
    )
    dcType = SkipUndefinedField(
        fields.Str,
        validate=validate.OneOf(
            ["IMAGE", "MOVING_IMAGE", "SOUND", "TEXT", "DATASET", "UNDETERMINED"]
        ),
        allow_none=True,
        attribute="attributes.dcType"
    )

    acCaption = SkipUndefinedField(
        fields.Str, attribute="attributes.acCaption", allow_none=True
    )
    acDigitizationDate = SkipUndefinedField(
        fields.DateTime, attribute="attributes.acDigitizationDate", allow_none=True
    )
    xmpMetadataDate = SkipUndefinedField(
        fields.DateTime, attribute="attributes.xmpMetadataDate", allow_none=True
    )
    xmpRightsWebStatement = SkipUndefinedField(
        fields.Str, attribute="attributes.xmpRightsWebStatement", allow_none=True
    )
    dcRights = SkipUndefinedField(
        fields.Str, attribute="attributes.dcRights", allow_none=True
    )
    xmpRightsOwner = SkipUndefinedField(
        fields.Str, attribute="attributes.xmpRightsOwner", allow_none=True
    )
    xmpRightsUsageTerms = SkipUndefinedField(
        fields.Str, attribute="attributes.xmpRightsUsageTerms", allow_none=True
    )
    orientation = SkipUndefinedField(
        fields.Int, attribute="attributes.orientation", allow_none=True
    )
    originalFilename = SkipUndefinedField(
        fields.Str, attribute="attributes.originalFilename"
    )
    acHashFunction = SkipUndefinedField(
        fields.Str, attribute="attributes.acHashFunction", allow_none=True
    )
    acHashValue = SkipUndefinedField(
        fields.Str, attribute="attributes.acHashValue", allow_none=True
    )
    acTags = SkipUndefinedField(
        fields.List, fields.Str, attribute="attributes.acTags", allow_none=True
    )
    publiclyReleasable = SkipUndefinedField(
        fields.Bool, attribute="attributes.publiclyReleasable", allow_none=True
    )
    notPubliclyReleasableReason = SkipUndefinedField(
        fields.Str, attribute="attributes.notPubliclyReleasableReason", allow_none=True
    )
    acSubtype = SkipUndefinedField(
        fields.Str, attribute="attributes.acSubtype", allow_none=True
    )
    group = SkipUndefinedField(fields.Str, required=True, attribute="attributes.group")
    managedAttributes = SkipUndefinedField(
        fields.Dict, required=False, attribute="attributes.managedAttributes"
    )

    # Relationships
    acMetadataCreator = create_relationship("metadata","person","acMetadataCreator")

    derivatives = create_relationship("metadata","derivative","derivatives")

    dcCreator = create_relationship("metadata","person","dcCreator")

    @post_load
    def set_none_to_undefined(self, data, **kwargs):
        for attr in data.attributes:
            if data.attributes[attr] is None:
                data.attributes[attr] = 'undefined'
        return data
        
    @post_dump
    def remove_skipped_fields(self, data, many, **kwargs):
        # Remove fields with the special marker value
        return {key: value for key, value in data.items() if value is not SkipUndefinedField(fields.Field).SKIP_MARKER}

    @post_load
    def object_deserialization(self, data, **kwargs):
        if 'meta' in data:
            del data['meta']
        return MetadataDTO(**data)

    meta = fields.DocumentMeta()

    class Meta:
        type_ = "metadata"


# {
#   "data": {
#     "id": "0190e0df-abef-7cf5-baa2-9453ec6f012d",
#     "type": "metadata",
#     "attributes": {
#       "createdBy": "dina-admin",
#       "createdOn": "2024-07-23T18:34:33.328038Z",
#       "bucket": "aafc",
#       "fileIdentifier": "0190e0df-0809-71a3-b8e5-036cfbfec914",
#       "fileExtension": ".png",
#       "resourceExternalURL": null,
#       "dcFormat": "image/png",
#       "dcType": "IMAGE",
#       "acCaption": "sample_640×426.png",
#       "acDigitizationDate": "2024-07-23T07:00:00Z",
#       "xmpMetadataDate": "2024-07-23T18:34:33.357486Z",
#       "xmpRightsWebStatement": "https://open.canada.ca/en/open-government-licence-canada",
#       "dcRights": "© His Majesty The King in Right of Canada, as represented by the Minister of Agriculture and Agri-Food | © Sa Majesté le Roi du chef du Canada, représentée par le ministre de l’Agriculture et de l’Agroalimentaire",
#       "xmpRightsOwner": "Government of Canada",
#       "xmpRightsUsageTerms": "Government of Canada Usage Term",
#       "orientation": 1,
#       "originalFilename": "sample_640×426.png",
#       "acHashFunction": "SHA-1",
#       "acHashValue": "e29c5ca02f1b2faec0302700fc084584cf2869ae",
#       "publiclyReleasable": true,
#       "acSubtype": "OBJECT SUBTYPE 1",
#       "group": "aafc",
#       "managedAttributes": {
#         "legacy_barcode": "123"
#       }
#     },
#     "relationships": {
#       "acMetadataCreator": {
#         "data": {
#           "id": "3c47203f-9833-4945-b673-ece4e3bd4f9a",
#           "type": "person"
#         }
#       },
#       "dcCreator": {
#         "data": {
#           "id": "afcf0bcc-c6c8-40c5-b97b-1855ce5d1729",
#           "type": "person"
#         }
#       }
#     }
#   },
#   "meta": {
#     "totalResourceCount": 1,
#     "external": [
#       {
#         "href": "Agent/api/v1/person",
#         "type": "person"
#       }
#     ],
#     "moduleVersion": "1.17"
#   },
# }
