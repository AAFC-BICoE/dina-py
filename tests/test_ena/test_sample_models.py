"""
Comprehensive tests for ENA Sample models and JSON serialization.

Tests verify that Sample models serialize correctly to JSON format
expected by the ENA Webin API v2.
"""

import unittest
import json
from dinapy.ena.models import Sample, Organism, Attribute


class TestOrganismModel(unittest.TestCase):
    """Test the Organism model."""
    
    def test_organism_basic(self):
        """Test basic organism creation."""
        organism = Organism(taxon_id=9606)
        self.assertEqual(organism.taxon_id, 9606)
        self.assertIsNone(organism.scientific_name)
        self.assertIsNone(organism.common_name)
    
    def test_organism_full(self):
        """Test organism with all fields."""
        organism = Organism(
            taxon_id=9606,
            scientific_name="Homo sapiens",
            common_name="human"
        )
        self.assertEqual(organism.taxon_id, 9606)
        self.assertEqual(organism.scientific_name, "Homo sapiens")
        self.assertEqual(organism.common_name, "human")
    
    def test_organism_json_serialization(self):
        """Test organism serializes correctly to JSON with camelCase."""
        organism = Organism(
            taxon_id=1284369,
            scientific_name="stomach metagenome"
        )
        data = organism.model_dump(by_alias=True, exclude_none=True)
        
        self.assertEqual(data["taxonId"], 1284369)
        self.assertEqual(data["scientificName"], "stomach metagenome")
        self.assertNotIn("commonName", data)  # Should be excluded when None


class TestAttributeModel(unittest.TestCase):
    """Test the Attribute model."""
    
    def test_attribute_basic(self):
        """Test basic attribute creation."""
        attr = Attribute(tag="test", value="value")
        self.assertEqual(attr.tag, "test")
        self.assertEqual(attr.value, "value")
        self.assertIsNone(attr.unit)
    
    def test_attribute_with_unit(self):
        """Test attribute with unit."""
        attr = Attribute(
            tag="geographic location (latitude)",
            value="1.81",
            unit="DD"
        )
        self.assertEqual(attr.tag, "geographic location (latitude)")
        self.assertEqual(attr.value, "1.81")
        self.assertEqual(attr.unit, "DD")
    
    def test_attribute_json_serialization(self):
        """Test attribute serializes correctly."""
        attr = Attribute(tag="collection date", value="2024-01-01")
        data = attr.model_dump(by_alias=True, exclude_none=True)
        
        self.assertEqual(data["tag"], "collection date")
        self.assertEqual(data["value"], "2024-01-01")
        self.assertNotIn("unit", data)
    
    def test_attribute_with_unit_json(self):
        """Test attribute with unit serializes correctly."""
        attr = Attribute(tag="temperature", value="25", unit="celsius")
        data = attr.model_dump(by_alias=True, exclude_none=True)
        
        self.assertEqual(data["tag"], "temperature")
        self.assertEqual(data["value"], "25")
        self.assertEqual(data["unit"], "celsius")


class TestSampleModel(unittest.TestCase):
    """Test the Sample model."""
    
    def test_sample_minimal(self):
        """Test minimal sample creation."""
        sample = Sample(
            alias="test_sample",
            organism=Organism(taxon_id=9606),
            attributes=[
                Attribute(tag="collection date", value="2024-01-01")
            ]
        )
        
        self.assertEqual(sample.alias, "test_sample")
        self.assertIsNone(sample.title)
        self.assertEqual(sample.organism.taxon_id, 9606)
        self.assertEqual(len(sample.attributes), 1)
    
    def test_sample_full(self):
        """Test complete sample creation."""
        sample = Sample(
            alias="sample_001",
            title="Test Sample Title",
            organism=Organism(
                taxon_id=410658,
                scientific_name="soil metagenome"
            ),
            description="A test sample description",
            attributes=[
                Attribute(tag="collection date", value="2024-01-15"),
                Attribute(tag="geographic location (country and/or sea)", value="Canada"),
                Attribute(tag="temperature", value="25", unit="celsius")
            ]
        )
        
        self.assertEqual(sample.alias, "sample_001")
        self.assertEqual(sample.title, "Test Sample Title")
        self.assertEqual(sample.description, "A test sample description")
        self.assertEqual(sample.organism.taxon_id, 410658)
        self.assertEqual(len(sample.attributes), 3)
    
    def test_sample_with_links(self):
        """Test sample with optional sample_links."""
        from dinapy.ena.models import Link, XrefLink
        
        sample = Sample(
            alias="linked_sample",
            organism=Organism(taxon_id=9606),
            attributes=[Attribute(tag="test", value="value")],
            sample_links=[
                Link(url="https://example.com/data"),
                Link(xref_link=XrefLink(db="Pubmed", id="12345678"))
            ]
        )
        
        self.assertEqual(len(sample.sample_links), 2)
        self.assertEqual(sample.sample_links[0].url, "https://example.com/data")
        self.assertEqual(sample.sample_links[1].xref_link.db, "Pubmed")
        
        # Test serialization with alias
        data = sample.model_dump(by_alias=True, exclude_none=True)
        self.assertIn("sampleLinks", data)
        self.assertEqual(len(data["sampleLinks"]), 2)
    
    def test_sample_links_optional(self):
        """Test that sample_links is optional and defaults to empty list."""
        sample = Sample(
            alias="no_links",
            organism=Organism(taxon_id=9606),
            attributes=[Attribute(tag="test", value="value")]
        )
        
        self.assertEqual(len(sample.sample_links), 0)
        
        # When serialized without sample_links, it should be excluded
        data = sample.model_dump(by_alias=True, exclude_none=True)
        # Empty lists are not excluded by exclude_none
        self.assertEqual(data.get("sampleLinks", []), [])
    
    def test_sample_json_format(self):
        """Test sample serializes to correct JSON format."""
        sample = Sample(
            alias="stomach_microbiota",
            title="human gastric microbiota, mucosal",
            organism=Organism(taxon_id=1284369),
            attributes=[
                Attribute(tag="investigation type", value="mimarks-survey"),
                Attribute(tag="sequencing method", value="pyrosequencing"),
                Attribute(tag="collection date", value="2010-01-20"),
                Attribute(tag="geographic location (latitude)", value="1.81", unit="DD"),
                Attribute(tag="ena-checklist", value="ERC000014")
            ]
        )
        
        data = sample.model_dump(by_alias=True, exclude_none=True)
        
        # Verify top-level fields
        self.assertEqual(data["alias"], "stomach_microbiota")
        self.assertEqual(data["title"], "human gastric microbiota, mucosal")
        
        # Verify organism structure
        self.assertIn("organism", data)
        self.assertEqual(data["organism"]["taxonId"], 1284369)
        
        # Verify attributes
        self.assertIn("attributes", data)
        self.assertEqual(len(data["attributes"]), 5)
        
        # Check specific attribute
        lat_attr = next(a for a in data["attributes"] 
                       if a["tag"] == "geographic location (latitude)")
        self.assertEqual(lat_attr["value"], "1.81")
        self.assertEqual(lat_attr["unit"], "DD")
    
    def test_sample_json_matches_ena_format(self):
        """Test that sample JSON exactly matches ENA expected format."""
        sample = Sample(
            alias="test_sample",
            title="Test Sample",
            organism=Organism(taxon_id=9606),
            attributes=[
                Attribute(tag="collection date", value="2024-01-01")
            ]
        )
        
        # Create payload as it would be sent to ENA
        payload = {
            "samples": [sample.model_dump(by_alias=True, exclude_none=True)]
        }
        
        # Verify structure
        self.assertIn("samples", payload)
        self.assertEqual(len(payload["samples"]), 1)
        
        sample_data = payload["samples"][0]
        self.assertIn("alias", sample_data)
        self.assertIn("organism", sample_data)
        self.assertIn("taxonId", sample_data["organism"])
        self.assertIn("attributes", sample_data)
        self.assertIsInstance(sample_data["attributes"], list)
    
    def test_sample_full_ena_payload(self):
        """Test complete ENA submission payload format."""
        sample = Sample(
            alias="stomach_microbiota",
            title="human gastric microbiota, mucosal",
            organism=Organism(taxon_id=1284369),
            attributes=[
                Attribute(tag="investigation type", value="mimarks-survey"),
                Attribute(tag="sequencing method", value="pyrosequencing"),
                Attribute(tag="collection date", value="2010-01-20"),
                Attribute(tag="host body site", value="Mucosa of stomach"),
                Attribute(tag="human-associated environmental package", value="human-associated"),
                Attribute(tag="geographic location (latitude)", value="1.81", unit="DD"),
                Attribute(tag="geographic location (longitude)", value="-78.76", unit="DD"),
                Attribute(tag="geographic location (country and/or sea)", value="Colombia"),
                Attribute(tag="geographic location (region and locality)", value="Tumaco"),
                Attribute(tag="environment (biome)", value="coast"),
                Attribute(tag="environment (feature)", value="human-associated habitat"),
                Attribute(tag="project name", value="Human microbiota"),
                Attribute(tag="environment (material)", value="gastric biopsy"),
                Attribute(tag="ena-checklist", value="ERC000014")
            ]
        )
        
        # Build complete submission payload
        payload = {
            "submission": {
                "alias": "sub_test",
                "actions": [{"type": "ADD"}]
            },
            "samples": [sample.model_dump(by_alias=True, exclude_none=True)]
        }
        
        # Verify JSON is valid and structure is correct
        json_str = json.dumps(payload)
        parsed = json.loads(json_str)
        
        self.assertEqual(parsed["samples"][0]["alias"], "stomach_microbiota")
        self.assertEqual(parsed["samples"][0]["organism"]["taxonId"], 1284369)
        self.assertEqual(len(parsed["samples"][0]["attributes"]), 14)


class TestSampleValidation(unittest.TestCase):
    """Test Sample model validation."""
    
    def test_sample_requires_alias(self):
        """Test that sample requires an alias."""
        with self.assertRaises(Exception):  # Pydantic ValidationError
            Sample(
                organism=Organism(taxon_id=9606),
                attributes=[Attribute(tag="test", value="value")]
            )
    
    def test_sample_requires_organism(self):
        """Test that sample requires an organism."""
        with self.assertRaises(Exception):  # Pydantic ValidationError
            Sample(
                alias="test",
                attributes=[Attribute(tag="test", value="value")]
            )
    
    def test_sample_attributes_optional(self):
        """Test that sample attributes are optional (can be empty list)."""
        # Per XSD, SAMPLE_ATTRIBUTES is optional (minOccurs="0")
        sample = Sample(
            alias="test",
            organism=Organism(taxon_id=9606),
            attributes=[]
        )
        self.assertEqual(len(sample.attributes), 0)
    
    def test_organism_requires_taxon_id(self):
        """Test that organism requires a taxon ID."""
        with self.assertRaises(Exception):  # Pydantic ValidationError
            Organism()
    
    def test_attribute_requires_tag_and_value(self):
        """Test that attribute requires both tag and value."""
        with self.assertRaises(Exception):  # Pydantic ValidationError
            Attribute(tag="test")
        
        with self.assertRaises(Exception):  # Pydantic ValidationError
            Attribute(value="value")


if __name__ == "__main__":
    unittest.main()
