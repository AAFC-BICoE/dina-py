"""
Pydantic model for StorageUnitUsage.

Replaces:
  - dinapy/entities/StorageUnitUsage.py  (StorageUnitUsageAttributesDTO + builder)
  - dinapy/schemas/storageunitusageschema.py  (StorageUnitUsage schema)
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class StorageUnitUsageAttributes(BaseModel):
    usageType: str | None = None
    wellRow: str | None = None
    wellColumn: int | None = None
    cellNumber: int | None = None
    storageUnitName: str | None = None
    createdOn: datetime | None = None
    createdBy: str | None = None


StorageUnitUsageData = JsonApiData[StorageUnitUsageAttributes]


class StorageUnitUsageDocument(JsonApiDocument[StorageUnitUsageAttributes]):
    pass
