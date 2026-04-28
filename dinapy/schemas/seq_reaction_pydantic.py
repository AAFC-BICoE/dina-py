"""
Pydantic model for SeqReaction.

Replaces:
  - dinapy/entities/SeqReaction.py  (SeqReactionAttributesDTO + builder)
  - dinapy/schemas/seq_reaction_schema.py  (SeqReactionSchema)
"""
from __future__ import annotations
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class SeqReactionAttributes(BaseModel):
    createdBy: str | None = None
    createdOn: str | None = None
    group: str | None = None


SeqReactionData = JsonApiData[SeqReactionAttributes]


class SeqReactionDocument(JsonApiDocument[SeqReactionAttributes]):
    pass
