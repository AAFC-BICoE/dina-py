"""
Pydantic model for MetagenomicsBatchItem.

Replaces:
  - dinapy/entities/MetagenomicsBatchItem.py  (MetagenomicsBatchItemDTO + builder)
  - dinapy/schemas/metagenomics_batch_item_schema.py  (MetagenomicsBatchItemSchema)
"""
from __future__ import annotations
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class MetagenomicsBatchItemAttributes(BaseModel):
    createdBy: str | None = None
    createdOn: str | None = None


MetagenomicsBatchItemData = JsonApiData[MetagenomicsBatchItemAttributes]


class MetagenomicsBatchItemDocument(JsonApiDocument[MetagenomicsBatchItemAttributes]):
    pass
