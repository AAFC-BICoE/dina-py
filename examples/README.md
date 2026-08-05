
# 📁 Examples Folder Guide

This README provides instructions for running the example scripts located in the `examples` folder. These scripts demonstrate how to interact with the DINA API for various operations such as bulk editing and record deletion.

---

## 📂 Folder Structure

```
examples/
├── collection/
    ├── association.py
    ├── bulk-edit-collecting-event.py
    ├── bulk-edit-material-sample.py
    ├── managed_attributes_api_test.py
    └── retrieve_delete_organism_api_test.py
├── data-export/
    └── data_export_test.py
├── object-store/
    ├── metadata_api_test.py
    ├── object_export_test.py
├── external-resource-import-demo/
    ├── external_resource_importer.py
    ├── link_samples_to_project.py
├── seqdb/
    ├── metagenomic_batch_create_test.py
    ├── molecular_analysis_run_create_test.py
└── api-query-and-record/
    ├── main.py
    ├── keycloak-config.sample.yml
    └── README.md


```

---

## ⚙️ Setup Instructions

### 1. Environment Variables

Before running any script, set the following environment variables:

```bash
export keycloak_username="your_username"
export keycloak_password="your_password"
```

Alternatively, you can hardcode them in the scripts:

```python
os.environ["keycloak_username"] = "your_username"
os.environ["keycloak_password"] = "your_password"
```

### 2. Dependencies

Make sure the `dinapy` package and its dependencies are installed:

```bash
pip install -e .
```

All serialization uses **Pydantic v2** — there is no marshmallow dependency.

---

## � Pydantic Round-Trip Pattern

All scripts that interact with the API follow the same serialization pattern powered by Pydantic v2.

### Creating a new record (POST)

Only set the fields you want. The server will default anything you leave out to `null` — do not pass `None` in the constructor for fields you don't care about.

```python
from dinapy.schemas.association_pydantic import AssociationDocument, AssociationData, AssociationAttributes
from dinapy.schemas.pydantic_base import RelationshipData, RelationshipLinkage

doc = AssociationDocument(
    data=AssociationData(
        type="association",
        attributes=AssociationAttributes(
            associationType="has_host",
            remarks="collected together",
        ),
        relationships={
            "sample": RelationshipData(data=RelationshipLinkage(type="material-sample", id="<uuid>")),
            "associatedSample": RelationshipData(data=RelationshipLinkage(type="material-sample", id="<uuid>")),
        },
    )
)
api.create_entity(doc.serialize())
```

See [`collection/association.py`](collection/association.py) for a full create + list + fetch example.

### Updating a record (PATCH)

Deserialize the API response, mutate only the fields you want to change, then serialize back. Fields that came in as `null` from the API are stripped at deserialize time and will not appear in the payload unless you explicitly assign them.

```python
from dinapy.schemas.collecting_event_pydantic import CollectingEventDocument

response = collecting_event_api.get_entity(uuid)
doc = CollectingEventDocument.deserialize(response.json())

# Change one field — only this field ends up in the PATCH payload
doc.data.attributes.dwcVerbatimElevation = "0.15"
collecting_event_api.update_entity(uuid, doc.serialize())

# To intentionally clear a field on the server, assign None after deserializing
doc.data.attributes.verbatimLatitude = None
collecting_event_api.update_entity(uuid, doc.serialize())  # sends {"verbatimLatitude": null}
```

See [`collection/bulk-edit-collecting-event.py`](collection/bulk-edit-collecting-event.py) and [`collection/bulk-edit-material-sample.py`](collection/bulk-edit-material-sample.py) for bulk PATCH examples.

---

## 📜 Script Descriptions

### `association.py`

Demonstrates the full lifecycle of an Association record using Pydantic:

- Lists all associations.
- Filters associations by sample UUID.
- Fetches and deserializes a single association.
- Creates a new association with `sample` and `associatedSample` relationships.

---

### `bulk-edit-collecting-event.py`

- Retrieves collecting event records filtered by group `"aafc"`.
- Deserializes each record with `CollectingEventDocument.deserialize()`.
- Mutates `dwcVerbatimElevation` on the deserialized object (only that field appears in the PATCH payload).
- Sends a bulk update via `bulk_update()`.

---

### `bulk-edit-material-sample.py`

- Retrieves material sample records filtered by group `"aafc"`.
- Deserializes each record with `MaterialSampleDocument.deserialize()`.
- Mutates `preparationRemarks` on the deserialized object.
- Sends a bulk update via `bulk_update()`.

---

### `managed_attributes_api_test.py`
This script tests the creation of managed attributes:

- Builds a managed attribute with properties like name, type, group, and component.
- Serializes the attribute and sends it to the DINA API.
- Prints the UUID of the created managed attribute.

---

### `retrieve_delete_organism_api_test.py`

- Retrieves a specific organism record by UUID.
- Prints the retrieved record.
- Deletes the same record.
- Prints the HTTP status code of the delete operation.

---

### `data_export_test.py`
This script tests the export functionality of the DINA object store module:

- Authenticates using environment variables (`keycloak_username`, `keycloak_password`).
- Retrieves metadata for a file named `"object_upload - Copy.png"` using a filter.
- Extracts the `fileIdentifier` from the metadata.
- Creates an object export request using that identifier.
- Downloads the exported object using the DINA API.

---

### `external_resource_importer.py`
This script imports external resources and links them to newly created material samples:

- Reads a dataset file line-by-line to extract file paths and names.
- Constructs metadata for each file (e.g., type, format, URL, bucket).
- Uploads metadata to the DINA object store.
- Creates a relationship between the metadata and a new material sample.
- Builds and uploads the material sample object.
- Logs the UUIDs of created resources and handles errors (e.g., duplicate files).

---

### `link_samples_to_project.py`
This script links existing material samples to a specific project:

- Uses a predefined project UUID.
- Builds a relationship object linking material samples to the project.
- Reads UUIDs of material samples from a file.
- Updates each material sample to include the project relationship.
- Logs successful updates and errors.

---

### `metadata_api_test.py`
This script tests the metadata creation functionality:

- Loads configuration from a YAML file.
- Uses the DINA API client to scan a directory for files.
- Creates metadata records for each file found.

---

### `object_export_test.py`
This script tests the object export functionality:

- Retrieves metadata for a specific file using a filter.
- Extracts the `fileIdentifier` from the metadata.
- Creates an object export request using that identifier.
- Sends the request to the DINA API and prints the response.

---

### `metagenomic_batch_create_test.py`
This script creates a metagenomics batch and associated batch items:

- Builds relationships to a predefined index set and PCR batch items.
- Sets attributes for the metagenomics batch and items.
- Creates the batch and each item using the DINA API.
- Prints the UUIDs of the created batch and items.

---

### `molecular_analysis_run_create_test.py`
This script creates a molecular analysis run and associated entities:

- Initializes a molecular analysis run with attributes like name and group.
- Iteratively creates 10 molecular analysis results.
- For each result, creates a run item and links it to the result and run.
- For each run item, creates a sequencing reaction and links it to the item.
- Prints UUIDs for all created entities.

---

## 🧪 Notes

- These scripts are functional examples and can be adapted into unit tests.
- Use caution when running delete operations in production environments.
- You may extend these examples to cover more API endpoints or data models.