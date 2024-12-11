# This file contains tests relating to MetagenomicBatchAPI.
# Currently only contains tests for the MetagenomicBatchSchema (serialization and deserialization tests).
# API mock call tests should be added.

import unittest

from marshmallow.exceptions import ValidationError

import os
import sys

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.schemas.metagenomics_batch_schema import MetagenomicsBatchSchema
from dinapy.entities.MetagenomicsBatch import *

VALID_METAGENOMICS_BATCH_DATA = {
  "data": {
    "id": "019398b3-6219-73b9-a822-e12c0ff1e9c6",
    "type": "metagenomics-batch",
    "attributes": {
      "createdBy": "dina-admin",
      "createdOn": "2024-12-05T21:21:53.156284Z",
      "group": "aafc",
      "name": "metagenomics-batch-test"
    },
    "relationships": {
      "indexSet": {
        "data": {
          "id": "456036bc-6fa6-4779-b028-ec26a7b7e6dd",
          "type": "index-set"
        }
      }
    }
  }
}

class MetagenomicsBatchSchemaTest(unittest.TestCase):
  def test_deserialize_metagenomics_batch(self):
    schema = MetagenomicsBatchSchema()
    try:
      result = schema.load(VALID_METAGENOMICS_BATCH_DATA)
      print(result.__dict__)
      self.assertIsInstance(result, MetagenomicsBatchDTO)
    except ValidationError as e:
      self.fail(f"Validation failed with error: {e.messages}")

  def test_serialize_metagenomics_batch(self):
    schema = MetagenomicsBatchSchema()
    metagenomics_batch_attributes = MetagenomicsBatchAttributesDTOBuilder(
      ).set_createdBy("dina-admin").set_group("aafc").set_name("metagenomics-batch-test").build()
    metagenomics_batch = MetagenomicsBatchDTOBuilder(
      ).set_attributes(metagenomics_batch_attributes).build()
      
    try:
      serialized_metagenomics_batch = schema.dump(metagenomics_batch)
      expected = {
        "data": {
          "type": "metagenomics-batch",
          "attributes": {
            "group": "aafc",
            "name": "metagenomics-batch-test"
          }
        }
      }

      print(serialized_metagenomics_batch)
      self.assertIsInstance(serialized_metagenomics_batch, dict)
      self.assertDictEqual(serialized_metagenomics_batch, expected)
    except ValidationError as e:
      self.fail(f"Validation failed with error: {e.messages}")

if __name__ == "__main__":
    unittest.main()