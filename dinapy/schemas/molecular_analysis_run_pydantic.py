"""
Pydantic model for MolecularAnalysisRun.

Replaces:
  - dinapy/entities/MolecularAnalysisRun.py  (MolecularAnalysisRunDTO + builder)
  - dinapy/schemas/molecular_analysis_run_schema.py  (MolecularAnalysisRunSchema)
"""
from __future__ import annotations
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class MolecularAnalysisRunAttributes(BaseModel):
    createdBy: str | None = None
    createdOn: str | None = None
    group: str
    name: str | None = None


MolecularAnalysisRunData = JsonApiData[MolecularAnalysisRunAttributes]


class MolecularAnalysisRunDocument(JsonApiDocument[MolecularAnalysisRunAttributes]):
    pass
