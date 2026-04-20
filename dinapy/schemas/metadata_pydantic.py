"""
Pydantic model for Metadata (object-store).

Replaces:
  - dinapy/entities/Metadata.py  (MetadataAttributesDTO + builder)
  - dinapy/schemas/metadata_schema.py  (MetadataSchema)
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class MetadataAttributes(BaseModel):
    createdOn: datetime | None = None
    createdBy: str | None = None
    bucket: str | None = None
    filename: str | None = None
    fileIdentifier: str | None = None
    fileExtension: str | None = None
    resourceExternalURL: str | None = None
    sourceSet: str | None = None
    dcFormat: str | None = None
    dcType: str | None = None
    acCaption: str | None = None
    acDigitizationDate: datetime | None = None
    xmpMetadataDate: datetime | None = None
    xmpRightsWebStatement: str | None = None
    dcRights: str | None = None
    xmpRightsOwner: str | None = None
    xmpRightsUsageTerms: str | None = None
    orientation: int | None = None
    originalFilename: str | None = None
    acHashFunction: str | None = None
    acHashValue: str | None = None
    acTags: list[str] | None = None
    publiclyReleasable: bool | None = None
    notPubliclyReleasableReason: str | None = None
    acSubtype: str | None = None
    group: str | None = None
    managedAttributes: dict[str, Any] | None = None


MetadataData = JsonApiData[MetadataAttributes]


class MetadataDocument(JsonApiDocument[MetadataAttributes]):
    pass
