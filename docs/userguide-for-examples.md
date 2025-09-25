
# 📁 Examples Folder Guide

This README provides instructions for running the example scripts located in the `examples` folder. These scripts demonstrate how to interact with the DINA API for various operations such as bulk editing and record deletion.

---

## 📂 Folder Structure

```
examples/
├── collection/
    ├── bulk-edit-collecting-event.py
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
├── retrieve_delete_organism_api_test.py
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

Ensure the following Python packages are installed:

```bash
pip install marshmallow
```

Also make sure the `dinapy` package and its modules are available in your Python path.

---

## 📜 Script Descriptions

### `bulk-edit-collecting-event.py`

- Retrieves collecting event records filtered by group `"aafc"`.
- Deserializes the first 10 records.
- Updates the `dwcVerbatimElevation` field to `"0.15"`.
- Prepares and sends a bulk update payload.

---

## `managed_attributes_api_test.py`
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

## `data_export_test.py`
This script tests the export functionality of the DINA object store module:

- Authenticates using environment variables (`keycloak_username`, `keycloak_password`).
- Retrieves metadata for a file named `"object_upload - Copy.png"` using a filter.
- Extracts the `fileIdentifier` from the metadata.
- Creates an object export request using that identifier.
- Downloads the exported object using the DINA API.

---

## `external_resource_importer.py`
This script imports external resources and links them to newly created material samples:

- Reads a dataset file line-by-line to extract file paths and names.
- Constructs metadata for each file (e.g., type, format, URL, bucket).
- Uploads metadata to the DINA object store.
- Creates a relationship between the metadata and a new material sample.
- Builds and uploads the material sample object.
- Logs the UUIDs of created resources and handles errors (e.g., duplicate files).

---

## `link_samples_to_project.py`
This script links existing material samples to a specific project:

- Uses a predefined project UUID.
- Builds a relationship object linking material samples to the project.
- Reads UUIDs of material samples from a file.
- Updates each material sample to include the project relationship.
- Logs successful updates and errors.

---

## `metadata_api_test.py`
This script tests the metadata creation functionality:

- Loads configuration from a YAML file.
- Uses the DINA API client to scan a directory for files.
- Creates metadata records for each file found.

---

## `object_export_test.py`
This script tests the object export functionality:

- Retrieves metadata for a specific file using a filter.
- Extracts the `fileIdentifier` from the metadata.
- Creates an object export request using that identifier.
- Sends the request to the DINA API and prints the response.

---

## `metagenomic_batch_create_test.py`
This script creates a metagenomics batch and associated batch items:

- Builds relationships to a predefined index set and PCR batch items.
- Sets attributes for the metagenomics batch and items.
- Creates the batch and each item using the DINA API.
- Prints the UUIDs of the created batch and items.

---

## `molecular_analysis_run_create_test.py`
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