"""
Pydantic model for Person.

Replaces:
  - dinapy/entities/Person.py  (PersonAttributesDTO + builder)
  - dinapy/schemas/personschema.py  (PersonSchema)
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class PersonAttributes(BaseModel):
    displayName: str
    familyNames: str
    email: str | None = None
    createdBy: str | None = None
    createdOn: datetime | None = None
    givenNames: str | None = None
    aliases: list[str] | None = None
    webpage: str | None = None
    remarks: str | None = None


PersonData = JsonApiData[PersonAttributes]


class PersonDocument(JsonApiDocument[PersonAttributes]):
    pass
