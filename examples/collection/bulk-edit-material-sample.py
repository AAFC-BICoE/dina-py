# Import necessary modules
import json
import sys
import os
from pydantic import ValidationError

# Set up the project root path to allow importing local modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import DINA-related modules and utilities
from dinapy.apis.collectionapi.materialsampleapi import MaterialSampleAPI
from dinapy.schemas.material_sample_pydantic import MaterialSampleDocument
from dinapy.utils import *

# Set environment variables for authentication (replace with actual credentials or use a secure method)
# os.environ["keycloak_username"] = "dina-admin"
# os.environ["keycloak_password"] = "dina-admin"

def main():
    # Initialize the MaterialSample API client (uses certificate-based authentication)
    material_sample_api = MaterialSampleAPI()

    # Retrieve records from the API where the 'group' field matches 'aafc'
    records = get_dina_records_by_field(material_sample_api, "group", "aafc")

    # Deserialize the first 5 records into MaterialSample objects using the schema
    material_samples = []
    for record in records[:5]:  # Limit to first 5 records for testing
        try:
            # Deserialize the record using Pydantic schema
            doc = MaterialSampleDocument.deserialize(record)
            material_samples.append(doc.data)
        except ValidationError as e:
            # Print validation errors and skip invalid records
            print(f"Validation error: {e}")
            continue

    print(f"Successfully parsed {len(material_samples)} material samples")

    # Re-initialize API (optional, could reuse previous instance)
    material_sample_api = MaterialSampleAPI()

    # Modify a specific field in each material sample
    for material_sample in material_samples:
        # Set the 'preparationRemarks' attribute to a new value
        material_sample.attributes.preparationRemarks = "test-preparation-remarks"

    # Prepare the payload for bulk update, including only the modified field
    bulk_payload = prepare_bulk_payload(
        entities=material_samples,
        include_fields=["preparationRemarks"]
    )

    # Print the bulk payload for inspection/debugging
    print(json.dumps(bulk_payload))

    # Send the bulk update request to the API
    response = material_sample_api.bulk_update(bulk_payload)

    # print the response from the bulk update operation
    print(response)

# Entry point for script execution
if __name__ == "__main__":
    main()