"""Tests for the Pydantic-based Association model."""
import unittest
import json
import sys
import os
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.schemas.association_pydantic import (
    AssociationAttributes,
    AssociationData,
    AssociationDocument,
)

VALID_ASSOCIATION_SINGLE_RESPONSE = {
    "data": {
        "id": "019df898-332c-713f-bf63-27309e650bc4",
        "type": "association",
        "attributes": {
            "createdOn": "2026-05-05T14:46:41.599288Z",
            "createdBy": "dina-admin",
            "associationType": "has_host",
            "remarks": "test remark",
        },
    }
}


class AssociationPydanticTest(unittest.TestCase):

    # ── Single deserialization ─────────────────────────────────────────────────

    def test_deserialize_single_response(self):
        doc = AssociationDocument.deserialize(VALID_ASSOCIATION_SINGLE_RESPONSE)
        self.assertEqual(doc.data.id, "019df898-332c-713f-bf63-27309e650bc4")
        self.assertEqual(doc.data.attributes.associationType, "has_host")
        self.assertIsNone(doc.data.relationships)

    # ── Serialization ─────────────────────────────────────────────────────────

    def test_serialize_only_set_fields(self):
        doc = AssociationDocument(
            data=AssociationData(
                type="association",
                attributes=AssociationAttributes(
                    associationType="has_host",
                    remarks="test remark",
                ),
            )
        )
        payload = doc.serialize()
        attrs = payload["data"]["attributes"]
        self.assertEqual(payload["data"]["type"], "association")
        self.assertEqual(attrs["associationType"], "has_host")
        self.assertEqual(attrs["remarks"], "test remark")
        # Unset fields must not appear in the payload
        self.assertNotIn("createdBy", attrs)
        self.assertNotIn("createdOn", attrs)
        self.assertNotIn("relationships", payload["data"])

    def test_serialize_excludes_none_fields(self):
        doc = AssociationDocument(
            data=AssociationData(
                type="association",
                attributes=AssociationAttributes(
                    associationType="parasitizes",
                ),
            )
        )
        payload = doc.serialize()
        self.assertNotIn("remarks", payload["data"]["attributes"])

    # ── Round-trip ────────────────────────────────────────────────────────────

    def test_round_trip_single(self):
        """Deserialize → re-serialize should produce a clean PATCH payload."""
        doc = AssociationDocument.deserialize(VALID_ASSOCIATION_SINGLE_RESPONSE)
        payload = doc.serialize()
        self.assertEqual(payload["data"]["id"], "019df898-332c-713f-bf63-27309e650bc4")
        self.assertEqual(payload["data"]["attributes"]["associationType"], "has_host")
        self.assertNotIn("relationships", payload["data"])


if __name__ == "__main__":
    unittest.main()
