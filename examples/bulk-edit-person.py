# Import necessary modules
import json
import sys
import os
from marshmallow.exceptions import ValidationError

# Set up the project root path to allow importing local modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import DINA-related modules and utilities
from dinapy.entities.CollectingEvent import *
from dinapy.apis.agentapi.personapi import PersonAPI
from dinapy.schemas.personschema import PersonSchema
from dinapy.utils import *

# Set environment variables for authentication (replace with actual credentials or use a secure method)
os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

def main():
    # Initialize the Person API client (uses certificate-based authentication)
    person_api = PersonAPI()

    # Retrieve records from the API where the 'group' field matches 'aafc'
    records = person_api.find_many()
    print(records)
    # Deserialize the first 2 records into Person objects using the schema
    persons = []
    for record in records[:2]:
        try:
            # Deserialize the record using Marshmallow schema
            print(record)
            person = PersonSchema().load({"data": record})
            persons.append(person)
        except ValidationError as e:
            # Print validation errors and skip invalid records
            print(f"Validation error: {e}")
            continue

    print(f"Successfully parsed {len(persons)} persons")

    # Modify a specific field in each person
    for record in persons:
        # Set the 'lastName' attribute to a new value
        record.attributes["familyNames"] = "test-family-name"

    # Prepare the payload for bulk update, including only the modified field
    bulk_payload = prepare_bulk_payload(
        entities=persons,
        include_fields=["familyNames"]
    )

    # Print the bulk payload for inspection/debugging
    print(json.dumps(bulk_payload))

    # Send the bulk update request to the API
    response = person_api.bulk_update(bulk_payload)

    # print the response from the bulk update operation
    print(response)

# Entry point for script execution
if __name__ == "__main__":
    main()