import json
from pprint import pprint

import sys
import os

# Import for Metagenomics Batch
from dinapy.apis.seqdbapi.metagenomics_batch_api import MetagenomicsBatchApi
from dinapy.schemas.metagenomics_batch_pydantic import (
    MetagenomicsBatchDocument, MetagenomicsBatchData, MetagenomicsBatchAttributes
)

# Import for Metagenomics Batch Item
from dinapy.apis.seqdbapi.metagenomics_batch_item_api import MetagenomicsBatchItemApi
from dinapy.schemas.metagenomics_batch_item_pydantic import (
    MetagenomicsBatchItemDocument, MetagenomicsBatchItemData, MetagenomicsBatchItemAttributes
)

from dinapy.schemas.pydantic_base import RelationshipData, RelationshipLinkage

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
    # Set Metagenomics Batch Attributes and Relationships
    metagenomics_batch_api = MetagenomicsBatchApi()
    serialized_metagenomics_batch = MetagenomicsBatchDocument(
        data=MetagenomicsBatchData(
            type="metagenomics-batch",
            attributes=MetagenomicsBatchAttributes(
                createdBy="dina-admin",
                group="aafc",
                name="metagenomics-batch-test"
            ),
            relationships={
                "indexSet": RelationshipData(
                    data=RelationshipLinkage(type="index-set", id="456036bc-6fa6-4779-b028-ec26a7b7e6dd")
                )
            }
        )
    ).serialize()

    # Create Metagenomics Batch
    metagenomics_batch_response = metagenomics_batch_api.create_entity(serialized_metagenomics_batch)
    batch_id = metagenomics_batch_response.json()['data']['id']
    print(f"Metagenomics Batch: {batch_id} created\n")

    for item in PCR_BATCH_ITEMS:
        # Set Metagenomics Batch Item Attributes and Relationships
        metagenomics_batch_item_api = MetagenomicsBatchItemApi()
        serialized_metagenomics_batch_item = MetagenomicsBatchItemDocument(
            data=MetagenomicsBatchItemData(
                type="metagenomics-batch-item",
                attributes=MetagenomicsBatchItemAttributes(
                    createdBy="dina-admin"
                ),
                relationships={
                    "metagenomicsBatch": RelationshipData(
                        data=RelationshipLinkage(type="metagenomics-batch", id=batch_id)
                    ),
                    "pcrBatchItem": RelationshipData(
                        data=RelationshipLinkage(type="pcr-batch-item", id=item)
                    )
                }
            )
        ).serialize()

        # Create Metagenomics Batch Item
        metagenomics_batch_item_response = metagenomics_batch_item_api.create_entity(serialized_metagenomics_batch_item)
        batch_item_id = metagenomics_batch_item_response.json()['data']['id']
        print(f"Metagenomics Batch Item: {batch_item_id} created\n")

if __name__ == "__main__":
    main()