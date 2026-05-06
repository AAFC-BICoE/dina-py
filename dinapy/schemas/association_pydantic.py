"""
Pydantic model for Association.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class AssociationAttributes(BaseModel):
    createdBy: str | None = None
    createdOn: datetime | None = None
    associationType: str | None = None
    remarks: str | None = None

AssociationData = JsonApiData[AssociationAttributes]


class AssociationDocument(JsonApiDocument[AssociationAttributes]):
    pass
