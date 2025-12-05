
# dinapy/ena/mappers.py
from __future__ import annotations
from typing import Dict, Any, Optional, List
from dinapy.ena.models import Project, ProjectLink, XrefLink, Sample, Organism, Attribute

def project_from_dina_json(dina_project: Dict[str, Any], center_name: str,
                           pubmed_id: Optional[str] = None) -> Project:
    attrs = dina_project["data"]["attributes"]
    alias = dina_project["data"]["id"]

    title = attrs.get("name") or "Untitled Project"
    descs = (attrs.get("multilingualDescription") or {}).get("descriptions") or []
    description = " ".join(d.get("desc") for d in descs if d.get("desc")) or "No description"

    links: List[ProjectLink] = []
    if pubmed_id:
        links.append(ProjectLink(xrefLink=XrefLink(db="PUBMED", id=str(pubmed_id))))

    return Project(
        alias=alias,
        title=title,
        description=description,
        sequencingProject={},   # maps to SUBMISSION_PROJECT → SEQUENCING_PROJECT
        project_links=links,
        attributes=[],
    )

def sample_from_material_sample_json(ms: Dict[str, Any], checklist: Optional[str] = None) -> Sample:
    attrs = ms["data"]["attributes"]
    alias = attrs.get("materialSampleName") or str(attrs.get("dwcCatalogNumber") or ms["data"]["id"])
    title = alias
    taxon_id = int(attrs.get("taxonomyId", 1284369))  # swap with your resolver if present

    attributes = []
    # If DINA provides MIxS fields, just map them through:
    if checklist:
        attributes.append({"tag": "ena-checklist", "value": checklist})

    # e.g., collection date, barcode
    if attrs.get("preparationDate"):
        attributes.append({"tag": "collection date", "value": str(attrs["preparationDate"])})
    if attrs.get("barcode"):
        attributes.append({"tag": "barcode", "value": str(attrs["barcode"])})

    return Sample(
        alias=alias,
        title=title,
        organism=Organism(taxonId=taxon_id),
        attributes=[Attribute(**a) if isinstance(a, dict) else a for a in attributes]
    )
