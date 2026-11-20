"""Tests for the Pydantic-based StorageUnitType model."""
import unittest
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from pydantic import ValidationError

from dinapy.schemas.storage_unit_type_pydantic import (
    StorageUnitTypeAttributes,
    StorageUnitTypeData,
    StorageUnitTypeDocument,
)

RESPONSE = {
    "data": {
        "id": "019df898-332c-713f-bf63-27309e650bc4",
        "type": "storage-unit-type",
        "attributes": {
            "createdOn": "2026-05-05T14:46:41.599288Z",
            "createdBy": "dina-admin",
            "name": "96 well plate",
            "group": "aafc",
            "isInsertable": True,
            "gridLayoutDefinition": {
                "numberOfRows": 8,
                "numberOfColumns": 12,
                "fillDirection": "BY_ROW",
            },
        },
    }
}


class StorageUnitTypePydanticTest(unittest.TestCase):

    def test_deserialize_response(self):
        doc = StorageUnitTypeDocument.deserialize(RESPONSE)
        attrs = doc.data.attributes
        self.assertEqual(doc.data.id, "019df898-332c-713f-bf63-27309e650bc4")
        self.assertEqual(attrs.name, "96 well plate")
        self.assertEqual(attrs.group, "aafc")
        self.assertTrue(attrs.isInsertable)
        self.assertEqual(attrs.gridLayoutDefinition["numberOfColumns"], 12)
        self.assertIsNone(doc.data.relationships)

    def test_deserialize_strips_nulls(self):
        resp = {"data": {"id": "1", "type": "storage-unit-type",
                         "attributes": {"name": "n", "group": "g", "gridLayoutDefinition": None}}}
        doc = StorageUnitTypeDocument.deserialize(resp)
        self.assertNotIn("gridLayoutDefinition", doc.data.attributes.model_fields_set)

    def test_serialize_only_set_fields(self):
        doc = StorageUnitTypeDocument(
            data=StorageUnitTypeData(
                type="storage-unit-type",
                attributes=StorageUnitTypeAttributes(name="box", group="aafc"),
            )
        )
        payload = doc.serialize()
        self.assertEqual(payload["data"]["type"], "storage-unit-type")
        self.assertEqual(payload["data"]["attributes"], {"name": "box", "group": "aafc"})

    def test_serialize_explicit_null(self):
        doc = StorageUnitTypeDocument(
            data=StorageUnitTypeData(
                id="1",
                type="storage-unit-type",
                attributes=StorageUnitTypeAttributes(
                    name="box", group="aafc", gridLayoutDefinition=None),
            )
        )
        attrs = doc.serialize()["data"]["attributes"]
        self.assertIn("gridLayoutDefinition", attrs)
        self.assertIsNone(attrs["gridLayoutDefinition"])

    def test_required_fields(self):
        with self.assertRaises(ValidationError):
            StorageUnitTypeAttributes(group="aafc")
        with self.assertRaises(ValidationError):
            StorageUnitTypeAttributes(name="box")

    def test_round_trip(self):
        doc = StorageUnitTypeDocument.deserialize(RESPONSE)
        out = doc.serialize()
        self.assertEqual(out["data"]["id"], RESPONSE["data"]["id"])
        self.assertEqual(out["data"]["attributes"]["name"], "96 well plate")


if __name__ == "__main__":
    unittest.main()
