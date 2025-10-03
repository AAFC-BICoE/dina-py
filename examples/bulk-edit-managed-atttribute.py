# Import necessary modules
from ast import If
import json
import sys
import os
from marshmallow.exceptions import ValidationError

# Set up the project root path to allow importing local modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import DINA-related modules and utilities
from dinapy.apis.collectionapi.managedattributesapi import ManagedAttributeAPI
from dinapy.schemas.managedattributeschema import ManagedAttributesSchema
from dinapy.utils import *

# Set environment variables for authentication (replace with actual credentials or use a secure method)
os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

def main():
    # Initialize the ManagedAttribute API client (uses certificate-based authentication)
    managed_attribute_api = ManagedAttributeAPI()

    # Retrieve records from the API where the 'group' field matches 'aafc'
    records = managed_attribute_api.get_entity_by_field("group", "aafc").json()["data"]
    print(records)
    # Deserialize the first 10 records into ManagedAttribute objects using the schema
    managed_attributes = []
    for record in records[:10]:
        try:
            # Deserialize the record using Marshmallow schema
            managed_attribute = ManagedAttributesSchema().load({"data": record})
            if managed_attribute.attributes["multilingualDescription"]["descriptions"] is not None:
                managed_attributes.append(managed_attribute)
        except ValidationError as e:
            # Print validation errors and skip invalid records
            print(f"Validation error: {e}")
            continue

    print(f"Successfully parsed {len(managed_attributes)} managed attributes")

    # Re-initialize API and schema (optional, could reuse previous instances)
    managed_attribute_api = ManagedAttributeAPI()

    # Modify a specific field in each managed attribute
    for record in managed_attributes:
        # Set the 'multilingualDescription.descriptions' attribute to a new value
        record.attributes["multilingualDescription"]["descriptions"][0]["desc"] = "updated by bulk edit script"
        record.attributes["multilingualDescription"]["descriptions"][1]["desc"] = "updated by bulk edit script"

    # Prepare the payload for bulk update, including only the modified field
    bulk_payload = prepare_bulk_payload(
        entities=managed_attributes,
        include_fields=["name", "multilingualDescription"]
    )

    # Print the bulk payload for inspection/debugging
    print(json.dumps(bulk_payload))

    # Send the bulk update request to the API
    response = managed_attribute_api.bulk_update(bulk_payload)

    # print the response from the bulk update operation
    print(response)

# Entry point for script execution
if __name__ == "__main__":
    main()