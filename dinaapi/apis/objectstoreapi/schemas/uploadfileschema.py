# This file holds schemas for serializing and deserializing File upload response entities
# using the JSON API format. It utilizes the marshmallow_jsonapi library.
from marshmallow_jsonapi import Schema, fields

class UploadFileSchema(Schema):
    class Meta:
        type_ = 'file'  # Type name for your resource

    fileIdentifier = fields.Str(attribute='fileIdentifier')
    dcType = fields.Str(attribute='dcType')
    createdBy = fields.Str(attribute='createdBy')
    createdOn = fields.DateTime(attribute='createdOn')
    originalFilename = fields.Str(attribute='originalFilename')
    sha1Hex = fields.Str(attribute='sha1Hex')
    receivedMediaType = fields.Str(attribute='receivedMediaType')
    detectedMediaType = fields.Str(attribute='detectedMediaType')
    detectedFileExtension = fields.Str(attribute='detectedFileExtension')
    evaluatedMediaType = fields.Str(attribute='evaluatedMediaType')
    evaluatedFileExtension = fields.Str(attribute='evaluatedFileExtension')
    sizeInBytes = fields.Int(attribute='sizeInBytes')
    bucket = fields.Str(attribute='bucket')
    dateTimeDigitized = fields.DateTime(attribute='dateTimeDigitized')
    exif = fields.Dict(attribute='exif')
    isDerivative = fields.Boolean(attribute='isDerivative')
    uuid = fields.Str(attribute='uuid')
    meta = fields.Dict(attribute='meta')