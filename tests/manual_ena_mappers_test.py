"""
Tests for DINA to ENA mappers using fixture material sample data.
"""

import json
import pytest
from dinapy.schemas.material_sample_pydantic import MaterialSampleData
from dinapy.ena.mappers.dina_to_ena.mappers_dto import (
    material_sample_to_ena,
    extract_scientific_name_from_material_sample,
)

# Real material sample from DINA
MATERIAL_SAMPLE_JSON = {
    "data": {
        "id": "019b990a-92d7-7f6e-b9c2-b082945672b6",
        "type": "material-sample",
        "attributes": {
            "version": 0,
            "group": "overy-lab",
            "createdOn": "2026-01-07T15:19:25.635391Z",
            "createdBy": "elkayssin",
            "dwcCatalogNumber": None,
            "dwcOtherCatalogNumbers": None,
            "materialSampleName": "CHEM1222-3",
            "identifiers": {},
            "materialSampleType": None,
            "preparationDate": None,
            "preservationType": None,
            "preparationFixative": None,
            "preparationMaterials": None,
            "preparationSubstrate": None,
            "managedAttributes": {},
            "preparationManagedAttributes": {},
            "extensionValues": {},
            "preparationRemarks": None,
            "dwcDegreeOfEstablishment": None,
            "barcode": None,
            "publiclyReleasable": None,
            "notPubliclyReleasableReason": None,
            "tags": None,
            "materialSampleState": None,
            "materialSampleRemarks": None,
            "stateChangedOn": None,
            "stateChangeRemarks": None,
            "allowDuplicateName": False,
            "restrictionFieldsExtension": {},
            "isRestricted": False,
            "restrictionRemarks": None,
            "sourceSet": "wb_upload_1767799121645",
            "isBaseForSplitByType": None,
            "associations": []
        }
    }
}

ORGANISM_DATA = {
    "data": {
        "id": "019b990a-923e-7bdf-88b8-52332d9e5f92",
        "type": "organism",
        "attributes": {
            "group": "overy-lab",
            "determination": [
                {
                    "verbatimScientificName": "Fusarium poae",
                    "scientificName": None,
                    "isPrimary": True
                }
            ]
        }
    }
}


@pytest.fixture
def sample_dto():
    return MaterialSampleData.model_validate(MATERIAL_SAMPLE_JSON["data"])


def test_basic_mapping(sample_dto):
    """Basic mapping with provided taxon ID"""
    ena_sample = material_sample_to_ena(material_sample=sample_dto, taxon_id=5126)

    assert ena_sample.alias == "019b990a-92d7-7f6e-b9c2-b082945672b6"
    assert ena_sample.title == "CHEM1222-3"
    assert ena_sample.organism.taxon_id == 5126


def test_scientific_name_extraction(sample_dto):
    """Extract scientific name from organism data"""
    scientific_name = extract_scientific_name_from_material_sample(
        sample_dto,
        organism_data=ORGANISM_DATA,
    )

    assert scientific_name == "Fusarium poae"


def test_with_managed_attributes():
    """Extract scientific name from managedAttributes"""
    sample_json = json.loads(json.dumps(MATERIAL_SAMPLE_JSON))
    sample_json["data"]["attributes"]["managedAttributes"] = {"scientificName": "Aspergillus niger"}
    sample_dto = MaterialSampleData.model_validate(sample_json["data"])

    scientific_name = extract_scientific_name_from_material_sample(sample_dto)
    assert scientific_name == "Aspergillus niger"

    ena_sample = material_sample_to_ena(material_sample=sample_dto, taxon_id=5061)
    assert ena_sample.organism.taxon_id == 5061


def test_with_checklist(sample_dto):
    """Map with ENA checklist"""
    ena_sample = material_sample_to_ena(
        material_sample=sample_dto,
        taxon_id=5126,
        checklist="ERC000011",
    )

    checklist_attrs = [attr for attr in ena_sample.attributes if attr.tag == "ENA-CHECKLIST"]
    assert len(checklist_attrs) == 1
    assert checklist_attrs[0].value == "ERC000011"


def test_fallback_taxon():
    """Fallback to environmental sample taxon ID when none provided"""
    sample_dto = MaterialSampleData.model_validate(MATERIAL_SAMPLE_JSON["data"])

    ena_sample = material_sample_to_ena(material_sample=sample_dto)

    assert ena_sample.organism.taxon_id == 1284369

