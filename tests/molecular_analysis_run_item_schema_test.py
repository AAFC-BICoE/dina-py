# This file contains tests relating to MolecularAnalysisRunItemAPI.
# Currently only contains tests for the MolecularAnalysisRunItemSchema (serialization and deserialization tests).
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
from dinapy.schemas.molecular_analysis_run_item_schema import MolecularAnalysisRunItemSchema
from dinapy.entities.MolecularAnalysisRunItem import *

KEYCLOAK_CONFIG_PATH = "tests/keycloak-config.yml"

VALID_MOLECULAR_ANALYSIS_RUN_ITEM_DATA = {
    "data": {
        "id": "0142a2c5-a950-4962-8856-445c7f5770d9",
        "type": "molecular-analysis-run-item",
        "attributes": {
            "createdBy": "dina-admin",
            "createdOn": "2024-11-25T18:51:03.089726Z",
            "usageType": "seq-reaction"
        }
    }
}

class MolecularAnalysisRunSchemaTest(unittest.TestCase):
    def test_deserealize_molecular_analysis_run_item(self):
        schema = MolecularAnalysisRunItemSchema()
        try:
            result = schema.load(VALID_MOLECULAR_ANALYSIS_RUN_ITEM_DATA)
            pp = pprint.PrettyPrinter(indent=0)
            pp.pprint(result)
            self.assertIsInstance(result, MolecularAnalysisRunItemDTO)
        except ValidationError as e:
            self.fail(f"Validation failed with error: {e.messages}")

    def test_serialize_molecular_analysis_run_item(self):
        schema = MolecularAnalysisRunItemSchema()
        molecular_analysis_run_item_attributes = MolecularAnalysisRunItemAttributesDTOBuilder(
          ).set_createdBy("dina-admin").set_usageType("seq-reaction").build()
        molecular_analysis_run_item = MolecularAnalysisRunItemDTOBuilder(
          ).set_attributes(molecular_analysis_run_item_attributes).build()

        try:
          serialized_molecular_analysis_run_item = schema.dump(molecular_analysis_run_item)
          expected = {
            "data": {
              "type": "molecular-analysis-run-item",
              "attributes": {
                "usageType": "seq-reaction"
              }
            }
          }

          pp = pprint.PrettyPrinter(indent=0)
          pp.pprint(serialized_molecular_analysis_run_item)
          self.assertIsInstance(serialized_molecular_analysis_run_item, dict)
          self.assertDictEqual(serialized_molecular_analysis_run_item, expected)
        except ValidationError as e:
          self.fail(f"Validation failed with error: {e.messages}")

if __name__ == "__main__":
    unittest.main()