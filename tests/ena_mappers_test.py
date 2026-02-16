"""
Tests for DINA to ENA mappers using real material sample data.
"""
import pytest
import copy
from unittest.mock import patch, MagicMock
from dinapy.schemas.materialsampleschema import MaterialSampleSchema
from dinapy.schemas.collectingeventschema import CollectingEventSchema
from dinapy.schemas.project_schema import ProjectSchema
from dinapy.ena.mappers.dina_to_ena.mappers_dto import (
    material_sample_to_ena,
    extract_scientific_name_from_material_sample,
    resolve_taxon_id_from_scientific_name,
    batch_material_samples_to_ena,
    project_to_ena,
    safe_get_attr,
    get_managed_attribute,
    extract_unmapped_attributes
)
from dinapy.ena.models import Sample, Organism, Attribute


# =============================================================================
# TEST DATA - Real Material Sample from DINA
# =============================================================================

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
            "hierarchy": [
                {
                    "uuid": "019b990a-92d7-7f6e-b9c2-b082945672b6",
                    "name": "CHEM1222-3",
                    "rank": 1,
                    "organismPrimaryDetermination": [
                        {
                            "verbatimScientificName": "Fusarium poae",
                            "scientificNameDetails": {}
                        }
                    ]
                }
            ],
            "targetOrganismPrimaryScientificName": "Fusarium poae",
            "targetOrganismPrimaryClassification": {
                "phylum": "Ascomycota",
                "genus": "Fusarium",
                "species": "poae",
                "family": "Nectriaceae",
                "kingdom": "Fungi",
                "class": "Sordariomycetes",
                "order": "Hypocreales"
            },
            "effectiveScientificName": "Fusarium poae",
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
        },
        "relationships": {
            "projects": {
                "data": []
            },
            "organism": {
                "data": [
                    {
                        "id": "019b990a-923e-7bdf-88b8-52332d9e5f92",
                        "type": "organism"
                    }
                ]
            },
            "assemblages": {
                "data": []
            }
        }
    }
}

ORGANISM_DATA = {
    "data": {
        "id": "019b990a-923e-7bdf-88b8-52332d9e5f92",
        "type": "organism",
        "attributes": {
            "group": "overy-lab",
            "isTarget": None,
            "lifeStage": None,
            "sex": None,
            "remarks": None,
            "dwcVernacularName": None,
            "managedAttributes": {},
            "determination": [
                {
                    "verbatimScientificName": "Fusarium poae",
                    "verbatimDeterminer": None,
                    "verbatimDate": None,
                    "scientificName": None,
                    "transcriberRemarks": None,
                    "verbatimRemarks": None,
                    "determinationRemarks": None,
                    "typeStatus": None,
                    "typeStatusEvidence": None,
                    "determiner": None,
                    "determinedOn": None,
                    "qualifier": None,
                    "scientificNameSource": "CUSTOM",
                    "scientificNameDetails": {
                        "labelHtml": None,
                        "classificationPath": "Fungi|Ascomycota|Sordariomycetes|Hypocreales|Nectriaceae|Fusarium|poae",
                        "classificationRanks": "kingdom|phylum|class|order|family|genus|species",
                        "sourceUrl": None,
                        "recordedOn": None,
                        "currentName": None,
                        "isSynonym": None
                    },
                    "isPrimary": True,
                    "isFiledAs": None,
                    "managedAttributes": None
                }
            ],
            "createdOn": "2026-01-07T15:19:25.503522Z",
            "createdBy": "elkayssin"
        }
    }
}

COLLECTING_EVENT_JSON = {
    "data": {
        "id": "019b990a-test-collecting-event",
        "type": "collecting-event",
        "attributes": {
            "group": "overy-lab",
            "dwcCountry": "Canada",
            "dwcStateProvince": "Ontario",
            "dwcVerbatimLocality": "Ottawa",
            "endEventDateTime": "2025-12-15T00:00:00.000Z",
            "startEventDateTime": "2025-12-15T00:00:00.000Z",
            "managedAttributes": {}
        }
    }
}


# =============================================================================
# TEST: Scientific Name Extraction
# =============================================================================

class TestScientificNameExtraction:
    """Test extraction of scientific names from various sources."""
    
    def test_extract_from_effective_scientific_name(self):
        """Test extraction from effectiveScientificName attribute."""
        schema = MaterialSampleSchema()
        sample_dto = schema.load(MATERIAL_SAMPLE_JSON)
        
        scientific_name = extract_scientific_name_from_material_sample(sample_dto)
        
        assert scientific_name == "Fusarium poae"
    
    def test_extract_from_organism_data(self):
        """Test extraction from organism relationship data."""
        # Create a sample without effectiveScientificName
        sample_json = copy.deepcopy(MATERIAL_SAMPLE_JSON)
        sample_json["data"]["attributes"]["effectiveScientificName"] = None
        sample_json["data"]["attributes"]["targetOrganismPrimaryScientificName"] = None
        
        schema = MaterialSampleSchema()
        sample_dto = schema.load(sample_json)
        
        scientific_name = extract_scientific_name_from_material_sample(
            sample_dto,
            organism_data=ORGANISM_DATA
        )
        
        assert scientific_name == "Fusarium poae"
    
    def test_extract_from_managed_attributes(self):
        """Test extraction from managedAttributes."""
        sample_json = copy.deepcopy(MATERIAL_SAMPLE_JSON)
        sample_json["data"]["attributes"]["effectiveScientificName"] = None
        sample_json["data"]["attributes"]["targetOrganismPrimaryScientificName"] = None
        sample_json["data"]["attributes"]["managedAttributes"] = {
            "scientificName": "Aspergillus niger"
        }
        
        schema = MaterialSampleSchema()
        sample_dto = schema.load(sample_json)
        
        scientific_name = extract_scientific_name_from_material_sample(sample_dto)
        
        assert scientific_name == "Aspergillus niger"


# =============================================================================
# TEST: Material Sample to ENA Sample Mapping
# =============================================================================

class TestMaterialSampleToENA:
    """Test mapping of MaterialSample DTOs to ENA Sample models."""
    
    def test_basic_mapping_with_provided_taxon_id(self):
        """Test basic mapping with a pre-provided taxon ID."""
        schema = MaterialSampleSchema()
        sample_dto = schema.load(MATERIAL_SAMPLE_JSON)
        
        # Map with provided taxon ID (Fusarium poae = 5126)
        ena_sample = material_sample_to_ena(
            material_sample=sample_dto,
            taxon_id=5126
        )
        
        # Verify basic fields
        assert isinstance(ena_sample, Sample)
        assert ena_sample.alias == "019b990a-92d7-7f6e-b9c2-b082945672b6"
        assert ena_sample.title == "CHEM1222-3"
        assert ena_sample.organism.taxon_id == 5126
    
    def test_mapping_with_collecting_event(self):
        """Test mapping with collecting event data."""
        schema = MaterialSampleSchema()
        ce_schema = CollectingEventSchema()
        
        sample_dto = schema.load(MATERIAL_SAMPLE_JSON)
        ce_dto = ce_schema.load(COLLECTING_EVENT_JSON)
        
        ena_sample = material_sample_to_ena(
            material_sample=sample_dto,
            collecting_event=ce_dto,
            taxon_id=5126
        )
        
        # Check that collection date and geographic location are added
        attr_tags = [attr.tag for attr in ena_sample.attributes]
        assert "collection date" in attr_tags
        assert "geographic location (country and/or sea)" in attr_tags
        
        # Check geographic location value
        geo_attr = next(
            attr for attr in ena_sample.attributes
            if attr.tag == "geographic location (country and/or sea)"
        )
        assert "Canada" in geo_attr.value
        assert "Ontario" in geo_attr.value
    
    def test_mapping_with_checklist(self):
        """Test mapping with ENA checklist."""
        schema = MaterialSampleSchema()
        sample_dto = schema.load(MATERIAL_SAMPLE_JSON)
        
        ena_sample = material_sample_to_ena(
            material_sample=sample_dto,
            taxon_id=5126,
            checklist="ERC000011"
        )
        
        # Check checklist attribute
        checklist_attrs = [
            attr for attr in ena_sample.attributes
            if attr.tag == "ENA-CHECKLIST"
        ]
        assert len(checklist_attrs) == 1
        assert checklist_attrs[0].value == "ERC000011"
    
    @patch('dinapy.ena.mappers.dina_to_ena.mappers_dto.resolve_taxon_id_from_scientific_name')
    def test_auto_resolve_taxon_id(self, mock_resolve):
        """Test automatic taxon ID resolution."""
        # Mock the NCBI API call
        mock_resolve.return_value = 5126  # Fusarium poae
        
        schema = MaterialSampleSchema()
        sample_dto = schema.load(MATERIAL_SAMPLE_JSON)
        
        # Don't provide taxon_id - should auto-resolve
        ena_sample = material_sample_to_ena(
            material_sample=sample_dto,
            email="test@example.com"
        )
        
        # Verify the resolver was called
        mock_resolve.assert_called_once()
        call_args = mock_resolve.call_args
        assert call_args[0][0] == "Fusarium poae"
        
        # Verify the taxon ID was set
        assert ena_sample.organism.taxon_id == 5126
    
    def test_fallback_to_environmental_sample(self):
        """Test fallback to environmental sample taxon ID."""
        # Create sample without scientific name
        sample_json = copy.deepcopy(MATERIAL_SAMPLE_JSON)
        sample_json["data"]["attributes"]["effectiveScientificName"] = None
        sample_json["data"]["attributes"]["targetOrganismPrimaryScientificName"] = None
        sample_json["data"]["attributes"]["managedAttributes"] = {}
        
        schema = MaterialSampleSchema()
        sample_dto = schema.load(sample_json)
        
        ena_sample = material_sample_to_ena(
            material_sample=sample_dto
            # No taxon_id provided, no scientific name to resolve
        )
        
        # Should fall back to environmental sample
        assert ena_sample.organism.taxon_id == 1284369


# =============================================================================
# TEST: Taxonomy Resolution with NCBI
# =============================================================================

class TestTaxonomyResolution:
    """Test NCBI taxonomy ID resolution."""
    
    @patch('dinapy.ena.mappers.dina_to_ena.mappers_dto.requests.get')
    def test_successful_resolution(self, mock_get):
        """Test successful taxon ID resolution from NCBI."""
        # Mock NCBI API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "esearchresult": {
                "idlist": ["5126"]  # Fusarium poae
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        taxon_id = resolve_taxon_id_from_scientific_name(
            "Fusarium poae",
            email="test@example.com"
        )
        
        assert taxon_id == 5126
        
        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]['params']['db'] == 'taxonomy'
        assert call_args[1]['params']['term'] == 'Fusarium poae'
        assert call_args[1]['params']['email'] == 'test@example.com'
    
    @patch('dinapy.ena.mappers.dina_to_ena.mappers_dto.requests.get')
    def test_not_found(self, mock_get):
        """Test handling when taxon is not found."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "esearchresult": {
                "idlist": []  # Not found
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        taxon_id = resolve_taxon_id_from_scientific_name(
            "Nonexistent species",
            email="test@example.com"
        )
        
        assert taxon_id is None
    
    @patch('dinapy.ena.mappers.dina_to_ena.mappers_dto.requests.get')
    def test_network_error(self, mock_get):
        """Test handling of network errors."""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        taxon_id = resolve_taxon_id_from_scientific_name(
            "Fusarium poae",
            email="test@example.com"
        )
        
        # Should return None without crashing
        assert taxon_id is None
    
    def test_caching(self):
        """Test that caching prevents duplicate API calls."""
        cache = {}
        
        with patch('dinapy.ena.mappers.dina_to_ena.mappers_dto.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "esearchresult": {"idlist": ["5126"]}
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            # First call - should hit API
            taxon_id1 = resolve_taxon_id_from_scientific_name(
                "Fusarium poae",
                cache=cache
            )
            
            # Second call - should use cache
            taxon_id2 = resolve_taxon_id_from_scientific_name(
                "Fusarium poae",
                cache=cache
            )
            
            assert taxon_id1 == 5126
            assert taxon_id2 == 5126
            
            # API should only be called once
            assert mock_get.call_count == 1
            
            # Cache should contain the result
            assert cache["Fusarium poae"] == 5126


# =============================================================================
# TEST: Batch Mapping
# =============================================================================

class TestBatchMapping:
    """Test batch mapping of multiple samples."""
    
    @patch('dinapy.ena.mappers.dina_to_ena.mappers_dto.resolve_taxon_id_from_scientific_name')
    def test_batch_with_auto_resolve(self, mock_resolve):
        """Test batch mapping with auto-resolution."""
        # Create a cache-aware mock that mimics caching behavior
        call_count = {'count': 0}
        cache = {}
        
        def cache_aware_resolve(scientific_name, email=None, cache=None):
            # Only increment if not in provided cache
            if cache is None or scientific_name not in cache:
                call_count['count'] += 1
            # Populate cache if provided
            if cache is not None:
                cache[scientific_name] = 5126
            return 5126
        
        mock_resolve.side_effect = cache_aware_resolve
        
        # Create multiple samples with same scientific name
        schema = MaterialSampleSchema()
        sample1 = schema.load(MATERIAL_SAMPLE_JSON)
        
        sample2_json = copy.deepcopy(MATERIAL_SAMPLE_JSON)
        sample2_json["data"]["id"] = "sample-2"
        sample2_json["data"]["attributes"]["materialSampleName"] = "CHEM1222-4"
        sample2 = schema.load(sample2_json)
        
        samples = [sample1, sample2]
        
        # Batch map
        ena_samples = batch_material_samples_to_ena(
            material_samples=samples,
            email="test@example.com",
            auto_resolve_taxa=True
        )
        
        assert len(ena_samples) == 2
        assert all(isinstance(s, Sample) for s in ena_samples)
        assert all(s.organism.taxon_id == 5126 for s in ena_samples)
        
        # Should only call once due to caching (second call finds it in cache)
        assert call_count['count'] == 1


# =============================================================================
# TEST: Utility Functions
# =============================================================================

class TestUtilityFunctions:
    """Test utility helper functions."""
    
    def test_safe_get_attr(self):
        """Test safe attribute getter."""
        class TestObj:
            value = "test"
            undefined = "undefined"
            none_value = None
        
        obj = TestObj()
        
        assert safe_get_attr(obj, 'value') == "test"
        assert safe_get_attr(obj, 'undefined', 'default') == 'default'
        assert safe_get_attr(obj, 'none_value', 'default') == 'default'
        assert safe_get_attr(obj, 'missing', 'default') == 'default'
    
    def test_get_managed_attribute(self):
        """Test managed attribute extraction."""
        class TestAttrs:
            managedAttributes = {"key1": "value1", "key2": "undefined"}
            preparationManagedAttributes = {"key3": "value3"}
        
        attrs = TestAttrs()
        
        assert get_managed_attribute(attrs, 'key1') == "value1"
        assert get_managed_attribute(attrs, 'key2', 'default') == 'default'
        assert get_managed_attribute(attrs, 'key3') == "value3"
        assert get_managed_attribute(attrs, 'missing', 'default') == 'default'


# =============================================================================
# TEST: Unmapped Attributes
# =============================================================================

class TestUnmappedAttributes:
    """Test automatic extraction of unmapped attributes as generic ENA attributes."""
    
    def test_extract_unmapped_attributes_basic(self):
        """Test basic unmapped attribute extraction."""
        # Test with a dict (simpler case)
        attrs_dict = {
            'name': 'Test Name',
            'description': 'Test Description',
            'customField': 'Custom Value',
            'anotherField': 123,
            'noneField': None,
            'undefinedField': 'undefined'
        }
        
        mapped_keys = {'name', 'description'}
        
        unmapped = extract_unmapped_attributes(attrs_dict, mapped_keys, include_managed=False)
        
        # Should extract customField and anotherField, but not noneField or undefinedField
        tags = {attr.tag for attr in unmapped}
        assert 'customField' in tags
        assert 'anotherField' in tags
        assert 'noneField' not in tags
        assert 'undefinedField' not in tags
        assert 'name' not in tags  # explicitly mapped
        assert 'description' not in tags  # explicitly mapped
    
    def test_extract_unmapped_with_managed_attributes(self):
        """Test extraction including managedAttributes."""
        attrs_dict = {
            'name': 'Test',
            'managedAttributes': {
                'customKey': 'customValue',
                'anotherKey': 'anotherValue'
            },
            'preparationManagedAttributes': {
                'prepKey': 'prepValue'
            }
        }
        
        mapped_keys = {'name'}
        
        unmapped = extract_unmapped_attributes(attrs_dict, mapped_keys, include_managed=True)
        
        tags = {attr.tag for attr in unmapped}
        assert 'managed_customKey' in tags
        assert 'managed_anotherKey' in tags
        assert 'prep_prepKey' in tags
    
    def test_material_sample_unmapped_attributes(self):
        """Test unmapped attributes in material sample mapping."""
        # Create a sample with extra unmapped fields in managedAttributes
        sample_json = copy.deepcopy(MATERIAL_SAMPLE_JSON)
        sample_json["data"]["attributes"]["managedAttributes"] = {
            "habitat": "forest",
            "temperature": "25C",
            "customField1": "Custom Value 1"
        }
        
        schema = MaterialSampleSchema()
        sample_dto = schema.load(sample_json)
        
        ena_sample = material_sample_to_ena(
            material_sample=sample_dto,
            taxon_id=5126,
            include_unmapped=True
        )
        
        # Check that unmapped attributes are present
        attr_tags = {attr.tag for attr in ena_sample.attributes}
        
        # Should have managed attributes
        assert 'managed_habitat' in attr_tags
        assert 'managed_temperature' in attr_tags
        assert 'managed_customField1' in attr_tags
    
    def test_material_sample_without_unmapped_attributes(self):
        """Test that unmapped attributes can be disabled."""
        sample_json = copy.deepcopy(MATERIAL_SAMPLE_JSON)
        sample_json["data"]["attributes"]["managedAttributes"] = {
            "customField1": "Custom Value 1"
        }
        
        schema = MaterialSampleSchema()
        sample_dto = schema.load(sample_json)
        
        ena_sample = material_sample_to_ena(
            material_sample=sample_dto,
            taxon_id=5126,
            include_unmapped=False
        )
        
        # Should not have custom fields from managedAttributes
        attr_tags = {attr.tag for attr in ena_sample.attributes}
        assert 'managed_customField1' not in attr_tags
    
    def test_collecting_event_unmapped_attributes(self):
        """Test that collecting event unmapped attributes are prefixed with 'ce_'."""
        ce_json = copy.deepcopy(COLLECTING_EVENT_JSON)
        ce_json["data"]["attributes"]["managedAttributes"] = {
            "habitat": "woodland",
            "elevation": "500m"
        }
        
        schema = MaterialSampleSchema()
        ce_schema = CollectingEventSchema()
        
        sample_dto = schema.load(MATERIAL_SAMPLE_JSON)
        ce_dto = ce_schema.load(ce_json)
        
        ena_sample = material_sample_to_ena(
            material_sample=sample_dto,
            collecting_event=ce_dto,
            taxon_id=5126,
            include_unmapped=True
        )
        
        # Check that collecting event unmapped attributes are prefixed
        attr_tags = {attr.tag for attr in ena_sample.attributes}
        assert 'ce_managed_habitat' in attr_tags
        assert 'ce_managed_elevation' in attr_tags
    
    def test_project_unmapped_attributes(self):
        """Test unmapped attributes in project mapping."""
        project_json = {
            "data": {
                "id": "test-project-123",
                "type": "project",
                "attributes": {
                    "name": "Test Project",
                    "multilingualDescription": {
                        "descriptions": [
                            {"desc": "A test project", "lang": "en"}
                        ]
                    },
                    "startDate": "2025-01-01",
                    "endDate": "2026-12-31",
                    "status": "Active",
                    "extensionValues": {
                        "fundingAgency": "NSF",
                        "grantNumber": "12345"
                    }
                }
            }
        }
        
        schema = ProjectSchema()
        project_dto = schema.load(project_json)
        
        ena_project = project_to_ena(
            project=project_dto,
            include_unmapped=True
        )
        
        # Check that unmapped attributes are present (startDate, endDate, status)
        attr_tags = {attr.tag for attr in ena_project.attributes}
        assert 'startDate' in attr_tags
        assert 'endDate' in attr_tags
        assert 'status' in attr_tags
    
    def test_complex_nested_objects_excluded(self):
        """Test that complex nested objects are excluded from unmapped attributes."""
        attrs_dict = {
            'simpleString': 'value',
            'simpleNumber': 123,
            'nestedDict': {'key': 'value', 'nested': {'deep': 'value'}},
            'nestedList': ['item1', 'item2']
        }
        
        unmapped = extract_unmapped_attributes(attrs_dict, set(), include_managed=False)
        
        tags = {attr.tag for attr in unmapped}
        
        # Simple types should be included
        assert 'simpleString' in tags
        assert 'simpleNumber' in tags
        
        # Complex nested objects should be excluded
        assert 'nestedDict' not in tags
        assert 'nestedList' not in tags


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
