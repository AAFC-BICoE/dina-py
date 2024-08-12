import sys
import os
from marshmallow.exceptions import ValidationError
import unittest
import pprint

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.entities.StorageUnitUsage import *
from dinapy.entities.Relationships import *
from dinapy.apis.collectionapi.storageunitusageapi import StorageUnitUsageAPI
from dinapy.schemas.storageunitusageschema import StorageUnitUsage

from dinapy.utils import *
from dinapy.utils import *

os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"


class StorageUnitUsageSchemaTest(unittest.TestCase):
    def test_serialization(self):
        # Create a schema instance and validate the data
        storageUnitId = "0190f065-3d4b-7a6d-be78-a49548922396"
        storageUnitTypeId = "0190f065-3d4b-7a6d-be78-a12432643123"
        relationships = (
            RelationshipDTO.Builder()
            .add_relationship("storageUnit", "storage-unit", storageUnitId)
            .add_relationship("storageUnitType", "storage-unit-type", storageUnitTypeId)
            .build()
        )

        attributes = (
            StorageUnitUsageAttributesDTOBuilder()
            .set_wellColumn(1)
            .set_wellRow("A")
            .set_storageUnitName(None)
            .build()
        )

        dto = (
            StorageUnitUsageDTOBuilder()
            .set_attributes(attributes)
            .set_relationships(relationships)
            .build()
        )

        schema = StorageUnitUsage()

        serialized_storage_unit_usage = schema.dump(dto)
        expected = {
            "data": {
                "type": "storage-unit-usage",
                "attributes": {
                    "wellRow": "A",
                    "wellColumn": 1,
                    "storageUnitName": None,
                },
                "relationships": {
                    "storageUnit": {
                        "data": {
                            "type": "storage-unit",
                            "id": "0190f065-3d4b-7a6d-be78-a49548922396",
                        }
                    },
                    "storageUnitType": {
                        "data": {
                            "type": "storage-unit-type",
                            "id": "0190f065-3d4b-7a6d-be78-a12432643123",
                        }
                    },
                },
            }
        }
        pp = pprint.PrettyPrinter(indent=0)
        pp.pprint(serialized_storage_unit_usage)
        self.assertIsInstance(serialized_storage_unit_usage, dict)
        self.assertDictEqual(serialized_storage_unit_usage, expected)

    def test_deserialization(self):
        data = {
            "data": {
                "id": "01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe",
                "type": "storage-unit-usage",
                "links": {
                    "self": "/api/v1/storage-unit-usage/01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe"
                },
                "attributes": {
                    "wellColumn": 1,
                    "wellRow": "A",
                    "usageType": "material-sample",
                    "cellNumber": 1,
                    "storageUnitName": "Nazir-test",
                    "createdOn": "2024-06-18T21:24:12.320912Z",
                    "createdBy": "elkayssin",
                },
                "relationships": {
                    "storageUnitType": {
                        "links": {
                            "self": "/api/v1/storage-unit-usage/01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe/relationships/storageUnitType",
                            "related": "/api/v1/storage-unit-usage/01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe/storageUnitType",
                        }
                    },
                    "storageUnit": {
                        "links": {
                            "self": "/api/v1/storage-unit-usage/01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe/relationships/storageUnit",
                            "related": "/api/v1/storage-unit-usage/01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe/storageUnit",
                        },
                        "data": {
                            "id": "01902d3a-0ec1-7a57-8284-f4ba3aff1664",
                            "type": "storage-unit",
                        },
                    },
                },
            },
            "meta": {"totalResourceCount": 1, "moduleVersion": "0.91"},
        }

        schema = StorageUnitUsage()

        deserialized_storage_unit_usage = schema.load(data)
        serialized = schema.dump(deserialized_storage_unit_usage)
        pp = pprint.PrettyPrinter(indent=0)
        pp.pprint(deserialized_storage_unit_usage)
        self.assertIsInstance(deserialized_storage_unit_usage, StorageUnitUsageDTO)


if __name__ == "__main__":
    unittest.main()
