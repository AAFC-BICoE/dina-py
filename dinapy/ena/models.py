from __future__ import annotations
from typing import List, Optional, Dict, Literal, Union, Annotated
from datetime import date
from pydantic import BaseModel, Field, field_validator

class Attribute(BaseModel):
    tag: str
    value: str
    unit: Optional[str] = None

class Action(BaseModel):
    type: Literal["ADD", "HOLD", "RELEASE", "CANCEL"]
    # produce a "pattern" in generated JSON Schema
    holdUntilDate: Optional[Annotated[str, Field(pattern=r'^\d{4}-\d{1,2}-\d{1,2}$')]] = None

    @field_validator("holdUntilDate")
    def validate_hold_until_date(cls, v):
        if v is None or v == "":
            return v
        try:
            d = date.fromisoformat(v)  # strict ISO date normalization
            return d.isoformat()
        except Exception:
            raise ValueError("holdUntilDate must be an ISO date in format YYYY-MM-DD")


class Submission(BaseModel):
    alias: str
    actions: List[Action]
    attributes: List[Attribute] = Field(default_factory=list)

class XrefLink(BaseModel):
    db: str
    id: str

class ProjectLink(BaseModel):
    xrefLink: XrefLink

class Organism(BaseModel):
    # Schema permits either integer or numeric string for taxonId.
    taxonId: Union[int, str]

    @field_validator("taxonId")
    def validate_taxon_id(cls, v):
        # Coerce numeric strings to int; reject non-numeric strings.
        if isinstance(v, str):
            if v.isdigit():
                return int(v)
            raise ValueError("taxonId string must contain only digits")
        return v

class Sample(BaseModel):
    alias: str
    title: str
    organism: Organism
    attributes: List[Attribute]

class Project(BaseModel):
    alias: str
    title: str
    description: str
    # sequencingProject remains optional (default empty dict)
    sequencingProject: Dict = Field(default_factory=dict)
    project_links: List[ProjectLink] = Field(default_factory=list)
    attributes: List[Attribute] = Field(default_factory=list)
    firstPublic: Optional[str] = None  # date format (left as-is)

class WebinPayload(BaseModel):
    submission: Submission
    projects: List[Project] = Field(default_factory=list)
    samples: List[Sample] = Field(default_factory=list)