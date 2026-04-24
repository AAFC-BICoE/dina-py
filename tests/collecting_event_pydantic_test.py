"""
Tests for the Pydantic-based CollectingEvent model.
Mirrors collecting_event_schema_test.py to allow direct before/after comparison.
"""
import unittest
import json
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.schemas.collecting_event_pydantic import (
    CollectingEventAttributes,
    CollectingEventData,
    CollectingEventDocument,
)
from dinapy.schemas.pydantic_base import RelationshipData, RelationshipLinkage

# Sample API response (same data as collecting_event_schema_test.py)
VALID_COLLECTING_EVENT_RESPONSE = {
    "data": {
        "id": "f08516e5-add2-4baa-89bc-5b8abd0ec8ba",
        "type": "collecting-event",
        "attributes": {
            "version": 0,
            "dwcFieldNumber": None,
            "dwcRecordNumber": None,
            "group": "phillips-lab",
            "createdBy": "s-seqdbsoil",
            "createdOn": "2024-01-26T17:09:33.932301Z",
            "geoReferenceAssertions": [
                {
                    "dwcDecimalLatitude": 44.2,
                    "dwcDecimalLongitude": -80.7,
                    "isPrimary": True,
                }
            ],
            "eventGeom": {"type": "Point", "coordinates": [-80.7, 44.2]},
            "dwcVerbatimCoordinates": "44.2 -80.7",
            "startEventDateTime": "2017-08-07",
            "managedAttributes": {"site_codes": "BS"},
            "substrate": "Soil",
            "remarks": "Blocks of soil kept intact and on ice until transport back to lab",
            "publiclyReleasable": None,
        },
        "relationships": {
            "collectionMethod": {
                "data": {
                    "id": "01902d3a-0ec1-7a57-8284-f4ba3aff1664",
                    "type": "collection-method",
                }
            },
            "protocol": {
                "links": {
                    "self": "/api/v1/collecting-event/f08516e5/relationships/protocol"
                }
            },
        },
    }
}


class CollectingEventPydanticTest(unittest.TestCase):

    def test_deserialize_api_response(self):
        """Parse a full API response into a typed model."""
        doc = CollectingEventDocument.deserialize(VALID_COLLECTING_EVENT_RESPONSE)
        print("\n=== DESERIALIZED ===")
        print(json.dumps(doc.model_dump(mode="json"), indent=2))

        self.assertEqual(doc.data.id, "f08516e5-add2-4baa-89bc-5b8abd0ec8ba")
        self.assertEqual(doc.data.type, "collecting-event")
        self.assertEqual(doc.data.attributes.group, "phillips-lab")
        self.assertEqual(doc.data.attributes.startEventDateTime, "2017-08-07")
        self.assertIsNone(doc.data.attributes.publiclyReleasable)
        # relationship with data → parsed
        self.assertIsNotNone(doc.data.relationships["collectionMethod"].data)
        self.assertEqual(
            doc.data.relationships["collectionMethod"].data.id,
            "01902d3a-0ec1-7a57-8284-f4ba3aff1664",
        )

    def test_serialize_only_set_fields(self):
        """Only explicitly set fields appear in the request payload —
        no 'undefined' sentinel or SkipUndefinedField needed."""
        doc = CollectingEventDocument(
            data=CollectingEventData(
                type="collecting-event",
                attributes=CollectingEventAttributes(group="aafc"),
            )
        )
        payload = doc.serialize()
        print("\n=== SERIALIZED (only set fields) ===")
        print(json.dumps(payload, indent=2))

        self.assertEqual(payload["data"]["type"], "collecting-event")
        self.assertEqual(payload["data"]["attributes"]["group"], "aafc")
        # Unset fields must be absent — not None, not null
        self.assertNotIn("habitat", payload["data"]["attributes"])
        self.assertNotIn("startEventDateTime", payload["data"]["attributes"])
        self.assertNotIn("relationships", payload["data"])

    def test_serialize_with_relationships(self):
        """Relationships are serialized correctly for both single and many."""
        protocol_id = "8f68a05f-937d-4d40-88b4-ed92720d9c3f"
        collector_id = "497f6eca-6276-4993-bfeb-53cbbbba6f08"

        doc = CollectingEventDocument(
            data=CollectingEventData(
                type="collecting-event",
                attributes=CollectingEventAttributes(group="aafc"),
                relationships={
                    "protocol": RelationshipData(
                        data=RelationshipLinkage(type="protocol", id=protocol_id)
                    ),
                    "collectors": RelationshipData(
                        data=[RelationshipLinkage(type="person", id=collector_id)]
                    ),
                },
            )
        )
        payload = doc.serialize()
        print("\n=== SERIALIZED (with relationships) ===")
        print(json.dumps(payload, indent=2))

        rels = payload["data"]["relationships"]
        self.assertEqual(rels["protocol"]["data"]["id"], protocol_id)
        self.assertEqual(rels["protocol"]["data"]["type"], "protocol")
        self.assertEqual(rels["collectors"]["data"][0]["id"], collector_id)
        self.assertEqual(rels["collectors"]["data"][0]["type"], "person")

    def test_relationship_round_trip_does_not_nullify(self):
        """Relationships that had only links (no data) in the response must not
        appear in a subsequent serialized payload."""
        doc = CollectingEventDocument.deserialize(VALID_COLLECTING_EVENT_RESPONSE)
        payload = doc.serialize()
        print("\n=== SERIALIZED (round-trip — links-only rels stripped) ===")
        print(json.dumps(payload, indent=2))

        rels = payload["data"].get("relationships", {})
        # collectionMethod had data → present
        self.assertIn("collectionMethod", rels)
        self.assertIsNotNone(rels["collectionMethod"]["data"])
        # protocol had only links → absent from request payload
        self.assertNotIn("protocol", rels)


if __name__ == "__main__":
    unittest.main()
