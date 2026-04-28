"""Tests for the Pydantic-based Metadata model."""
import unittest
import json
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.schemas.metadata_pydantic import (
    MetadataAttributes,
    MetadataData,
    MetadataDocument,
)
from dinapy.schemas.pydantic_base import RelationshipData, RelationshipLinkage

VALID_METADATA_RESPONSE = {
    "data": {
        "id": "d3e2f1a0-abcd-1234-5678-000000000001",
        "type": "metadata",
        "attributes": {
            "createdBy": "dina-admin",
            "createdOn": "2023-06-15T12:00:00.000000Z",
            "bucket": "mybucket",
            "filename": "sample_image.jpg",
            "fileIdentifier": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "fileExtension": ".jpg",
            "dcType": "IMAGE",
            "group": "aafc",
            "publiclyReleasable": True,
            "acTags": ["tag1", "tag2"],
        },
        "relationships": {
            "acMetadataCreator": {
                "data": {
                    "id": "bfa3c68b-8e13-4295-8e25-47dbe041cb64",
                    "type": "person",
                }
            },
            "derivatives": {
                "links": {
                    "self": "/api/v1/metadata/d3e2f1a0/relationships/derivatives"
                }
            },
            "dcCreator": {
                "links": {
                    "self": "/api/v1/metadata/d3e2f1a0/relationships/dcCreator"
                }
            },
        },
    }
}


class MetadataPydanticTest(unittest.TestCase):

    def test_deserialize_api_response(self):
        doc = MetadataDocument.deserialize(VALID_METADATA_RESPONSE)
        print("\n=== METADATA DESERIALIZED ===")
        print(json.dumps(doc.model_dump(mode="json"), indent=2))

        self.assertEqual(doc.data.id, "d3e2f1a0-abcd-1234-5678-000000000001")
        self.assertEqual(doc.data.attributes.bucket, "mybucket")
        self.assertEqual(doc.data.attributes.dcType, "IMAGE")
        self.assertEqual(doc.data.attributes.acTags, ["tag1", "tag2"])
        # acMetadataCreator has data → preserved
        self.assertIsNotNone(doc.data.relationships["acMetadataCreator"].data)
        # links-only → dropped
        self.assertNotIn("derivatives", doc.data.relationships)
        self.assertNotIn("dcCreator", doc.data.relationships)

    def test_serialize_only_set_fields(self):
        doc = MetadataDocument(
            data=MetadataData(
                type="metadata",
                attributes=MetadataAttributes(
                    bucket="mybucket",
                    group="aafc",
                    filename="photo.png",
                    dcType="IMAGE",
                ),
            )
        )
        payload = doc.serialize()
        print("\n=== METADATA SERIALIZED ===")
        print(json.dumps(payload, indent=2))

        self.assertEqual(payload["data"]["attributes"]["bucket"], "mybucket")
        self.assertEqual(payload["data"]["attributes"]["dcType"], "IMAGE")
        self.assertNotIn("acCaption", payload["data"]["attributes"])
        self.assertNotIn("relationships", payload["data"])

    def test_serialize_with_acMetadataCreator(self):
        person_id = "bfa3c68b-8e13-4295-8e25-47dbe041cb64"
        doc = MetadataDocument(
            data=MetadataData(
                type="metadata",
                attributes=MetadataAttributes(bucket="mybucket", group="aafc"),
                relationships={
                    "acMetadataCreator": RelationshipData(
                        data=RelationshipLinkage(type="person", id=person_id)
                    )
                },
            )
        )
        payload = doc.serialize()
        self.assertEqual(
            payload["data"]["relationships"]["acMetadataCreator"]["data"]["id"],
            person_id,
        )

    def test_links_only_relationships_not_in_request(self):
        doc = MetadataDocument.deserialize(VALID_METADATA_RESPONSE)
        payload = doc.serialize()
        rels = payload["data"].get("relationships", {})
        self.assertNotIn("derivatives", rels)
        self.assertNotIn("dcCreator", rels)


if __name__ == "__main__":
    unittest.main()
