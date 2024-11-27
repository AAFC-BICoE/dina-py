# This file contains tests relating to SeqReactionAPI.
# Currently only contains tests for the SeqReactionSchema (serialization and deserialization tests).
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
from dinapy.schemas.seq_reaction_schema import SeqReactionSchema
from dinapy.entities.SeqReaction import *

KEYCLOAK_CONFIG_PATH = "tests/keycloak-config.yml"

VALID_SEQ_REACTION_DATA = {
  "data": {
      "id": "91fe4965-ef82-41b1-b3ae-cd0457085c1f",
      "type": "seq-reaction",
      "attributes": {
        "createdBy": "dina-admin",
        "createdOn": "2024-11-25T18:51:42.544427Z",
        "group": "aafc"
      }
    },
  "meta": {
    "totalResourceCount": 1,
    "external": [
      {
        "href": "collection/api/v1/storage-unit-usage",
        "type": "storage-unit-usage"
      }
    ],
    "moduleVersion": "2.17.0"
  }
}

class MolecularAnalysisRunSchemaTest(unittest.TestCase):
    def test_deserealize_seq_reaction(self):
        schema = SeqReactionSchema()
        try:
            result = schema.load(VALID_SEQ_REACTION_DATA)
            pp = pprint.PrettyPrinter(indent=0)
            pp.pprint(result)
            self.assertIsInstance(result, SeqReactionDTO)
        except ValidationError as e:
            self.fail(f"Validation failed with error: {e.messages}")

    def test_serialize_seq_reaction(self):
        schema = SeqReactionSchema()
        seq_reaction_attributes = SeqReactionAttributesDTOBuilder(
          ).set_group("aafc").build()
        seq_reaction = SeqReactionDTOBuilder(
          ).set_attributes(seq_reaction_attributes).build()

        try:
          serialized_seq_reaction = schema.dump(seq_reaction)
          expected = {
            "data": {
              "type": "seq-reaction",
              "attributes": {
                "group": "aafc"
              }
            }
          }

          pp = pprint.PrettyPrinter(indent=0)
          pp.pprint(serialized_seq_reaction)
          self.assertIsInstance(serialized_seq_reaction, dict)
          self.assertDictEqual(serialized_seq_reaction, expected)
        except ValidationError as e:
          self.fail(f"Validation failed with error: {e.messages}")

if __name__ == "__main__":
    unittest.main()