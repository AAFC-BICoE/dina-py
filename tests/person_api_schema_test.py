# This file contains tests relating to PersonAPI.
# Currently only contains tests for the PersonSchema (serialization and deserialization tests).
# API mock call tests should be added.


import unittest

from marshmallow.exceptions import ValidationError

import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now you can import modules from the dinaapi package
from dinapy.schemas.personschema import PersonSchema

KEYCLOAK_CONFIG_PATH = "tests/keycloak-config.yml"

VALID_PERSON_DATA = {
    "data": {
        "id": "bfa3c68b-8e13-4295-8e25-47dbe041cb64",
        "type": "person",
        "links": {"self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64"},
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
                    "self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/relationships/identifiers",
                    "related": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/identifiers",
                }
            },
            "organizations": {
                "links": {
                    "self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/relationships/organizations",
                    "related": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/organizations",
                }
            },
        },
    },
    "meta": {"totalResourceCount": 1, "moduleVersion": "0.24"},
}


class PersonAPITestCase(unittest.TestCase):
    def test_valid_person_schema(self):
        # Create a schema instance and validate the data
        schema = PersonSchema()
        try:
            result = schema.load(VALID_PERSON_DATA)
            self.assertIsInstance(result, dict)
        except ValidationError as e:
            self.fail(f"Validation failed with error: {e.messages}")

    def test_invalid_person_schema(self):
        # Example invalid data with missing required fields
        invalid_data = {
            "data": {
                "id": "bfa3c68b-8e13-4295-8e25-47dbe041cb64",
                "type": "person",
                "links": {
                    "self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64"
                },
                "attributes": {
                    # "displayName": "testBob", no display name
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
                            "self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/relationships/identifiers",
                            "related": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/identifiers",
                        }
                    },
                    "organizations": {
                        "links": {
                            "self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/relationships/organizations",
                            "related": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/organizations",
                        }
                    },
                },
            },
            "meta": {"totalResourceCount": 1, "moduleVersion": "0.24"},
        }

        # Create a schema instance and attempt to validate the invalid data
        schema = PersonSchema()
        with self.assertRaises(ValidationError):
            schema.load(invalid_data)


if __name__ == "__main__":
    unittest.main()
