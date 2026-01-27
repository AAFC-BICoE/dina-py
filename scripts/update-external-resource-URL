from dinapy.apis.objectstoreapi.objectstore_api import ObjectStoreAPI
from dinapy.schemas.metadata_schema import MetadataSchema
from dinapy.utils import *
from urllib.parse import urlparse
from pathlib import Path
import csv
import sys

# Configuration
CSV_FILENAME = "record_ids_guy.csv"  # Path to your CSV file
RESUME_ID = None # Default: process all. Can be set via command-line or manually.

object_store_schema = MetadataSchema()
dina_metadata_api = ObjectStoreAPI()

def update_fields(metadata_dto):
    attributes = metadata_dto.attributes
    caption = attributes.get("acCaption", "")
    extension = attributes.get("fileExtension", "")
    resource_url = attributes.get("resourceExternalURL", "")
    filename = attributes.get("filename", "")

    print("Before Update: \n", "Filename: ", filename, "\nCaption: ", caption, "\nExtension: ", extension, "\nResource URL: ", resource_url)

    # Update path: Replace grdi_eco with wp4/DINA_mount in the URL path
    if resource_url:
        # Replace grdi_eco with wp4/DINA_mount in the path
        if "grdi_eco" in resource_url:
            updated_url = resource_url.replace("/grdi_eco/", "/wp4/DINA_mount/")
            attributes["resourceExternalURL"] = updated_url
            print(f"Path updated: grdi_eco -> wp4/DINA_mount")

    print("After Update: \n", "Filename: ", attributes["filename"], "\nResource URL: ", attributes["resourceExternalURL"])
    return metadata_dto

# --- Main Script ---
# Read IDs from CSV
record_ids = []
with open(CSV_FILENAME, mode="r") as file:
    reader = csv.reader(file)
    for row in reader:
        if row:  # Skip empty rows
            record_ids.append(row[0])

print(f"Loaded {len(record_ids)} IDs from {CSV_FILENAME}")

# If resume flag is set, skip until that ID
if RESUME_ID:
    print(f"Resuming from ID: {RESUME_ID}")
    try:
        start_index = record_ids.index(RESUME_ID)
        record_ids = record_ids[start_index:]
    except ValueError:
        print(f"Resume ID {RESUME_ID} not found in CSV. Processing all records.")
else:
    print("Processing all records.")

# Process each record by ID
for record_id in record_ids:
    print(f"Processing record ID: {record_id}")
    response = dina_metadata_api.get_entity(record_id, "metadata")
    if response.status_code != 200:
        print(f"Failed to fetch record {record_id}: {response.status_code}")
        continue

    wrapped_json = {"data": response.json()["data"]}
    metadata_dto = object_store_schema.load(wrapped_json)

    if metadata_dto.attributes.get("resourceExternalURL") != "undefined":
        updated_metadata_dto = update_fields(metadata_dto)
        
        # Verify that the updated URL resolves to a real filesystem path
        updated_url = updated_metadata_dto.attributes.get("resourceExternalURL", "")
        parsed_url = urlparse(updated_url)
        
        # Extract the filesystem path from file:// URL
        if parsed_url.scheme == "file":
            file_path = parsed_url.path
            path_obj = Path(file_path)
            
            if path_obj.exists():
                print(f"✅ Path verified: {file_path}")
                
                # Proceed with update
                entity = object_store_schema.dump(updated_metadata_dto)
                print("Updating entity with data:", entity)
                if 'meta' in entity:
                    del entity['meta']
                update_response = dina_metadata_api.update_entity(updated_metadata_dto.get_id(), entity, "metadata")
                print(update_response.json())
            else:
                print(f"❌ Path does not exist: {file_path}")
                print(f"Skipping update for record {metadata_dto.id}")
        else:
            print(f"⚠️  URL is not a file:// scheme: {updated_url}")
            print(f"Skipping verification for record {metadata_dto.id}")
    else:
        print(f"Skipping record {metadata_dto.id}: resourceExternalURL is undefined")