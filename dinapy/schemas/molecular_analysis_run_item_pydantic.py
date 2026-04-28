"""
Pydantic model for MolecularAnalysisRunItem.

Replaces:
  - dinapy/entities/MolecularAnalysisRunItem.py  (MolecularAnalysisRunItemDTO + builder)
  - dinapy/schemas/molecular_analysis_run_item_schema.py  (MolecularAnalysisRunItemSchema)
"""
from __future__ import annotations
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class MolecularAnalysisRunItemAttributes(BaseModel):
    createdBy: str | None = None
    createdOn: str | None = None
    usageType: str | None = None


MolecularAnalysisRunItemData = JsonApiData[MolecularAnalysisRunItemAttributes]


class MolecularAnalysisRunItemDocument(JsonApiDocument[MolecularAnalysisRunItemAttributes]):
    pass
