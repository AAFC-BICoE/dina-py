#!/usr/bin/env python3
"""
Manual test script for DINA to ENA mappers using real material sample data.
Run this to verify the mappers work correctly with actual DINA data.
"""

import json
from dinapy.schemas.materialsampleschema import MaterialSampleSchema
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


def test_basic_mapping():
    """Test 1: Basic mapping with provided taxon ID"""
    print("\n" + "="*70)
    print("TEST 1: Basic Mapping with Provided Taxon ID")
    print("="*70)
    
    try:
        # Deserialize the material sample
        schema = MaterialSampleSchema()
        sample_dto = schema.load(MATERIAL_SAMPLE_JSON)
        
        print(f"✓ Successfully deserialized MaterialSample")
        print(f"  ID: {sample_dto.id}")
        print(f"  Type: {sample_dto.type}")
        print(f"  Name: {sample_dto.attributes.get('materialSampleName')}")
        
        # Fusarium poae = NCBI:txid5126
        ena_sample = material_sample_to_ena(
            material_sample=sample_dto,
            taxon_id=5126
        )
        
        print(f"\n✓ Successfully mapped to ENA Sample")
        print(f"  Alias: {ena_sample.alias}")
        print(f"  Title: {ena_sample.title}")
        print(f"  Taxon ID: {ena_sample.organism.taxon_id}")
        print(f"  Attributes: {len(ena_sample.attributes)}")
        
        # Verify
        assert ena_sample.alias == "019b990a-92d7-7f6e-b9c2-b082945672b6"
        assert ena_sample.title == "CHEM1222-3"
        assert ena_sample.organism.taxon_id == 5126
        
        print("\n✓ TEST 1 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scientific_name_extraction():
    """Test 2: Extract scientific name from organism data"""
    print("\n" + "="*70)
    print("TEST 2: Scientific Name Extraction from Organism Data")
    print("="*70)
    
    try:
        schema = MaterialSampleSchema()
        sample_dto = schema.load(MATERIAL_SAMPLE_JSON)
        
        # Extract scientific name using organism data
        scientific_name = extract_scientific_name_from_material_sample(
            sample_dto,
            organism_data=ORGANISM_DATA
        )
        
        print(f"✓ Extracted scientific name: '{scientific_name}'")
        
        # Verify
        assert scientific_name == "Fusarium poae", f"Expected 'Fusarium poae', got '{scientific_name}'"
        
        print("✓ TEST 2 PASSED")
        return True
        
    except Exception as e:
        print(f"✗ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_managed_attributes():
    """Test 3: Extract scientific name from managedAttributes"""
    print("\n" + "="*70)
    print("TEST 3: Scientific Name from managedAttributes")
    print("="*70)
    
    try:
        # Modify sample to have scientific name in managedAttributes
        sample_json = json.loads(json.dumps(MATERIAL_SAMPLE_JSON))
        sample_json["data"]["attributes"]["managedAttributes"] = {
            "scientificName": "Aspergillus niger"
        }
        
        schema = MaterialSampleSchema()
        sample_dto = schema.load(sample_json)
        
        scientific_name = extract_scientific_name_from_material_sample(sample_dto)
        
        print(f"✓ Extracted scientific name: '{scientific_name}'")
        
        # Map to ENA
        ena_sample = material_sample_to_ena(
            material_sample=sample_dto,
            taxon_id=5061  # A. niger = NCBI:txid5061
        )
        
        print(f"✓ Mapped to ENA Sample: {ena_sample.title}")
        print(f"  Taxon ID: {ena_sample.organism.taxon_id}")
        
        print("✓ TEST 3 PASSED")
        return True
        
    except Exception as e:
        print(f"✗ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_checklist():
    """Test 4: Map with ENA checklist"""
    print("\n" + "="*70)
    print("TEST 4: Mapping with ENA Checklist")
    print("="*70)
    
    try:
        schema = MaterialSampleSchema()
        sample_dto = schema.load(MATERIAL_SAMPLE_JSON)
        
        # Map with checklist
        ena_sample = material_sample_to_ena(
            material_sample=sample_dto,
            taxon_id=5126,
            checklist="ERC000011"  # GSC MIxS host associated
        )
        
        # Check for checklist attribute
        checklist_attrs = [
            attr for attr in ena_sample.attributes
            if attr.tag == "ENA-CHECKLIST"
        ]
        
        assert len(checklist_attrs) == 1, "Checklist attribute not found"
        assert checklist_attrs[0].value == "ERC000011"
        
        print(f"✓ Checklist attribute added: {checklist_attrs[0].value}")
        print("✓ TEST 4 PASSED")
        return True
        
    except Exception as e:
        print(f"✗ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fallback_taxon():
    """Test 5: Fallback to environmental sample taxon ID"""
    print("\n" + "="*70)
    print("TEST 5: Fallback to Environmental Sample Taxon")
    print("="*70)
    
    try:
        # Create sample without scientific name
        sample_json = json.loads(json.dumps(MATERIAL_SAMPLE_JSON))
        # No taxon_id provided, no scientific name to resolve
        
        schema = MaterialSampleSchema()
        sample_dto = schema.load(sample_json)
        
        ena_sample = material_sample_to_ena(
            material_sample=sample_dto
            # No taxon_id, no organism_data
        )
        
        # Should fall back to environmental sample
        print(f"✓ Taxon ID: {ena_sample.organism.taxon_id}")
        assert ena_sample.organism.taxon_id == 1284369
        print("✓ Correctly fell back to environmental sample (NCBI:txid1284369)")
        
        print("✓ TEST 5 PASSED")
        return True
        
    except Exception as e:
        print(f"✗ TEST 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  DINA to ENA Mappers - Manual Test Suite")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Basic Mapping", test_basic_mapping()))
    results.append(("Scientific Name Extraction", test_scientific_name_extraction()))
    results.append(("ManagedAttributes", test_with_managed_attributes()))
    results.append(("Checklist", test_with_checklist()))
    results.append(("Fallback Taxon", test_fallback_taxon()))
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
