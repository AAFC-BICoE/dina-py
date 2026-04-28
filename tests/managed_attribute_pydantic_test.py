"""Tests for the Pydantic-based ManagedAttribute model."""
import unittest
import json
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.schemas.managed_attribute_pydantic import (
    ManagedAttributeAttributes,
    ManagedAttributeData,
    ManagedAttributeDocument,
)

VALID_MANAGED_ATTRIBUTE_RESPONSE = {
    "data": {
        "id": "01900001-0000-0000-0000-000000000001",
        "type": "managed-attribute",
        "attributes": {
            "createdBy": "dina-admin",
            "createdOn": "2023-01-01T00:00:00.000000Z",
            "group": "aafc",
            "name": "site_codes",
            "key": "site_codes",
            "vocabularyElementType": "STRING",
            "unit": None,
            "managedAttributeComponent": "COLLECTING_EVENT",
            "acceptedValues": None,
            "multilingualDescription": {
                "descriptions": [{"lang": "en", "desc": "Site code identifier"}]
            },
        },
        "relationships": {},
    }
}


class ManagedAttributePydanticTest(unittest.TestCase):

    def test_deserialize_api_response(self):
        doc = ManagedAttributeDocument.deserialize(VALID_MANAGED_ATTRIBUTE_RESPONSE)
        print("\n=== MANAGED ATTRIBUTE DESERIALIZED ===")
        print(json.dumps(doc.model_dump(mode="json"), indent=2))

        self.assertEqual(doc.data.id, "01900001-0000-0000-0000-000000000001")
        self.assertEqual(doc.data.attributes.name, "site_codes")
        self.assertEqual(doc.data.attributes.key, "site_codes")
        self.assertEqual(doc.data.attributes.vocabularyElementType, "STRING")
        self.assertIsNone(doc.data.attributes.unit)

    def test_serialize_only_set_fields(self):
        doc = ManagedAttributeDocument(
            data=ManagedAttributeData(
                type="managed-attribute",
                attributes=ManagedAttributeAttributes(
                    group="aafc",
                    name="new_attribute",
                    key="new_attribute",
                    vocabularyElementType="INTEGER",
                    managedAttributeComponent="MATERIAL_SAMPLE",
                ),
            )
        )
        payload = doc.serialize()
        print("\n=== MANAGED ATTRIBUTE SERIALIZED ===")
        print(json.dumps(payload, indent=2))

        self.assertEqual(payload["data"]["type"], "managed-attribute")
        self.assertEqual(payload["data"]["attributes"]["name"], "new_attribute")
        self.assertEqual(payload["data"]["attributes"]["vocabularyElementType"], "INTEGER")
        self.assertNotIn("unit", payload["data"]["attributes"])
        self.assertNotIn("acceptedValues", payload["data"]["attributes"])
        self.assertNotIn("relationships", payload["data"])

    def test_none_unit_excluded_from_request(self):
        """Explicitly set unit=None should not appear because exclude_none=True."""
        doc = ManagedAttributeDocument(
            data=ManagedAttributeData(
                type="managed-attribute",
                attributes=ManagedAttributeAttributes(group="aafc", unit=None),
            )
        )
        payload = doc.serialize()
        self.assertNotIn("unit", payload["data"]["attributes"])


if __name__ == "__main__":
    unittest.main()
