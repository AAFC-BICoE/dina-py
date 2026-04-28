"""Tests for the Pydantic-based Person model."""
import unittest
import json
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.schemas.person_pydantic import (
    PersonAttributes,
    PersonData,
    PersonDocument,
)
from dinapy.schemas.pydantic_base import RelationshipData, RelationshipLinkage

VALID_PERSON_RESPONSE = {
    "data": {
        "id": "bfa3c68b-8e13-4295-8e25-47dbe041cb64",
        "type": "person",
        "attributes": {
            "displayName": "testBob",
            "email": "bob.builder@agr.gc.ca",
            "createdBy": "cnc-su",
            "createdOn": "2023-02-20T16:18:10.688627Z",
            "givenNames": "Bob",
            "familyNames": "Builder",
            "aliases": ["Yes we can"],
            "webpage": None,
            "remarks": None,
        },
        "relationships": {
            "identifiers": {
                "links": {
                    "self": "/api/v1/person/bfa3c68b/relationships/identifiers",
                    "related": "/api/v1/person/bfa3c68b/identifiers",
                }
            },
            "organizations": {
                "links": {
                    "self": "/api/v1/person/bfa3c68b/relationships/organizations",
                    "related": "/api/v1/person/bfa3c68b/organizations",
                }
            },
        },
    },
}


class PersonPydanticTest(unittest.TestCase):

    def test_deserialize_api_response(self):
        doc = PersonDocument.deserialize(VALID_PERSON_RESPONSE)
        print("\n=== PERSON DESERIALIZED ===")
        print(json.dumps(doc.model_dump(mode="json"), indent=2))

        self.assertEqual(doc.data.id, "bfa3c68b-8e13-4295-8e25-47dbe041cb64")
        self.assertEqual(doc.data.attributes.displayName, "testBob")
        self.assertEqual(doc.data.attributes.familyNames, "Builder")
        self.assertEqual(doc.data.attributes.aliases, ["Yes we can"])
        self.assertIsNone(doc.data.attributes.webpage)
        # Both relationships are links-only → no relationships on model
        self.assertIsNone(doc.data.relationships)

    def test_serialize_only_set_fields(self):
        doc = PersonDocument(
            data=PersonData(
                type="person",
                attributes=PersonAttributes(
                    displayName="testBob",
                    familyNames="Builder",
                    givenNames="Bob",
                    email="bob.builder@agr.gc.ca",
                    aliases=["Yes we can"],
                ),
            )
        )
        payload = doc.serialize()
        print("\n=== PERSON SERIALIZED ===")
        print(json.dumps(payload, indent=2))

        attrs = payload["data"]["attributes"]
        self.assertEqual(attrs["displayName"], "testBob")
        self.assertEqual(attrs["familyNames"], "Builder")
        self.assertEqual(attrs["aliases"], ["Yes we can"])
        self.assertNotIn("webpage", attrs)
        self.assertNotIn("createdBy", attrs)
        self.assertNotIn("relationships", payload["data"])

    def test_serialize_with_organization_relationship(self):
        org_id = "aaaaaaaa-0000-0000-0000-000000000001"
        doc = PersonDocument(
            data=PersonData(
                type="person",
                attributes=PersonAttributes(
                    displayName="Alice",
                    familyNames="Smith",
                ),
                relationships={
                    "organizations": RelationshipData(
                        data=[RelationshipLinkage(type="organization", id=org_id)]
                    )
                },
            )
        )
        payload = doc.serialize()
        rels = payload["data"]["relationships"]
        self.assertEqual(rels["organizations"]["data"][0]["id"], org_id)

    def test_links_only_relationships_not_in_request(self):
        doc = PersonDocument.deserialize(VALID_PERSON_RESPONSE)
        payload = doc.serialize()
        self.assertNotIn("relationships", payload["data"])


if __name__ == "__main__":
    unittest.main()
