"""Tests for the Pydantic-based Controlled Vocabulary Item model."""
import unittest
import json
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.schemas.controlled_vocabulary_pydantic import (
    ControlledVocabularyItemAttributes,
    ControlledVocabularyData,
    ControlledVocabularyDocument,
)

VALID_CONTROLLED_VOCABULARY_RESPONSE = {
    "data": {
        "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
        "type": "controlled-vocabulary-item",
        "attributes": {
            "name": "bodyColor",
            "key": "body_color",
            "group": "aafc",
            "term": "http://example.com/term/bodyColor",
            "vocabularyElementType": "STRING",
            "acceptedValues": ["red", "blue", 1],
            "unit": "cm",
            "uriTemplate": "http://example.com/term/$1",
            "dinaComponent": "MATERIAL_SAMPLE",
            "multilingualTitle": {
                "titles": [{"lang": "en", "title": "Body Color"}]
            },
            "multilingualDescription": {
                "descriptions": [
                    {"lang": "en", "desc": "The color of the body"},
                    {"lang": "fr", "desc": "La couleur du corps"},
                ]
            },
            "createdBy": "dina-admin",
            "createdOn": "1985-04-12T23:20:50.52Z",
            "lastUpdatedOn": "1985-04-12T23:20:50.52Z",
        },
    },
    "meta": {"moduleVersion": "0.1", "totalResourceCount": 1},
}

VALID_LIST_RESPONSE = {
    "data": [
        {
            "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
            "type": "controlled-vocabulary-item",
            "attributes": {
                "name": "bodyColor",
                "key": "body_color",
                "group": "aafc",
                "term": "http://example.com/term/bodyColor",
                "vocabularyElementType": "STRING",
                "acceptedValues": ["red", "blue", 1],
                "unit": "cm",
                "uriTemplate": "http://example.com/term/$1",
                "dinaComponent": "MATERIAL_SAMPLE",
                "multilingualTitle": {
                    "titles": [{"lang": "en", "title": "Body Color"}]
                },
                "multilingualDescription": {
                    "descriptions": [
                        {"lang": "en", "desc": "The color of the body"}
                    ]
                },
                "createdBy": "dina-admin",
                "createdOn": "1985-04-12T23:20:50.52Z",
                "lastUpdatedOn": "1985-04-12T23:20:50.52Z",
            },
        },
        {
            "id": "e391f2ff-7d65-5c12-a1f7-e812859f1962",
            "type": "controlled-vocabulary-item",
            "attributes": {
                "name": "eyeColor",
                "key": "eye_color",
                "group": "aafc",
                "term": "http://example.com/term/eyeColor",
                "vocabularyElementType": "STRING",
                "acceptedValues": ["brown", "blue", "green"],
                "unit": None,
                "uriTemplate": None,
                "dinaComponent": "MATERIAL_SAMPLE",
                "multilingualTitle": None,
                "multilingualDescription": None,
                "createdBy": "dina-admin",
                "createdOn": "1985-04-12T23:20:50.52Z",
                "lastUpdatedOn": None,
            },
        },
    ],
    "meta": {"moduleVersion": "0.1", "totalResourceCount": 2},
}


class ControlledVocabularyPydanticTest(unittest.TestCase):

    def test_deserialize_single_response(self):
        """Deserialize a GET-by-ID response."""
        doc = ControlledVocabularyDocument.deserialize(VALID_CONTROLLED_VOCABULARY_RESPONSE)

        self.assertEqual(doc.data.id, "d290f1ee-6c54-4b01-90e6-d701748f0851")


    def test_deserialize_list_response(self):
        """Deserialize a GET-all response by iterating data items."""
        items = [
            ControlledVocabularyDocument.deserialize({"data": item})
            for item in VALID_LIST_RESPONSE["data"]
        ]

        self.assertEqual(items[0].data.attributes.name, "bodyColor")
        self.assertEqual(items[1].data.attributes.name, "eyeColor")

    def test_serialize_post_payload(self):
        """Build a POST request payload — only set fields appear."""
        doc = ControlledVocabularyDocument(
            data=ControlledVocabularyData(
                type="controlled-vocabulary-item",
                attributes=ControlledVocabularyItemAttributes(
                    name="bodyColor",
                    key="body_color",
                    group="aafc",
                    term="http://example.com/term/bodyColor",
                    vocabularyElementType="STRING",
                    acceptedValues=["red", "blue", 1],
                    unit="cm",
                    uriTemplate="http://example.com/term/$1",
                    dinaComponent="MATERIAL_SAMPLE",
                    multilingualTitle={
                        "titles": [{"lang": "en", "title": "Body Color"}]
                    },
                    multilingualDescription={
                        "descriptions": [
                            {"lang": "en", "desc": "The color of the body"}
                        ]
                    },
                ),
            )
        )

        payload = doc.serialize()
        print("\n=== POST PAYLOAD ===")
        print(json.dumps(payload, indent=2))

        self.assertEqual(payload["data"]["type"], "controlled-vocabulary-item")
        attrs = payload["data"]["attributes"]
        self.assertEqual(attrs["name"], "bodyColor")
        self.assertEqual(attrs["acceptedValues"], ["red", "blue", 1])
        self.assertIn("multilingualTitle", attrs)

        # createdBy/createdOn not set → excluded
        self.assertNotIn("createdBy", attrs)
        self.assertNotIn("createdOn", attrs)
        self.assertNotIn("lastUpdatedOn", attrs)
        self.assertNotIn("relationships", payload["data"])

    def test_roundtrip(self):
        doc = ControlledVocabularyDocument(
            data=ControlledVocabularyData(
                type="controlled-vocabulary-item",
                attributes=ControlledVocabularyItemAttributes(
                    name="roundtripTest",
                    key="roundtrip_test",
                    group="aafc",
                    vocabularyElementType="INTEGER",
                    acceptedValues=[1, 2, 3],
                    unit="mm",
                    dinaComponent="COLLECTING_EVENT",
                ),
            )
        )

        payload = doc.serialize()
        doc2 = ControlledVocabularyDocument.deserialize(payload)

        self.assertEqual(doc2.data.attributes.name, "roundtripTest")
        self.assertEqual(doc2.data.attributes.key, "roundtrip_test")
        self.assertEqual(doc2.data.attributes.vocabularyElementType, "INTEGER")
        self.assertEqual(doc2.data.attributes.acceptedValues, [1, 2, 3])
        self.assertEqual(doc2.data.attributes.unit, "mm")


if __name__ == "__main__":
    unittest.main()
