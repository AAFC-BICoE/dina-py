import unittest

import responses
from marshmallow.exceptions import ValidationError

import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now you can import modules from the dinaapi package
from dinaapi.personapi.personapi import PersonAPI, PersonSchema


class PersonAPITestCase(unittest.TestCase):
    @responses.activate
    def test_person_find(self):
        # Mock the API response
        mock_response_data = {
            "data": {
                "id": "bfa3c68b-8e13-4295-8e25-47dbe041cb64",
                "type": "person",
                "attributes": {
                    "displayName": "John Doe",
                    "email": "john@example.com",
                    "createdBy": "admin",
                    "createdOn": "2023-08-02T12:00:00Z",
                    "givenNames": "John",
                    "familyNames": "Doe",
                    "webpage": "https://example.com",
                    "remarks": "This is a mock person.",
                    "aliases": ["Johnny"],
                },
                "relationships": {
                    "organizations": {
                        "data": [{"type": "organization", "id": "12345"}]
                    },
                    "identifiers": {"data": [{"type": "identifier", "id": "67890"}]},
                },
            }
        }

        responses.add(
            responses.GET,
            "https://dina-dev2.biodiversity.agr.gc.ca/api/agent-api/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64",
            json=mock_response_data,
            status=200,
        )

        # Instantiate PersonAPI and make the API call
        person_api = PersonAPI()
        response = person_api.find("bfa3c68b-8e13-4295-8e25-47dbe041cb64")

        # Check the response status code and content
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertDictEqual(response_data, mock_response_data)

    @responses.activate
    def test_person_find_not_found(self):
        # Mock the API response for a not found error
        responses.add(
            responses.GET,
            "https://dina-dev2.biodiversity.agr.gc.ca/api/agent-api/person/non_existent_uuid",
            json={"error": "person not found"},
            status=404,
        )

        # Instantiate PersonAPI and make the API call
        person_api = PersonAPI()
        response = person_api.find("non_existent_uuid")

        # Check the response status code and content
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertEqual(response_data, {"error": "Person not found"})

    def test_valid_data(self):
        # Example valid data
        data = {
            "data": {
                "id": "bfa3c68b-8e13-4295-8e25-47dbe041cb64",
                "type": "person",
                "links": {
                    "self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64"
                },
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

        # Create a schema instance and validate the data
        schema = PersonSchema()
        try:
            result = schema.load(data)
            self.assertIsInstance(result, dict)
        except ValidationError as e:
            self.fail(f"Validation failed with error: {e.messages}")

    def test_invalid_data(self):
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
