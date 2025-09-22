# This file contains tests relating to PersonAPI.
# Currently only contains tests for the PersonSchema (serialization and deserialization tests).
# API mock call tests should be added.


import unittest
from marshmallow import ValidationError
import sys
import os
from datetime import datetime

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.schemas.personschema import PersonSchema
from dinapy.entities.Person import PersonDTOBuilder,PersonAttributesDTOBuilder, PersonDTO

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
    def setUp(self):
        self.schema = PersonSchema()

    def test_valid_person_schema_load(self):
        """Test loading valid person data"""
        try:
            result = self.schema.load(VALID_PERSON_DATA)
            # Should return a PersonDTO object
            self.assertIsInstance(result, PersonDTO)
            # Verify attributes were loaded correctly
            self.assertEqual(result.get_id(), "bfa3c68b-8e13-4295-8e25-47dbe041cb64")
            self.assertEqual(result.get_attributes().get("displayName"), "testBob")
            self.assertEqual(result.get_attributes().get("email"), "bob.builder@agr.gc.ca")
        except ValidationError as e:
            self.fail(f"Validation failed with error: {e.messages}")

    def test_valid_person_schema_dump(self):
        """Test dumping person data to JSON"""
        # Create a PersonDTO
        person_attributes = PersonAttributesDTOBuilder().displayName("testBob")\
            .email("bob.builder@agr.gc.ca")\
            .givenNames("Bob")\
            .familyNames("Builder")\
            .aliases(["Yes we can"]).build()
        person = PersonDTOBuilder().attributes(person_attributes).build()

        #Dump to JSON
        result = self.schema.dump(person)

        # Verify essential fields
        self.assertEqual(result['data']['attributes']['displayName'], "testBob")

    def test_invalid_person_schema(self):
        """Test loading invalid person data"""
        invalid_data = {
            "data": {
                "type": "person",
                "attributes": {
                    # Missing required displayName
                    "email": "bob.builder@agr.gc.ca",
                    "createdBy": "cnc-su",
                    "createdOn": "2023-02-20T16:18:10.688627Z",
                }
            }
        }

        with self.assertRaises(ValidationError) as context:
            self.schema.load(invalid_data)

        errors = context.exception.messages

        # Add debug print to see actual error structure
        print(f"Error structure: {errors}")

        # Check if any error has the expected detail message
        missing_field_errors = [
            error for error in errors['errors'] 
            if error['detail'] == 'Missing data for required field.'
        ]
        
        self.assertTrue(
            len(missing_field_errors) > 0,
            f"Expected 'Missing data for required field' error in: {errors}"
        )

        # Optional: Verify specific field that's missing
        self.assertTrue(
            any(error['source']['pointer'] == '/data/attributes/displayName' 
                for error in errors['errors']),
            "Expected error about missing displayName field"
        )

if __name__ == "__main__":
    unittest.main()
