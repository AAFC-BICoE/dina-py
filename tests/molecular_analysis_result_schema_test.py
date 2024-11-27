# This file contains tests relating to MolecularAnalysisResultAPI.
# Currently only contains tests for the MolecularAnalysisResultSchema (serialization and deserialization tests).
# API mock call tests should be added.

import unittest
import pprint

from marshmallow.exceptions import ValidationError

import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now you can import modules from the dinaapi package
from dinapy.schemas.molecular_analysis_result_schema import MolecularAnalysisResultSchema
from dinapy.entities.MolecularAnalysisResult import *

KEYCLOAK_CONFIG_PATH = "tests/keycloak-config.yml"

VALID_MOLECULAR_ANALYSIS_RESULT_DATA = {
  "data": {
    "id": "018fe165-12f0-417d-895b-39f84222b26d",
    "type": "molecular-analysis-result",
    "attributes": {
      "createdBy": "dina-admin",
      "createdOn": "2024-11-25T18:38:17.134466Z",
      "group": "aafc"
    }
  }
}

class MolecularAnalysisRunSchemaTest(unittest.TestCase):
    def test_deserealize_molecular_analysis_result(self):
        schema = MolecularAnalysisResultSchema()
        try:
            result = schema.load(VALID_MOLECULAR_ANALYSIS_RESULT_DATA)
            pp = pprint.PrettyPrinter(indent=0)
            pp.pprint(result)
            self.assertIsInstance(result, MolecularAnalysisResultDTO)
        except ValidationError as e:
            self.fail(f"Validation failed with error: {e.messages}")

    def test_serialize_molecular_analysis_result(self):
        schema = MolecularAnalysisResultSchema()
        molecular_analysis_result_attributes = MolecularAnalysisResultAttributesDTOBuilder(
          ).set_group("aafc").build()
        molecular_analysis_result = MolecularAnalysisResultDTOBuilder(
          ).set_attributes(molecular_analysis_result_attributes).build()

        try:
          serialized_molecular_analysis_result = schema.dump(molecular_analysis_result)
          expected = {
            "data": {
              "type": "molecular-analysis-result",
              "attributes": {
                "group": "aafc"
              }
            }
          }

          pp = pprint.PrettyPrinter(indent=0)
          pp.pprint(serialized_molecular_analysis_result)
          self.assertIsInstance(serialized_molecular_analysis_result, dict)
          self.assertDictEqual(serialized_molecular_analysis_result, expected)
        except ValidationError as e:
          self.fail(f"Validation failed with error: {e.messages}")

if __name__ == "__main__":
    unittest.main()