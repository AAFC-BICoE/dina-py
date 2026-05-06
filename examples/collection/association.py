from dinapy.apis.collectionapi.associationapi import AssociationAPI
from dinapy.schemas.association_pydantic import AssociationDocument, AssociationData, AssociationAttributes
from dinapy.schemas.pydantic_base import RelationshipData, RelationshipLinkage
import json

association_api = AssociationAPI()

# ── 1. List all associations ───────────────────────────────────────────────────
response = association_api.get_associations()
print("All associations:")
print(json.dumps(response.json(), indent=2))

# ── 2. Filter by sample UUID ───────────────────────────────────────────────────
SAMPLE_UUID = "019df927-a199-7399-b279-e2f648236731"  # replace with a real UUID

response = association_api.get_associations_by_sample_uuid(
    SAMPLE_UUID,
    include=["associatedSample", "sample"],
)
print(f"\nAssociations for sample {SAMPLE_UUID}:")
print(json.dumps(response.json(), indent=2))

# ── 3. Fetch a single association by UUID ─────────────────────────────────────
ASSOCIATION_UUID = "019df928-4fbe-717d-aaa2-8a8d7e5f8d2e"  # replace with a real UUID

response = association_api.get_entity(ASSOCIATION_UUID)
doc = AssociationDocument.deserialize(response.json())
print(f"\nSingle association {ASSOCIATION_UUID}:")
print(f"  type        : {doc.data.attributes.associationType}")
print(f"  remarks     : {doc.data.attributes.remarks}")
print(f"  createdBy   : {doc.data.attributes.createdBy}")
print(f"  createdOn   : {doc.data.attributes.createdOn}")

# ── 4. Create a new association ────────────────────────────────────────────────
new_doc = AssociationDocument(
    data=AssociationData(
        type="association",
        attributes=AssociationAttributes(
            associationType="has_host",
            remarks="test remark",
        ),
        relationships={
            "sample": RelationshipData(
                data=RelationshipLinkage(type="material-sample", id="019df927-a178-7465-b73e-36a127a2b2ca")
            ),
            "associatedSample": RelationshipData(
                data=RelationshipLinkage(type="material-sample", id="019df927-a1d4-7777-88cd-0e19a50b9785")
            ),
        },
    )
)
create_response = association_api.create_entity(new_doc.serialize())
print("\nCreate response status:", create_response.status_code)
if create_response.status_code in (200, 201):
    created = AssociationDocument.deserialize(create_response.json())
    print("Created association UUID:", created.data.id)
