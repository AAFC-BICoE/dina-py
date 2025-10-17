import json
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from datetime import datetime

# Add the root directory to Python path to allow importing local modules

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import DINA utilities and schema definitions

from dinapy.utils import prepare_bulk_payload
from dinapy.schemas.personschema import PersonSchema

# Sample valid person data for testing

VALID_PERSON_DATA_ONE = {
  "data":
    {
      "id": "39e2e74c-e3ae-4d80-959b-dcb4ec35897b",
      "type": "person",
      "attributes": {
        "displayName": "Test One Person One",
        "email": "test1@example.com",
        "createdBy": "test-user",
        "createdOn": "2024-01-01T00:00:00Z",
        "givenNames": "Test One",
        "familyNames": "Person One",
        "aliases": []
      },
      "relationships": {
        "identifiers": {
          "links": {
            "self": "/api/v1/person/39e2e74c-e3ae-4d80-959b-dcb4ec35897b/relationships/identifiers",
            "related": "/api/v1/person/39e2e74c-e3ae-4d80-959b-dcb4ec35897b/identifiers"
          }
        },
        "organizations": {
          "links": {
            "self": "/api/v1/person/39e2e74c-e3ae-4d80-959b-dcb4ec35897b/relationships/organizations",
            "related": "/api/v1/person/39e2e74c-e3ae-4d80-959b-dcb4ec35897b/organizations"
          }
        }
      },
      "links": {
        "self": "/api/v1/person/39e2e74c-e3ae-4d80-959b-dcb4ec35897b"
      }
    }
}
VALID_PERSON_DATA_TWO = {
    "data":
    {
      "id": "bba50a6e-2348-4f17-b570-7171b7305a24", 
      "type": "person",
      "attributes": {
        "displayName": "Test Two Person Two",
        "email": "test2@example.com",
        "createdBy": "test-user",
        "createdOn": "2024-01-01T00:00:00Z",
        "givenNames": "Test Two",
        "familyNames": "Person Two",
        "aliases": []
      },
      "relationships": {
        "identifiers": {
          "links": {
            "self": "/api/v1/person/bba50a6e-2348-4f17-b570-7171b7305a24/relationships/identifiers",
            "related": "/api/v1/person/bba50a6e-2348-4f17-b570-7171b7305a24/identifiers"
          }
        },
        "organizations": {
          "links": {
            "self": "/api/v1/person/bba50a6e-2348-4f17-b570-7171b7305a24/relationships/organizations",
            "related": "/api/v1/person/bba50a6e-2348-4f17-b570-7171b7305a24/organizations"
          }
        }
      },
      "links": {
        "self": "/api/v1/person/bba50a6e-2348-4f17-b570-7171b7305a24"
      }
    }
}

# Define a test case for bulk updating person entities

class TestBulkUpdate(unittest.TestCase):
    
    @patch('dinapy.dinaapi.DinaAPI')  # Mock the DinaAPI class to avoid real API calls
    def test_bulk_update_persons(self, MockDinaAPI):
        
        # Create a mock response object with a successful status code

        mock_response = MagicMock()
        mock_response.status_code = 200

        # Configure the mock API to return the mock response on bulk_update

        MockDinaAPI.return_value.bulk_update.return_value = mock_response
        person_api = MockDinaAPI.return_value

        # Initialize the schema for deserialization

        person_schema = PersonSchema()

        # Deserialize the test data into Person objects

        person1 = person_schema.load(VALID_PERSON_DATA_ONE)
        person2 = person_schema.load(VALID_PERSON_DATA_TWO)

        # Verify that deserialization worked correctly

        self.assertEqual(person1.id, "39e2e74c-e3ae-4d80-959b-dcb4ec35897b")
        self.assertEqual(person1.attributes['familyNames'], "Person One")

        # Modify the 'familyNames' attribute for both persons

        person1.attributes['familyNames'] = "prazeres"
        person2.attributes['familyNames'] = "prazeres"
        
        # Prepare the bulk update payload with only the modified field

        bulk_payload = prepare_bulk_payload(
            entities=[person1, person2],
            include_fields=["familyNames"]
        )
        
        # Define the expected payload structure

        expected_payload = {
            "data": [
                {
                    "id": "39e2e74c-e3ae-4d80-959b-dcb4ec35897b",
                    "type": "person",
                    "attributes": {
                        "familyNames": "prazeres"
                    }
                },
                {
                    "id": "bba50a6e-2348-4f17-b570-7171b7305a24",
                    "type": "person",
                    "attributes": {
                        "familyNames": "prazeres"
                    }
                }
            ]
        }
        
        # Assert that the generated payload matches the expected structure

        self.assertEqual(json.dumps(bulk_payload), json.dumps(expected_payload))
        
        # Perform the bulk update using the mocked API

        response = person_api.bulk_update(bulk_payload)
        
        # Verify that the bulk_update method was called with the correct payload

        person_api.bulk_update.assert_called_once_with(bulk_payload)
        
        # Assert that the response status code is 200 (success)

        self.assertEqual(response.status_code, 200)
        
# Run the test case if this script is executed directly


if __name__ == '__main__':
    unittest.main()