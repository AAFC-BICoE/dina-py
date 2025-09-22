import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from datetime import datetime

# Add the root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.utils import prepare_bulk_payload
from dinapy.schemas.personschema import PersonSchema
from dinapy.entities.Person import Person,PersonDTOBuilder, PersonAttributesDTOBuilder

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

class TestBulkUpdate(unittest.TestCase):
    
    def setUp(self):
        self.config_path = "tests/keycloak-config.yml"
        
    @patch('dinapy.dinaapi.DinaAPI')
    def test_bulk_update_persons(self, MockDinaAPI):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        MockDinaAPI.return_value.bulk_update.return_value = mock_response
        person_api = MockDinaAPI.return_value
        person_schema = PersonSchema()

        # Load both persons from the test data

        person1 = person_schema.load(VALID_PERSON_DATA_ONE)
        person2 = person_schema.load(VALID_PERSON_DATA_TWO)

        # Verify deserialization worked
        self.assertEqual(person1.id, "39e2e74c-e3ae-4d80-959b-dcb4ec35897b")
        self.assertEqual(person1.attributes['familyNames'], "Person One")

        # Update family names
        person1.attributes['familyNames'] = "prazeres"
        person2.attributes['familyNames'] = "prazeres"
        
        # Prepare bulk payload
        bulk_payload = prepare_bulk_payload(
            entities=[person1, person2],
            schema=PersonSchema,
            include_fields=["familyNames"]
        )
        
        # Expected payload structure
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
        
        # Assert payload structure is correct
        self.assertEqual(bulk_payload, expected_payload)
        
        # Perform bulk update
        response = person_api.bulk_update(bulk_payload)
        
        # Verify the request was made with correct payload
        person_api.bulk_update.assert_called_once_with(bulk_payload)
        
        # Assert response
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()