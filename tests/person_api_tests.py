import unittest
import responses

from dinaapi.personapi.personapi import PersonAPI

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
                    "identifiers": {
                        "data": [{"type": "identifier", "id": "67890"}]
                    },
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
            json={"error": "Person not found"},
            status=404,
        )

        # Instantiate PersonAPI and make the API call
        person_api = PersonAPI()
        response = person_api.find("non_existent_uuid")

        # Check the response status code and content
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertEqual(response_data, {"error": "Person not found"})
