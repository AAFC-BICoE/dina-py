"""
Pydantic model for CollectingEvent.

Replaces:
  - dinapy/entities/CollectingEvent.py  (CollectingEventAttributesDTO + builder)
  - dinapy/schemas/collectingeventschema.py  (CollectingEventSchema)

Usage — deserializing an API response:
    doc = CollectingEventDocument.parse_response(api_response_dict)
    doc.data.id           # "f08516e5-..."
    doc.data.attributes.group   # "phillips-lab"

Usage — serializing a new resource for POST/PATCH:
    doc = CollectingEventDocument(
        data=CollectingEventData(
            type="collecting-event",
            attributes=CollectingEventAttributes(group="aafc"),
            relationships={
                "protocol": RelationshipData(
                    data=RelationshipLinkage(type="protocol", id="8f68a05f-...")
                ),
                "collectors": RelationshipData(
                    data=[RelationshipLinkage(type="person", id="497f6eca-...")]
                ),
            }
        )
    )
    payload = doc.to_request()  # only set fields included — no 'undefined' needed
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import (
    JsonApiData,
    JsonApiDocument,
    RelationshipData,
    RelationshipLinkage,
)


class CollectingEventAttributes(BaseModel):
    # Read-only server fields
    version: int | None = None
    createdBy: str | None = None
    createdOn: datetime | None = None

    # Core fields
    group: str | None = None
    startEventDateTime: str | None = None
    endEventDateTime: str | None = None
    verbatimEventDateTime: str | None = None
    habitat: str | None = None
    substrate: str | None = None
    remarks: str | None = None
    host: str | None = None

    # DWC fields
    dwcFieldNumber: str | None = None
    dwcRecordNumber: str | None = None
    dwcRecordedBy: str | None = None
    dwcVerbatimCoordinates: str | None = None
    dwcVerbatimLatitude: str | None = None
    dwcVerbatimLongitude: str | None = None
    dwcVerbatimCoordinateSystem: str | None = None
    dwcVerbatimSRS: str | None = None
    dwcVerbatimElevation: str | None = None
    dwcVerbatimDepth: str | None = None
    dwcVerbatimLocality: str | None = None
    dwcCountry: str | None = None
    dwcCountryCode: str | None = None
    dwcStateProvince: str | None = None
    dwcMinimumElevationInMeters: float | None = None
    dwcMaximumElevationInMeters: float | None = None
    dwcMinimumDepthInMeters: float | None = None
    dwcMaximumDepthInMeters: float | None = None

    # Complex fields
    otherRecordNumbers: list[str] | None = None
    geoReferenceAssertions: list[dict[str, Any]] | None = None
    eventGeom: dict[str, Any] | None = None
    extensionValues: dict[str, Any] | None = None
    managedAttributes: dict[str, Any] | None = None
    geographicPlaceNameSource: str | None = None
    geographicPlaceNameSourceDetail: dict[str, Any] | None = None
    geographicThesaurus: dict[str, Any] | None = None
    tags: list[str] | None = None

    # Visibility
    publiclyReleasable: bool | None = None
    notPubliclyReleasableReason: str | None = None


# Typed aliases for the generic envelope
CollectingEventData = JsonApiData[CollectingEventAttributes]


class CollectingEventDocument(JsonApiDocument[CollectingEventAttributes]):
    pass
