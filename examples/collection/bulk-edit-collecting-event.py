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
from dinapy.apis.collectionapi.collectingeventapi import CollectingEventAPI
from dinapy.schemas.collectingeventschema import CollectingEventSchema
from dinapy.utils import *

# Set environment variables for authentication (replace with actual credentials or use a secure method)
os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

def main():
    # Initialize the CollectingEvent API client (uses certificate-based authentication)
    collecting_event_api = CollectingEventAPI()

    # Retrieve records from the API where the 'group' field matches 'aafc'
    records = get_dina_records_by_field(collecting_event_api, "group", "aafc")
    print(records)
    # Deserialize the first 10 records into CollectingEvent objects using the schema
    collecting_events = []
    for record in records[:10]:
        try:
            # Deserialize the record using Marshmallow schema
            collecting_event = CollectingEventSchema().load({"data": record})
            collecting_events.append(collecting_event)
        except ValidationError as e:
            # Print validation errors and skip invalid records
            print(f"Validation error: {e}")
            continue

    print(f"Successfully parsed {len(collecting_events)} collecting events")

    # Re-initialize API and schema (optional, could reuse previous instances)
    collecting_event_api = CollectingEventAPI()
    collecting_event_schema = CollectingEventSchema()

    # Modify a specific field in each collecting event
    for record in collecting_events:
        # Set the 'dwcVerbatimElevation' attribute to a new value
        record.attributes["dwcVerbatimElevation"] = "0.15"

    # Prepare the payload for bulk update, including only the modified field
    bulk_payload = prepare_bulk_payload(
        entities=collecting_events,
        include_fields=["dwcVerbatimElevation"]
    )

    # Print the bulk payload for inspection/debugging
    print(json.dumps(bulk_payload))

    # Send the bulk update request to the API
    response = collecting_event_api.bulk_update(bulk_payload)

    # print the response from the bulk update operation
    print(response.json())

# Entry point for script execution
if __name__ == "__main__":
    main()