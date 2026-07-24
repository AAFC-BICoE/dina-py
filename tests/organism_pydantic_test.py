"""Tests for the Pydantic-based Organism model."""
import unittest
import json
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.schemas.organism_pydantic import (
    OrganismDocument
)


VALID_ORGANISM_RESPONSE = {
    "data": {
        "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
        "type": "organism",
        "attributes": {
            "createdBy": "dina-admin",
            "createdOn": "1985-04-12T23:20:50.52Z",
            "group": "aafc",
            "isTarget": True,
            "managedAttributes": {"prop1": "value1", "prop2": "value2"},
            "lifeStage": "adult",
            "sex": "female",
            "remarks": "Some remarks",
            "dwcVernacularName": "House mouse",
            "determination": [
                {
                    "verbatimScientificName": "Mus musculus",
                    "verbatimDeterminer": "Linnaeus",
                    "verbatimDate": "1758",
                    "scientificName": "Mus musculus",
                    "transcriberRemarks": "Verified",
                    "verbatimRemarks": "Original label",
                    "determinationRemarks": "Confirmed",
                    "typeStatus": "HOLOTYPE",
                    "typeStatusEvidence": "Specimen matches description",
                    "determiner": ["497f6eca-6276-4993-bfeb-53cbbbba6f08"],
                    "determinedOn": "2019-08-24",
                    "qualifier": "cf.",
                    "scientificNameSource": "GBIF Backbone",
                    "scientificNameDetails": {
                        "classificationPath": "Animalia;Chordata;Mammalia;Rodentia;Muridae;Mus;Mus musculus",
                        "classificationRanks": "Kingdom;Phylum;Class;Order;Family;Genus;Species",
                        "sourceUrl": "https://www.gbif.org/species/2433740",
                        "labelHtml": "<i>Mus musculus</i> Linnaeus, 1758",
                        "recordedOn": "2019-08-24",
                        "currentName": "Mus musculus",
                        "isSynonym": False,
                    },
                    "isPrimary": True,
                    "isFiledAs": True,
                    "managedAttributes": {"detAttr1": "detVal1"},
                }
            ],
        },
    }
}


class OrganismPydanticTest(unittest.TestCase):

    def test_full_roundtrip_with_field_modification(self):
        """Deserialize, modify a field, serialize back, and verify."""
        doc = OrganismDocument.deserialize(VALID_ORGANISM_RESPONSE)

        # Modify a top-level field
        doc.data.attributes.isTarget = False
        doc.data.attributes.lifeStage = "larva"

        # Modify a nested determination field
        doc.data.attributes.determination[0].isPrimary = False
        doc.data.attributes.determination[0].qualifier = "aff."

        # Modify a deeply nested field
        doc.data.attributes.determination[0].scientificNameDetails.isSynonym = True

        payload = doc.serialize()
        print("\n=== ORGANISM ROUNDTRIP (MODIFIED) ===")
        print(json.dumps(payload, indent=2))

        attrs = payload["data"]["attributes"]
        self.assertFalse(attrs["isTarget"])
        self.assertEqual(attrs["lifeStage"], "larva")
        self.assertFalse(attrs["determination"][0]["isPrimary"])
        self.assertEqual(attrs["determination"][0]["qualifier"], "aff.")
        self.assertTrue(
            attrs["determination"][0]["scientificNameDetails"]["isSynonym"]
        )


if __name__ == "__main__":
    unittest.main()
