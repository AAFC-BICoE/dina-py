"""
Pydantic model for Assemblage.

Replaces:
  - dinapy/entities/Assemblage.py  (AssemblageAttributesDTO + builder)
  - dinapy/schemas/assemblageschema.py  (AssemblageSchema)
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class AssemblageAttributes(BaseModel):
    createdBy: str | None = None
    createdOn: datetime | None = None
    group: str
    name: str | None = None
    managedAttributes: dict[str, Any] | None = None
    multilingualTitle: dict[str, Any] | None = None
    multilingualDescription: dict[str, Any] | None = None


AssemblageData = JsonApiData[AssemblageAttributes]


class AssemblageDocument(JsonApiDocument[AssemblageAttributes]):
    pass
