"""
Pydantic model for MolecularAnalysisResult.

Replaces:
  - dinapy/entities/MolecularAnalysisResult.py  (MolecularAnalysisResultDTO + builder)
  - dinapy/schemas/molecular_analysis_result_schema.py  (MolecularAnalysisResultSchema)
"""
from __future__ import annotations
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class MolecularAnalysisResultAttributes(BaseModel):
    group: str
    createdBy: str | None = None
    createdOn: str | None = None


MolecularAnalysisResultData = JsonApiData[MolecularAnalysisResultAttributes]


class MolecularAnalysisResultDocument(JsonApiDocument[MolecularAnalysisResultAttributes]):
    pass
