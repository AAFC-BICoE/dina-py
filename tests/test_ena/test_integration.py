"""
Integration test demonstrating complete ENA submission workflow.

This test shows how to use the models and workflow together.
It uses mocks so it can run without real ENA credentials.
"""

import unittest
from unittest.mock import Mock, patch
import json

from dinapy.ena.models import Sample, Organism, Attribute
from dinapy.ena.submission import ENASubmissionWorkflow
from dinapy.ena.receipt import ENAReceipt, ENAObject


class TestCompleteWorkflow(unittest.TestCase):
    """Integration test showing complete submission workflow."""
    
    def test_complete_sample_submission_workflow(self):
        """
        End-to-end test: Create sample -> Submit -> Parse receipt.
        
        This demonstrates the complete workflow a user would follow.
        """
        # Step 1: Create a Sample model with all required metadata
        sample = Sample(
            alias="stomach_microbiota",
            title="human gastric microbiota, mucosal",
            organism=Organism(
                taxon_id=1284369  # human gut metagenome
            ),
            description="Gastric mucosal sample from Colombian patient",
            attributes=[
                # Required MIxS attributes
                Attribute(tag="investigation type", value="mimarks-survey"),
                Attribute(tag="sequencing method", value="pyrosequencing"),
                Attribute(tag="collection date", value="2010-01-20"),
                
                # Location attributes with units
                Attribute(tag="geographic location (latitude)", value="1.81", unit="DD"),
                Attribute(tag="geographic location (longitude)", value="-78.76", unit="DD"),
                Attribute(tag="geographic location (country and/or sea)", value="Colombia"),
                Attribute(tag="geographic location (region and locality)", value="Tumaco"),
                
                # Environmental context
                Attribute(tag="environment (biome)", value="coast"),
                Attribute(tag="environment (feature)", value="human-associated habitat"),
                Attribute(tag="environment (material)", value="gastric biopsy"),
                
                # Host information
                Attribute(tag="host body site", value="Mucosa of stomach"),
                Attribute(tag="human-associated environmental package", value="human-associated"),
                
                # Project metadata
                Attribute(tag="project name", value="Human microbiota"),
                
                # Checklist
                Attribute(tag="ena-checklist", value="ERC000014")
            ]
        )
        
        # Step 2: Verify the sample model is correct
        self.assertEqual(sample.alias, "stomach_microbiota")
        self.assertEqual(sample.organism.taxon_id, 1284369)
        self.assertEqual(len(sample.attributes), 14)
        
        # Step 3: Verify JSON serialization matches ENA format
        sample_data = sample.model_dump(by_alias=True, exclude_none=True)
        
        # Check structure
        self.assertIn("alias", sample_data)
        self.assertIn("title", sample_data)
        self.assertIn("organism", sample_data)
        self.assertIn("attributes", sample_data)
        
        # Verify organism structure (not sampleName!)
        self.assertEqual(sample_data["organism"]["taxonId"], 1284369)
        
        # Verify attributes structure (not sampleAttributes!)
        self.assertEqual(len(sample_data["attributes"]), 14)
        
        # Check that attributes with units are properly formatted
        lat_attr = next(a for a in sample_data["attributes"] 
                       if a["tag"] == "geographic location (latitude)")
        self.assertEqual(lat_attr["value"], "1.81")
        self.assertEqual(lat_attr["unit"], "DD")
        
        # Step 4: Create submission payload
        payload = {
            "submission": {
                "alias": "sub_stomach_microbiota",
                "actions": [{"type": "ADD"}]
            },
            "samples": [sample_data]
        }
        
        # Verify payload is valid JSON
        json_str = json.dumps(payload, indent=2)
        self.assertIsInstance(json_str, str)
        
        # Parse back to ensure no serialization issues
        parsed = json.loads(json_str)
        self.assertEqual(parsed["samples"][0]["organism"]["taxonId"], 1284369)
        
        # Step 5: Submit using workflow (mocked)
        mock_api = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "accession": "SAMEA123456789",
            "alias": "stomach_microbiota"
        }
        mock_response.headers.get.return_value = "application/json"
        mock_api.post_json.return_value = mock_response
        
        workflow = ENASubmissionWorkflow(
            username="test_user",
            password="test_pass",
            test=True,
            webin_api=mock_api
        )
        
        receipt = workflow.submit_sample(sample)
        
        # Step 6: Verify submission was made with correct payload
        mock_api.post_json.assert_called_once()
        call_args = mock_api.post_json.call_args
        
        submitted_payload = call_args[1]['payload']
        self.assertEqual(submitted_payload['samples'][0]['alias'], 'stomach_microbiota')
        self.assertEqual(
            submitted_payload['samples'][0]['organism']['taxonId'], 
            1284369
        )
        
        # Step 7: Verify receipt (would be parsed from real response)
        self.assertIsInstance(receipt, ENAReceipt)
        
        print("\n" + "="*60)
        print("COMPLETE WORKFLOW TEST PASSED")
        print("="*60)
        print(f"\nSample created: {sample.alias}")
        print(f"Organism: {sample.organism.taxon_id}")
        print(f"Attributes: {len(sample.attributes)} metadata fields")
        print("\nJSON format verified")
        print("Submission workflow verified")
        print("All checks passed")
    
    def test_workflow_with_validation_errors(self):
        """Test that validation errors are caught at model creation time."""
        
        # Missing required field: organism
        with self.assertRaises(Exception) as context:
            Sample(
                alias="invalid_sample",
                attributes=[Attribute(tag="test", value="value")]
            )
        
        # Missing required field: alias
        with self.assertRaises(Exception) as context:
            Sample(
                organism=Organism(taxon_id=9606),
                attributes=[Attribute(tag="test", value="value")]
            )
        
        # Empty attributes list is now allowed (per XSD, SAMPLE_ATTRIBUTES is optional)
        # This should NOT raise an error
        sample = Sample(
            alias="valid_sample_no_attributes",
            organism=Organism(taxon_id=9606),
            attributes=[]
        )
        self.assertEqual(len(sample.attributes), 0)
        
        print("\n" + "="*60)
        print("VALIDATION TEST PASSED")
        print("="*60)
        print("\nPydantic models successfully prevent invalid submissions")
        print("Validation happens at model creation time")
        print("Errors are caught before API calls")


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
