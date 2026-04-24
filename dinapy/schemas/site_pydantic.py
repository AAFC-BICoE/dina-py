"""
Pydantic model for Site.

Replaces:
  - dinapy/entities/Site.py  (SiteAttributesDTO + builder)
  - dinapy/schemas/site_schema.py  (SiteSchema)
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class SiteAttributes(BaseModel):
    createdOn: datetime | None = None
    createdBy: str | None = None
    group: str
    name: str
    code: str | None = None
    siteGeom: dict[str, Any] | None = None
    multilingualDescription: dict[str, Any] | None = None


SiteData = JsonApiData[SiteAttributes]


class SiteDocument(JsonApiDocument[SiteAttributes]):
    pass
