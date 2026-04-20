"""
Pydantic model for MetagenomicsBatch.

Replaces:
  - dinapy/entities/MetagenomicsBatch.py  (MetagenomicsBatchDTO + builder)
  - dinapy/schemas/metagenomics_batch_schema.py  (MetagenomicsBatchSchema)
"""
from __future__ import annotations
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class MetagenomicsBatchAttributes(BaseModel):
    createdBy: str | None = None
    createdOn: str | None = None
    group: str | None = None
    name: str | None = None


MetagenomicsBatchData = JsonApiData[MetagenomicsBatchAttributes]


class MetagenomicsBatchDocument(JsonApiDocument[MetagenomicsBatchAttributes]):
    pass
