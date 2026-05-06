"""Tests for the Pydantic-based MaterialSample model."""
import unittest
import json
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.schemas.material_sample_pydantic import (
    MaterialSampleAttributes,
    MaterialSampleData,
    MaterialSampleDocument,
)
from dinapy.schemas.pydantic_base import RelationshipData, RelationshipLinkage

VALID_MATERIAL_SAMPLE_RESPONSE = {
    "data": {
        "id": "019137c0-2027-7bcf-ac92-3844dd80466e",
        "type": "material-sample",
        "attributes": {
            "version": 2,
            "group": "aafc",
            "createdOn": "2024-08-09T15:27:04.476752Z",
            "createdBy": "dina-admin",
            "dwcCatalogNumber": None,
            "dwcOtherCatalogNumbers": None,
            "materialSampleName": None,
            "materialSampleType": None,
            "materialSampleChildren": [],
            "managedAttributes": {},
            "extensionValues": {},
            "publiclyReleasable": True,
            "allowDuplicateName": False,
            "isRestricted": False,
        },
        "relationships": {
            "collectingEvent": {
                "data": {
                    "id": "f08516e5-add2-4baa-89bc-5b8abd0ec8ba",
                    "type": "collecting-event",
                }
            },
            "collection": {
                "links": {
                    "self": "/api/v1/material-sample/019137c0/relationships/collection",
                    "related": "/api/v1/material-sample/019137c0/collection",
                }
            },
            "projects": {
                "links": {
                    "self": "/api/v1/material-sample/019137c0/relationships/projects",
                    "related": "/api/v1/material-sample/019137c0/projects",
                }
            },
        },
    }
}


class MaterialSamplePydanticTest(unittest.TestCase):

    def test_deserialize_api_response(self):
        doc = MaterialSampleDocument.deserialize(VALID_MATERIAL_SAMPLE_RESPONSE)
        print("\n=== MATERIAL SAMPLE DESERIALIZED ===")
        print(json.dumps(doc.model_dump(mode="json"), indent=2))

        self.assertEqual(doc.data.id, "019137c0-2027-7bcf-ac92-3844dd80466e")
        self.assertEqual(doc.data.attributes.group, "aafc")
        self.assertTrue(doc.data.attributes.publiclyReleasable)
        # collectingEvent has data → preserved
        self.assertIsNotNone(doc.data.relationships["collectingEvent"].data)
        self.assertEqual(
            doc.data.relationships["collectingEvent"].data.id,
            "f08516e5-add2-4baa-89bc-5b8abd0ec8ba",
        )
        # links-only relationships → dropped
        self.assertNotIn("collection", doc.data.relationships)
        self.assertNotIn("projects", doc.data.relationships)

    def test_serialize_only_set_fields(self):
        doc = MaterialSampleDocument(
            data=MaterialSampleData(
                type="material-sample",
                attributes=MaterialSampleAttributes(
                    group="aafc",
                    allowDuplicateName=False,
                    isRestricted=False,
                ),
            )
        )
        payload = doc.serialize()
        print("\n=== MATERIAL SAMPLE SERIALIZED ===")
        print(json.dumps(payload, indent=2))

        self.assertEqual(payload["data"]["type"], "material-sample")
        self.assertEqual(payload["data"]["attributes"]["group"], "aafc")
        self.assertFalse(payload["data"]["attributes"]["allowDuplicateName"])
        self.assertNotIn("materialSampleName", payload["data"]["attributes"])
        self.assertNotIn("relationships", payload["data"])

    def test_serialize_with_relationships(self):
        collecting_event_id = "f08516e5-add2-4baa-89bc-5b8abd0ec8ba"
        project_id = "abc123ef-0000-0000-0000-000000000001"

        doc = MaterialSampleDocument(
            data=MaterialSampleData(
                type="material-sample",
                attributes=MaterialSampleAttributes(group="aafc"),
                relationships={
                    "collectingEvent": RelationshipData(
                        data=RelationshipLinkage(
                            type="collecting-event", id=collecting_event_id
                        )
                    ),
                    "projects": RelationshipData(
                        data=[RelationshipLinkage(type="project", id=project_id)]
                    ),
                },
            )
        )
        payload = doc.serialize()
        rels = payload["data"]["relationships"]
        self.assertEqual(rels["collectingEvent"]["data"]["id"], collecting_event_id)
        self.assertEqual(rels["projects"]["data"][0]["id"], project_id)

    def test_relationship_round_trip_does_not_nullify(self):
        """Links-only relationships from GET must not appear in a subsequent request."""
        doc = MaterialSampleDocument.deserialize(VALID_MATERIAL_SAMPLE_RESPONSE)
        payload = doc.serialize()
        # collection and projects were links-only → must be absent
        rels = payload["data"].get("relationships", {})
        self.assertNotIn("collection", rels)
        self.assertNotIn("projects", rels)

    def test_round_trip_null_vs_explicit_null(self):
        """Null attribute values from the API must not leak into a PATCH payload.
        Mutating a field to None after deserialization must appear as null so
        the server clears the field.
        """
        doc = MaterialSampleDocument.deserialize(VALID_MATERIAL_SAMPLE_RESPONSE)
        payload = doc.serialize()
        attrs = payload["data"]["attributes"]

        # These were null in the API response → stripped → must not appear
        self.assertNotIn("dwcCatalogNumber", attrs)
        self.assertNotIn("materialSampleName", attrs)
        self.assertNotIn("materialSampleType", attrs)

        # User explicitly clears a field → must appear as null in PATCH
        doc.data.attributes.materialSampleName = None
        attrs2 = doc.serialize()["data"]["attributes"]
        self.assertIn("materialSampleName", attrs2)
        self.assertIsNone(attrs2["materialSampleName"])


if __name__ == "__main__":
    unittest.main()
