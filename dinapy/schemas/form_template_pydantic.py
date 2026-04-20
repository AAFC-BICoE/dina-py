"""
Pydantic model for FormTemplate.

Replaces:
  - dinapy/entities/FormTemplate.py  (FormTemplateAttributesDTO + builder)
  - dinapy/schemas/formtemplateschema.py  (FormTemplateSchema)
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class FormTemplateAttributes(BaseModel):
    createdBy: str | None = None
    createdOn: datetime | None = None
    group: str | None = None
    name: str | None = None
    restrictToCreatedBy: bool | None = None
    viewConfiguration: dict[str, Any] | None = None
    components: dict[str, Any] | None = None


FormTemplateData = JsonApiData[FormTemplateAttributes]


class FormTemplateDocument(JsonApiDocument[FormTemplateAttributes]):
    pass
