# This file holds schemas for serializing and deserializing Metadata entities
# Using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow import post_load, validate
from marshmallow_jsonapi import Schema, fields


class MetadataSchema(Schema):
    """Schema for a Metadata used for serializing and deserializing JSON."""

    id = fields.Str(dump_only=False)
    # type = fields.Str()
    # self_link = fields.Nested("links.self")
    version = fields.Int(attribute="attributes.version")
    createdBy = fields.Str(attribute="attributes.createdBy")
    createdOn = fields.DateTime(attribute="attributes.createdOn")
    bucket = fields.Str(attribute="attributes.bucket")
    fileIdentifier = fields.UUID(attribute="attributes.fileIdentifier", allow_none=True)
    fileExtension = fields.Str(attribute="attributes.fileExtension", allow_none=True)
    resourceExternalURL = fields.Str(
        attribute="attributes.resourceExternalURL", allow_none=True
    )
    dcFormat = fields.Str(attribute="attributes.dcFormat", allow_none=True)
    dcType = fields.Str(
        validate=validate.OneOf(
            ["IMAGE", "MOVING_IMAGE", "SOUND", "TEXT", "DATASET", "UNDETERMINED"]
        ),
        allow_none=True,
    )
    acCaption = fields.Str(attribute="attributes.acCaption", allow_none=True)
    acDigitizationDate = fields.DateTime(attribute="attributes.acDigitizationDate", allow_none=True)
    xmpMetadataDate = fields.DateTime(attribute="attributes.xmpMetadataDate", allow_none=True)
    xmpRightsWebStatement = fields.Str(attribute="attributes.xmpRightsWebStatement", allow_none=True)
    dcRights = fields.Str(attribute="attributes.dcRights", allow_none=True)
    xmpRightsOwner = fields.Str(attribute="attributes.xmpRightsOwner", allow_none=True)
    xmpRightsUsageTerms = fields.Str(attribute="attributes.xmpRightsUsageTerms", allow_none=True)
    orientation = fields.Int(attribute="attributes.orientation", allow_none=True)
    originalFilename = fields.Str(attribute="attributes.originalFilename")
    acHashFunction = fields.Str(attribute="attributes.acHashFunction", allow_none=True)
    acHashValue = fields.Str(attribute="attributes.acHashValue", allow_none=True)
    acTags = fields.List(fields.Str(), attribute="attributes.acTags", allow_none=True)
    publiclyReleasable = fields.Bool(attribute="attributes.publiclyReleasable", allow_none=True)
    notPubliclyReleasableReason = fields.Str(
        attribute="attributes.notPubliclyReleasableReason", allow_none=True
    )
    acSubtype = fields.Str(attribute="attributes.acSubtype", allow_none=True)
    group = fields.Str(attribute="attributes.group", required=True)
    managedAttributes = fields.Dict(attribute="attributes.managedAttributes", allow_none=True)

    # Relationships
    acMetadataCreator = fields.Relationship(
        self_url="/api/v1/metadata/{id}/relationships/acMetadataCreator",
        self_url_kwargs={"id": "<id>"},
        related_url="/api/v1/metadata/{id}/acMetadataCreator",
        related_url_kwargs={"id": "<id>"},
        type_="person",
    )

    derivatives = fields.Relationship(
        self_url="/api/v1/metadata/{id}/relationships/derivatives",
        self_url_kwargs={"id": "<id>"},
        related_url="/api/v1/metadata/{id}/derivatives",
        related_url_kwargs={"id": "<id>"},
        type_="derivative",
        many=True,
    )

    dcCreator = fields.Relationship(
        self_url="/api/v1/metadata/{id}/relationships/dcCreator",
        self_url_kwargs={"id": "<id>"},
        related_url="/api/v1/metadata/{id}/dcCreator",
        related_url_kwargs={"id": "<id>"},
        type_="person",
    )

    meta = fields.DocumentMeta()

    class Meta:
        type_ = "metadata"
        # self_url = "/api/v1/metadata/{id}" or None
        # self_url_kwargs = {"id": "<id>"}
        strict = True

    def get_url(self, obj, **kwargs):
        if obj.id is not None:
            return super().get_url(obj, **kwargs)
        else:
            return None

    @post_load
    def remove_none_values(self, data, **kwargs):
        def clean_dict(d):
            if not isinstance(d, dict):
                return d
            cleaned = {k: clean_dict(v) for k, v in d.items() if v is not None}
            return cleaned if cleaned else None

        return clean_dict(data)


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
