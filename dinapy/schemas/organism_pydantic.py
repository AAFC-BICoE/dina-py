"""
Pydantic model for Organism.

"""
from __future__ import annotations
from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, HttpUrl

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class ScientificNameDetails(BaseModel):
    classificationPath: str | None = None
    classificationRanks: str | None = None
    sourceUrl: HttpUrl | str | None = None
    labelHtml: str | None = None
    recordedOn: date | None = None
    currentName: str | None = None
    isSynonym: bool | None = None


class Determination(BaseModel):
    verbatimScientificName: str | None = None
    verbatimDeterminer: str | None = None
    verbatimDate: str | None = None
    scientificName: str | None = None
    transcriberRemarks: str | None = None
    verbatimRemarks: str | None = None
    determinationRemarks: str | None = None
    typeStatus: str | None = None
    typeStatusEvidence: str | None = None
    determiner: list[str] | None = None
    determinedOn: date | None = None
    qualifier: str | None = None
    scientificNameSource: str | None = None
    scientificNameDetails: ScientificNameDetails | None = None
    isPrimary: bool | None = None
    isFiledAs: bool | None = None
    managedAttributes: dict[str, Any] | None = None


class OrganismAttributes(BaseModel):
    # Read-only server fields
    createdBy: str | None = None
    createdOn: datetime | None = None

    # Core fields
    group: str
    isTarget: bool | None = None
    lifeStage: str | None = None
    sex: str | None = None
    remarks: str | None = None
    dwcVernacularName: str | None = None
    managedAttributes: dict[str, Any] | None = None

    # Nested
    determination: list[Determination] | None = None


OrganismData = JsonApiData[OrganismAttributes]


class OrganismDocument(JsonApiDocument[OrganismAttributes]):
    pass
