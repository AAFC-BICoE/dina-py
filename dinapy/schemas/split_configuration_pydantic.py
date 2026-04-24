"""
Pydantic model for SplitConfiguration.

Replaces:
  - dinapy/entities/SplitConfiguration.py  (SplitConfigurationAttributesDTO + builder)
  - dinapy/schemas/splitconfigurationschema.py  (SplitConfigurationSchema)
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class SplitConfigurationAttributes(BaseModel):
    createdBy: str | None = None
    createdOn: datetime | None = None
    group: str
    name: str | None = None
    strategy: str | None = None
    conditionalOnMaterialSampleTypes: list[str] | None = None
    characterType: str | None = None
    separator: str | None = None
    materialSampleTypeCreatedBySplit: str | None = None


SplitConfigurationData = JsonApiData[SplitConfigurationAttributes]


class SplitConfigurationDocument(JsonApiDocument[SplitConfigurationAttributes]):
    pass
