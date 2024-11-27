# This file contains tests relating to MolecularAnalysisRunAPI.
# Currently only contains tests for the MolecularAnalysisRunSchema (serialization and deserialization tests).
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
from dinapy.schemas.molecular_analysis_run_schema import MolecularAnalysisRunSchema
from dinapy.entities.MolecularAnalysisRun import *

KEYCLOAK_CONFIG_PATH = "tests/keycloak-config.yml"

VALID_MOLECULAR_ANALYSIS_RUN_DATA = {
  "data": {
    "id": "d35d3e13-49d8-47eb-9536-a6ee7abc7db0",
    "type": "molecular-analysis-run",
    "attributes": {
      "createdBy": "dina-admin",
      "createdOn": "2024-11-25T18:38:17.134466Z",
      "group": "aafc",
      "name": "test run with results"
    }
  },
  "meta": {
    "totalResourceCount": 1,
    "external": [
      {
        "href": "objectstore/api/v1/metadata",
        "type": "metadata"
      }
    ],
    "moduleVersion": "2.17.0"
  }
}

class MolecularAnalysisRunSchemaTest(unittest.TestCase):
    def test_deserealize_molecular_analysis_run(self):
        schema = MolecularAnalysisRunSchema()
        try:
            result = schema.load(VALID_MOLECULAR_ANALYSIS_RUN_DATA)
            pp = pprint.PrettyPrinter(indent=0)
            pp.pprint(result)
            self.assertIsInstance(result, MolecularAnalysisRunDTO)
        except ValidationError as e:
            self.fail(f"Validation failed with error: {e.messages}")

    def test_serialize_molecular_analysis_run(self):
        schema = MolecularAnalysisRunSchema()
        molecular_analysis_run_attributes = MolecularAnalysisRunAttributesDTOBuilder(
          ).set_name("test run with results").set_group("aafc").build()
        molecular_analysis_run = MolecularAnalysisRunDTOBuilder(
          ).set_attributes(molecular_analysis_run_attributes).build()

        try:
          serialized_molecular_analysis_run = schema.dump(molecular_analysis_run)
          expected = {
            "data": {
              "type": "molecular-analysis-run",
              "attributes": {
                "group": "aafc",
                "name": "test run with results"
              }
            }
          }

          pp = pprint.PrettyPrinter(indent=0)
          pp.pprint(serialized_molecular_analysis_run)
          self.assertIsInstance(serialized_molecular_analysis_run, dict)
          self.assertDictEqual(serialized_molecular_analysis_run, expected)
        except ValidationError as e:
          self.fail(f"Validation failed with error: {e.messages}")

if __name__ == "__main__":
    unittest.main()