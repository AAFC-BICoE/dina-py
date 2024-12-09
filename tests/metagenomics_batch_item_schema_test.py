# This file contains tests relating to MetagenomicBatchItemAPI.
# Currently only contains tests for the MetagenomicBatchItemSchema (serialization and deserialization tests).
# API mock call tests should be added.

import unittest

from marshmallow.exceptions import ValidationError

import os
import sys

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.schemas.metagenomics_batch_item_schema import MetagenomicsBatchItemSchema
from dinapy.entities.MetagenomicsBatchItem import *

VALID_METAGENOMICS_BATCH_ITEM_DATA = {
  "data": {
    "id": "019398b3-6251-7dfd-8479-02cf0f2b8f84",
    "type": "metagenomics-batch-item",
    "attributes": {
      "createdBy": "dina-admin",
      "createdOn": "2024-12-05T21:21:53.219363Z"
    },
    "relationships": {
      "metagenomicsBatch": {
        "data": {
          "id": "019398b3-6219-73b9-a822-e12c0ff1e9c6",
          "type": "metagenomics-batch"
        }
      }
    }
  }
}

class MetagenomicsBatchItemSchemaTest(unittest.TestCase):
  def test_deserialize_metagenomics_batch_item(self):
      schema = MetagenomicsBatchItemSchema()
      try:
          result = schema.load(VALID_METAGENOMICS_BATCH_ITEM_DATA)
          print(result.__dict__)
          self.assertIsInstance(result, MetagenomicsBatchItemDTO)
      except ValidationError as e:
          self.fail(f"Validation failed with error: {e.messages}")

  def test_serialize_metagenomics_batch(self):
      schema = MetagenomicsBatchItemSchema()
      metagenomics_batch_item_attributes = MetagenomicsBatchItemAttributesDTOBuilder(
        ).set_name("test").set_createdBy("dina-admin").build()
      metagenomics_batch_item = MetagenomicsBatchItemDTOBuilder(
        ).set_attributes(metagenomics_batch_item_attributes).build()
      
      try:
        serialized_metagenomics_batch_item = schema.dump(metagenomics_batch_item)
        expected = {
          "data": {
            "type": "metagenomics-batch-item",
            "attributes": {
              "name": "test"
            }
          }
        }

        print(serialized_metagenomics_batch_item)
        self.assertIsInstance(serialized_metagenomics_batch_item, dict)
        self.assertDictEqual(serialized_metagenomics_batch_item, expected)
      except ValidationError as e:
          self.fail(f"Validation failed with error: {e.messages}")

if __name__ == "__main__":
  unittest.main()