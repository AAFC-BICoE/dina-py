

from dinapy.apis.objectstoreapi.objectstore_api import ObjectStoreAPI
from dinapy.schemas.metadata_schema import MetadataSchema
from dinapy.utils import *
import csv

GROUP_NAME = "guy-lab"

dina_metadata_api = ObjectStoreAPI()
records_list = get_dina_records_by_field(dina_metadata_api,"bucket",GROUP_NAME)
object_store_schema = MetadataSchema()

# Extract IDs
record_ids = []
for record in records_list:
    record_id = record["id"]
    record_ids.append(record_id)

# Save IDs to CSV
csv_filename = "record_ids_guy.csv"
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    for rid in record_ids:
        writer.writerow([rid])