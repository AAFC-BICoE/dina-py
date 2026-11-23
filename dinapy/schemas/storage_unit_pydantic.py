"""
Pydantic model for StorageUnit.

Relationships (set via ``relationships`` on the JSON API data object):
  - storageUnitType: storage-unit-type
  - parentStorageUnit: storage-unit
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class StorageUnitAttributes(BaseModel):
    createdBy: str | None = None
    createdOn: datetime | None = None
    name: str
    group: str
    barcode: str | None = None
    isGeneric: bool | None = False
    # Read-only / computed fields returned by the API
    storageUnitChildren: list[dict[str, Any]] | None = None
    hierarchy: list[dict[str, Any]] | None = None
    location: dict[str, Any] | None = None


StorageUnitData = JsonApiData[StorageUnitAttributes]


class StorageUnitDocument(JsonApiDocument[StorageUnitAttributes]):
    pass
