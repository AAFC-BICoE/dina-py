"""
Pydantic model for Project.

Replaces:
  - dinapy/entities/Project.py  (ProjectAttributesDTO + builder)
  - dinapy/schemas/project_schema.py  (ProjectSchema)
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class ProjectAttributes(BaseModel):
    createdBy: str | None = None
    createdOn: datetime | None = None
    contributors: list[dict[str, Any]] | None = None
    group: str
    name: str
    startDate: str | None = None
    endDate: str | None = None
    status: str | None = None
    multilingualDescription: dict[str, Any] | None = None
    extensionValues: dict[str, Any] | None = None


ProjectData = JsonApiData[ProjectAttributes]


class ProjectDocument(JsonApiDocument[ProjectAttributes]):
    pass
