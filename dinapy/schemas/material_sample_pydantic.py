"""
Pydantic model for MaterialSample.

Replaces:
  - dinapy/entities/MaterialSample.py  (MaterialSampleAttributesDTO + builder)
  - dinapy/schemas/materialsampleschema.py  (MaterialSampleSchema)
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from dinapy.schemas.pydantic_base import JsonApiData, JsonApiDocument


class MaterialSampleAttributes(BaseModel):
    version: int | None = None
    group: str
    createdOn: datetime | None = None
    createdBy: str | None = None
    dwcCatalogNumber: str | None = None
    dwcOtherCatalogNumbers: list[str] | None = None
    materialSampleName: str | None = None
    materialSampleType: str | None = None
    materialSampleChildren: list[Any] | None = None
    preparationDate: str | None = None
    preservationType: str | None = None
    preparationFixative: str | None = None
    preparationMaterials: str | None = None
    preparationSubstrate: str | None = None
    managedAttributes: dict[str, Any] | None = None
    preparationManagedAttributes: dict[str, Any] | None = None
    extensionValues: dict[str, Any] | None = None
    preparationRemarks: str | None = None
    dwcDegreeOfEstablishment: str | None = None
    hierarchy: list[dict[str, Any]] | None = None
    targetOrganismPrimaryScientificName: str | None = None
    targetOrganismPrimaryClassification: dict[str, Any] | None = None
    effectiveScientificName: str | None = None
    barcode: str | None = None
    publiclyReleasable: bool | None = None
    notPubliclyReleasableReason: str | None = None
    tags: list[str] | None = None
    materialSampleState: str | None = None
    materialSampleRemarks: str | None = None
    stateChangedOn: str | None = None
    stateChangeRemarks: str | None = None
    associations: list[Any] | None = None
    allowDuplicateName: bool | None = None
    restrictionFieldsExtension: dict[str, Any] | None = None
    isRestricted: bool | None = None
    restrictionRemarks: str | None = None
    sourceSet: str | None = None
    isBaseForSplitByType: bool | None = None
    identifiers: dict[str, Any] | None = None


MaterialSampleData = JsonApiData[MaterialSampleAttributes]


class MaterialSampleDocument(JsonApiDocument[MaterialSampleAttributes]):
    pass
