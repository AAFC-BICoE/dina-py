"""Tests for the Pydantic-based StorageUnit model."""
import unittest
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from pydantic import ValidationError

from dinapy.schemas.pydantic_base import RelationshipData, RelationshipLinkage
from dinapy.schemas.storage_unit_pydantic import (
    StorageUnitAttributes,
    StorageUnitData,
    StorageUnitDocument,
)

RESPONSE = {
    "data": {
        "id": "019df898-332c-713f-bf63-27309e650bc4",
        "type": "storage-unit",
        "attributes": {
            "createdOn": "2026-05-05T14:46:41.599288Z",
            "createdBy": "dina-admin",
            "name": "Freezer 1",
            "group": "aafc",
            "barcode": "ABC123",
            "isGeneric": False,
            "storageUnitChildren": [{"id": "c1", "type": "storage-unit"}],
            "hierarchy": [{"uuid": "u1", "name": "Freezer 1", "rank": 1}],
            "location": {"id": "p1", "type": "storage-unit"},
        },
        "relationships": {
            "storageUnitType": {"data": {"id": "t1", "type": "storage-unit-type"}},
            "parentStorageUnit": {"data": None},
        },
    }
}


class StorageUnitPydanticTest(unittest.TestCase):

    def test_deserialize_response(self):
        doc = StorageUnitDocument.deserialize(RESPONSE)
        attrs = doc.data.attributes
        self.assertEqual(attrs.name, "Freezer 1")
        self.assertEqual(attrs.barcode, "ABC123")
        self.assertFalse(attrs.isGeneric)
        self.assertEqual(attrs.hierarchy[0]["rank"], 1)
        self.assertEqual(len(attrs.storageUnitChildren), 1)

    def test_deserialize_drops_empty_relationships(self):
        doc = StorageUnitDocument.deserialize(RESPONSE)
        self.assertIn("storageUnitType", doc.data.relationships)
        self.assertNotIn("parentStorageUnit", doc.data.relationships)
        self.assertEqual(doc.data.relationships["storageUnitType"].data.id, "t1")

    def test_deserialize_strips_null_attributes(self):
        resp = {"data": {"id": "1", "type": "storage-unit",
                         "attributes": {"name": "n", "group": "g", "barcode": None}}}
        doc = StorageUnitDocument.deserialize(resp)
        self.assertNotIn("barcode", doc.data.attributes.model_fields_set)

    def test_serialize_only_set_fields(self):
        doc = StorageUnitDocument(
            data=StorageUnitData(
                type="storage-unit",
                attributes=StorageUnitAttributes(name="Shelf", group="aafc"),
            )
        )
        payload = doc.serialize()
        self.assertEqual(payload["data"]["type"], "storage-unit")
        self.assertEqual(payload["data"]["attributes"], {"name": "Shelf", "group": "aafc"})
        self.assertNotIn("relationships", payload["data"])

    def test_serialize_with_relationships(self):
        doc = StorageUnitDocument(
            data=StorageUnitData(
                type="storage-unit",
                attributes=StorageUnitAttributes(name="Shelf", group="aafc"),
                relationships={
                    "storageUnitType": RelationshipData(
                        data=RelationshipLinkage(type="storage-unit-type", id="t1")),
                    "parentStorageUnit": RelationshipData(data=None),
                },
            )
        )
        rels = doc.serialize()["data"]["relationships"]
        self.assertEqual(rels, {"storageUnitType": {"data": {"type": "storage-unit-type", "id": "t1"}}})

    def test_serialize_explicit_null(self):
        doc = StorageUnitDocument(
            data=StorageUnitData(
                id="1",
                type="storage-unit",
                attributes=StorageUnitAttributes(name="Shelf", group="aafc", barcode=None),
            )
        )
        attrs = doc.serialize()["data"]["attributes"]
        self.assertIn("barcode", attrs)
        self.assertIsNone(attrs["barcode"])

    def test_required_fields(self):
        with self.assertRaises(ValidationError):
            StorageUnitAttributes(group="aafc")
        with self.assertRaises(ValidationError):
            StorageUnitAttributes(name="Shelf")


if __name__ == "__main__":
    unittest.main()
