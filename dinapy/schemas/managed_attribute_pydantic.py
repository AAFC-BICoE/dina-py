"""
Pydantic model for ManagedAttribute.

Replaces:
  - dinapy/entities/ManagedAttribute.py  (ManagedAttributesDTO + builder)
  - dinapy/schemas/managedattributeschema.py  (ManagedAttributesSchema)
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class ManagedAttributeAttributes(BaseModel):
    name: str | None = None
    key: str | None = None
    vocabularyElementType: str | None = None
    unit: str | None = None
    managedAttributeComponent: str | None = None
    acceptedValues: list[Any] | None = None
    createdOn: datetime | None = None
    createdBy: str | None = None
    group: str | None = None
    multilingualDescription: dict[str, Any] | None = None


ManagedAttributeData = JsonApiData[ManagedAttributeAttributes]


class ManagedAttributeDocument(JsonApiDocument[ManagedAttributeAttributes]):
    pass
