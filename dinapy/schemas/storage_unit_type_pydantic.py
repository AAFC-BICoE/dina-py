"""
Pydantic model for StorageUnitType.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class StorageUnitTypeAttributes(BaseModel):
    createdBy: str | None = None
    createdOn: datetime | None = None
    name: str
    group: str
    isInsertable: bool | None = None
    # e.g. {"numberOfRows": 8, "numberOfColumns": 12, "fillDirection": "BY_ROW"}
    gridLayoutDefinition: dict[str, Any] | None = None


StorageUnitTypeData = JsonApiData[StorageUnitTypeAttributes]


class StorageUnitTypeDocument(JsonApiDocument[StorageUnitTypeAttributes]):
    pass
