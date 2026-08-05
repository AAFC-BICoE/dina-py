"""
Pydantic model for Controlled Vocabulary Item.

See: /controlled-vocabulary-item endpoint
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class ControlledVocabularyItemAttributes(BaseModel):
    name: str | None = None
    key: str | None = None
    group: str | None = None
    term: str | None = None
    vocabularyElementType: str | None = None
    acceptedValues: list[Any] | None = None
    unit: str | None = None
    uriTemplate: str | None = None
    dinaComponent: str | None = None
    multilingualTitle: dict[str, Any] | None = None
    multilingualDescription: dict[str, Any] | None = None
    createdBy: str | None = None
    createdOn: datetime | None = None
    lastUpdatedOn: datetime | None = None


ControlledVocabularyData = JsonApiData[ControlledVocabularyItemAttributes]


class ControlledVocabularyDocument(JsonApiDocument[ControlledVocabularyItemAttributes]):
   """Single-item JSON:API document — use for GET by ID and POST responses.

    For GET all responses, iterate over ``response["data"]`` and deserialize
    each item individually:

        [ControlledVocabularyDocument.deserialize({"data": item})
         for item in response["data"]]
    """