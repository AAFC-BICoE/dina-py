import json
from pprint import pprint

import sys
import os

# Import for Metagenomics Batch
from dinapy.apis.seqdbapi.metagenomics_batch_api import MetagenomicsBatchApi
from dinapy.schemas.metagenomics_batch_schema import MetagenomicsBatchSchema
from dinapy.entities.MetagenomicsBatch import *

# Import for Metagenomics Batch Item
from dinapy.apis.seqdbapi.metagenomics_batch_item_api import MetagenomicsBatchItemApi
from dinapy.schemas.metagenomics_batch_item_schema import MetagenomicsBatchItemSchema
from dinapy.entities.MetagenomicsBatchItem import *

from dinapy.entities.Relationships import RelationshipDTO

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# List of pre-made PCR Batch Item UUIDs
PCR_BATCH_ITEMS = [
    "bae9440e-7029-43e2-9ddb-ab3912187189",
    "e0eb9dba-c588-4252-b97a-92576f5613d2",
    "ffdc42d2-5701-401e-bb2e-b13eec9fb22b",
    "5e6b7a61-5a8d-43ec-8dee-4c5aa24ca31b",
    "300b6407-b67b-49be-9013-5379d7989f9f"
    ]

def main():
    # Build Relationship for Metagenomics Batch
    # using a pre-made Index Set in DINA-dev2
    batch_relationship = (
        RelationshipDTO.Builder()
            .add_relationship(
                "indexSet",
                "index-set",
                "456036bc-6fa6-4779-b028-ec26a7b7e6dd"
            ).build()
    )

    # Set Metagenomics Batch Attributes and Relationships
    metagenomics_batch_api = MetagenomicsBatchApi()
    metagenomics_batch_schema = MetagenomicsBatchSchema()
    metagenomics_batch_attributes = MetagenomicsBatchAttributesDTOBuilder(
      ).set_createdBy("dina-admin").set_group("aafc").set_name("metagenomics-batch-test").build()
    metagenomics_batch = MetagenomicsBatchDTOBuilder(
      ).set_relationships(batch_relationship).set_attributes(metagenomics_batch_attributes).build()

    serialized_metagenomics_batch = metagenomics_batch_schema.dump(metagenomics_batch)

    # print(f"{serialized_metagenomics_batch}\n")

    # Create Metagenomics Batch
    metagenomics_batch_response = metagenomics_batch_api.create_entity(serialized_metagenomics_batch)
    batch_id = metagenomics_batch_response.json()['data']['id']
    print(f"Metagenomics Batch: {batch_id} created\n")

    with open("./uuids.txt", "a") as f:
        print(f"Metagenomics Batch: {batch_id} created", file=f)

    for item in PCR_BATCH_ITEMS:
        # Build Relationships for Metagenomics Batch Items
        batch_item_relationship = (
            RelationshipDTO.Builder()
                .add_relationship(
                    "metagenomicsBatch",
                    "metagenomics-batch",
                    batch_id
                ).add_relationship(
                    "pcrBatchItem",
                    "pcr-batch-item",
                    item
                ).build()
        )

        # Set Metagenomics Batch Item Attributes and Relationships
        metagenomics_batch_item_api = MetagenomicsBatchItemApi()
        metagenomics_batch_item_schema = MetagenomicsBatchItemSchema()
        metagenomics_batch_item_attributes = MetagenomicsBatchItemAttributesDTOBuilder(
            ).set_createdBy("dina-admin").build()
        metagenomics_batch_item = MetagenomicsBatchItemDTOBuilder(
            ).set_relationships(batch_item_relationship).set_attributes(metagenomics_batch_item_attributes).build()

        serialized_metagenomics_batch_item = metagenomics_batch_item_schema.dump(metagenomics_batch_item)

        # print(f"{serialized_metagenomics_batch_item}\n")

        # Create Metagenomics Batch Item
        metagenomics_batch_item_response = metagenomics_batch_item_api.create_entity(serialized_metagenomics_batch_item)
        batch_item_id = metagenomics_batch_item_response.json()['data']['id']
        print(f"Metagenomics Batch Item: {batch_item_id} created\n")

        with open("./uuids.txt", "a") as f:
            print(f"Metagenomics Batch Item: {batch_item_id} created",file=f)

if __name__ == "__main__":
    main()