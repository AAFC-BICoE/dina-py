# This file contains tests relating to PersonAPI.
# Currently only contains tests for the PersonSchema (serialization and deserialization tests).
# API mock call tests should be added.

import unittest
import pprint

from marshmallow.exceptions import ValidationError

import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now you can import modules from the dinaapi package
from dinapy.schemas.metadata_schema import MetadataSchema

KEYCLOAK_CONFIG_PATH = "tests/keycloak-config.yml"

VALID_METADATA_DATA = {
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
            "group": "aafc",
            "managedAttributes": {"legacy_barcode": "123"},
        },
        "relationships": {
            "acMetadataCreator": {
                "data": {"id": "3c47203f-9833-4945-b673-ece4e3bd4f9a", "type": "person"}
            },
            "dcCreator": {
                "data": {"id": "afcf0bcc-c6c8-40c5-b97b-1855ce5d1729", "type": "person"}
            },
        },
    },
    "meta": {
        "totalResourceCount": 1,
        "external": [{"href": "Agent/api/v1/person", "type": "person"}],
        "moduleVersion": "1.17",
    },
}


class MetadataSchemaTest(unittest.TestCase):
    def test_valid_metadata_schema(self):
        # Create a schema instance and validate the data
        schema = MetadataSchema()
        try:
            result = schema.load(VALID_METADATA_DATA)
            pp = pprint.PrettyPrinter(indent=0)
            pp.pprint(result)
            self.assertIsInstance(result, dict)
        except ValidationError as e:
            self.fail(f"Validation failed with error: {e.messages}")

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
