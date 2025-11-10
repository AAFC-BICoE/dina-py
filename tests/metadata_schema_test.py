import unittest
import pprint

from marshmallow.exceptions import ValidationError

import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now you can import modules from the dinaapi package
from dinapy.entities.Metadata import MetadataAttributesDTOBuilder, MetadataDTOBuilder
from dinapy.entities.Relationships import RelationshipDTO
from dinapy.schemas.metadata_schema import MetadataSchema

KEYCLOAK_CONFIG_PATH = "tests/keycloak-config.yml"

VALID_METADATA_DATA = {
    "data":{
            "id": "3fa5734e-a953-41cb-a1ae-eb5f7498b8b9",
            "type": "metadata",
            "attributes": {
                "createdBy": "bilkhus",
                "createdOn": "2023-04-17T15:22:44.89746Z",
                "bucket": "aafc",
                "fileIdentifier": "e42e881e-71f2-43ce-91e8-a703a7dbfa04",
                "originalFilename": "Agarose-gel-electrophoresis.png",
                "filename": None,
                "fileExtension": ".png",
                "resourceExternalURL": None,
                "dcFormat": "image/png",
                "dcType": "IMAGE",
                "acCaption": "Agarose-gel-electrophoresis.png",
                "acDigitizationDate": None,
                "xmpMetadataDate": "2023-04-17T15:22:44.9176Z",
                "xmpRightsWebStatement": "https://open.canada.ca/en/open-government-licence-canada",
                "dcRights": "© His Majesty The King in Right of Canada, as represented by the Minister of Agriculture and Agri-Food | © Sa Majesté le Roi du chef du Canada, représentée par le ministre de l’Agriculture et de l’Agroalimentaire",
                "xmpRightsOwner": "Government of Canada",
                "xmpRightsUsageTerms": "Government of Canada Usage Term",
                "orientation": None,
                "acHashFunction": "SHA-1",
                "acHashValue": "aed6fd5b8402dc0ad66ca52c1df042a31e70e3bf",
                "publiclyReleasable": True,
                "group": "aafc",
                "managedAttributes": {}
            }
        }
}


class MetadataSchemaTest(unittest.TestCase):
    def test_deserialization(self):
        # Create a schema instance and attempt to deserialize JSON object using it
        schema = MetadataSchema()
        result = schema.load(VALID_METADATA_DATA)

    def test_serialization(self):
        # Create a schema instance and validate the data
        acMetadataCreatorId = "3c47203f-9833-4945-b673-ece4e3bd4f9a"
        dcCreatorId = "afcf0bcc-c6c8-40c5-b97b-1855ce5d1729"
        relationships = (
            RelationshipDTO.Builder()
            .add_relationship("acMetadataCreator", "person", acMetadataCreatorId)
            .add_relationship("dcCreator", "person", dcCreatorId)
            .build()
        )

        attributes = (
            MetadataAttributesDTOBuilder()
            .set_fileName("test_filename")
            .set_bucket("aafc")
            .set_fileIdentifier("0190e0df-0809-71a3-b8e5-036cfbfec914")
            .set_fileExtension(".png")
            .set_resourceExternalURL(None)
            .set_dcFormat("image/png")
            .set_dcType("IMAGE")
            .set_acCaption("sample_640×426.png")
            .set_xmpRightsWebStatement(
                "https://open.canada.ca/en/open-government-licence-canada"
            )
            .set_dcRights(
                "© His Majesty The King in Right of Canada, as represented by the Minister of Agriculture and Agri-Food | © Sa Majesté le Roi du chef du Canada, représentée par le ministre de l’Agriculture et de l’Agroalimentaire"
            )
            .set_xmpRightsOwner("Government of Canada")
            .set_xmpRightsUsageTerms("Government of Canada Usage Term")
            .set_orientation(1)
            .set_originalFilename("sample_640×426.png")
            .set_acHashFunction("SHA-1")
            .set_acHashValue("e29c5ca02f1b2faec0302700fc084584cf2869ae")
            .set_publiclyReleasable(True)
            .set_acSubtype("OBJECT SUBTYPE 1")
            .set_group("aafc")
            .build()
        )

        dto = (
            MetadataDTOBuilder()
            .set_attributes(attributes)
            .set_relationships(relationships)
            .build()
        )

        schema = MetadataSchema()

        serialized_metadata = schema.dump(dto)
        expected = {
            "data": {
                # "id": "0190e0df-abef-7cf5-baa2-9453ec6f012d",
                "type": "metadata",
                "attributes": {
                    "bucket": "aafc",
                    "fileIdentifier": "0190e0df-0809-71a3-b8e5-036cfbfec914",
                    "fileExtension": ".png",
                    "resourceExternalURL": None,
                    "dcFormat": "image/png",
                    "dcType": "IMAGE",
                    "acCaption": "sample_640×426.png",
                    "xmpRightsWebStatement": "https://open.canada.ca/en/open-government-licence-canada",
                    "dcRights": "© His Majesty The King in Right of Canada, as represented by the Minister of Agriculture and Agri-Food | © Sa Majesté le Roi du chef du Canada, représentée par le ministre de l’Agriculture et de l’Agroalimentaire",
                    "xmpRightsOwner": "Government of Canada",
                    "xmpRightsUsageTerms": "Government of Canada Usage Term",
                    "orientation": 1,
                    "originalFilename": "sample_640×426.png",
                    "acHashFunction": "SHA-1",
                    "acHashValue": "e29c5ca02f1b2faec0302700fc084584cf2869ae",
                    "publiclyReleasable": True,
                    "acSubtype": "OBJECT SUBTYPE 1",
                    "group": "aafc",
                },
                "relationships": {
                    "acMetadataCreator": {
                        "data": {
                            "id": "3c47203f-9833-4945-b673-ece4e3bd4f9a",
                            "type": "person",
                        }
                    },
                    "dcCreator": {
                        "data": {
                            "id": "afcf0bcc-c6c8-40c5-b97b-1855ce5d1729",
                            "type": "person",
                        }
                    },
                },
            },
        }
        self.assertIsInstance(serialized_metadata, dict)
        self.assertDictEqual(serialized_metadata, expected)

    def test_invalid_materialsample_schema(self):
        # Example invalid data with missing required fields
        invalid_data = {
            "data": {
                "id": "0190e0df-abef-7cf5-baa2-9453ec6f012d",
                "type": "metadata",
                "attributes": {
                    "createdBy": "dina-admin",
                    "createdOn": "2024-07-23T18:34:33.328038Z",
                    "bucket": "aafc",
                    "fileIdentifier": "0190e0df-0809-71a3-b8e5-036cfbfec914",
                    "fileExtension": ".png",
                    "resourceExternalURL": None,
                    "dcFormat": "image/png",
                    "dcType": "IMAGE",
                    "acCaption": "sample_640×426.png",
                    "acDigitizationDate": "2024-07-23T07:00:00Z",
                    "xmpMetadataDate": "2024-07-23T18:34:33.357486Z",
                    "xmpRightsWebStatement": "https://open.canada.ca/en/open-government-licence-canada",
                    "dcRights": "© His Majesty The King in Right of Canada, as represented by the Minister of Agriculture and Agri-Food | © Sa Majesté le Roi du chef du Canada, représentée par le ministre de l’Agriculture et de l’Agroalimentaire",
                    "xmpRightsOwner": "Government of Canada",
                    "xmpRightsUsageTerms": "Government of Canada Usage Term",
                    "orientation": 1,
                    "originalFilename": "sample_640×426.png",
                    "acHashFunction": "SHA-1",
                    "acHashValue": "e29c5ca02f1b2faec0302700fc084584cf2869ae",
                    "publiclyReleasable": True,
                    "acSubtype": "OBJECT SUBTYPE 1",
                    # "group": "aafc",
                    "managedAttributes": {"legacy_barcode": "123"},
                },
                "relationships": {
                    "acMetadataCreator": {
                        "data": {
                            "id": "3c47203f-9833-4945-b673-ece4e3bd4f9a",
                            "type": "person",
                        }
                    },
                    "dcCreator": {
                        "data": {
                            "id": "afcf0bcc-c6c8-40c5-b97b-1855ce5d1729",
                            "type": "person",
                        }
                    },
                },
            },
            "meta": {
                "totalResourceCount": 1,
                "external": [{"href": "Agent/api/v1/person", "type": "person"}],
                "moduleVersion": "1.17",
            },
        }
        # Create a schema instance and attempt to validate the invalid data
        schema = MetadataSchema()
        with self.assertRaises(ValidationError):
            schema.load(invalid_data)


if __name__ == "__main__":
    unittest.main()
