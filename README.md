# dina-py

Python access to the DINA API

## Recommended Python and pip Versions

The features, tests, and installations were tested with Python 3.12 and pip 24.0 and are recommended for users to install. To do this, run the following commands:
```bash
sudo apt install python3
sudo apt install python3-pip
```

## Current Features

#### JSON:API serialization and deserialization with Pydantic v2

Each resource exposes a `Document` class (e.g. `CollectingEventDocument`) that wraps the JSON:API envelope.  The two key methods are:

- **`Document.deserialize(response_dict)`** — parses an API response; `null` attribute values are stripped so they are never accidentally sent back in a PATCH request.
- **`doc.serialize()`** — produces a request payload; only fields that were explicitly set (or mutated after deserialization) are included, using Pydantic's `model_fields_set` tracking.

**Safe PATCH pattern:**
```python
# GET → mutate → PATCH (only changed fields are sent)
response = api.get_entity(uuid)
doc = CollectingEventDocument.deserialize(response.json())
doc.data.attributes.dwcVerbatimElevation = "0.15"   # only this field goes in the payload
api.update_entity(uuid, doc.serialize())

# To intentionally clear a field on the server, assign None after deserializing
doc.data.attributes.verbatimLatitude = None
api.update_entity(uuid, doc.serialize())   # → {"verbatimLatitude": null}
```

**POST (create) pattern:**
```python
# Only set the fields you want — the server defaults the rest to null
doc = CollectingEventDocument(
    data=CollectingEventData(
        type="collecting-event",
        attributes=CollectingEventAttributes(group="aafc", createdBy="dina-admin"),
    )
)
api.create_entity(doc.serialize())
```

Currently supported schemas:
- Association
- Collecting Event
- Form Template
- Managed Attribute
- Material Sample
- Metadata
- Metagenomics Batch
- Metagenomics Batch Item
- Molecular Analysis Result
- Molecular Analysis Run
- Molecular Analysis Run Item
- Person
- Project
- Split Configuration
- Storage Unit Usage
#### DINA APIs
- Currently supported APIs:
    - Agent API
      - Person
    - Collection API
      - Association
      - CollectingEvent
      - StorageUnit
      - StorageUnitUsage
      - FormTemplate
      - SplitConfiguration
      - MaterialSample
      - Organism
      - Project
    - Object Store API
      - Any Object Store API endpoint using ObjectStoreApi's CRUD methods 
    - SeqDB API
      - PCR Batch
      - PCR Batch Item
      - SEQ Reaction
      - Metagenomics Batch
      - Metagenomics Batch Item
      - Molecular Analysis Result
      - Molecular Analysis Run
      - Molecular Analysis Run Item
    - Export API
      - Any Export API endpoint using DinaExportApi's CRUD methods 
  
#### DINA_API_CLIENT
#### Currently supported operations:
   **upload_file:**
   - metavar="<file_path> : (str) = Path to the file to be uploaded.",
   - help="Upload a file to Object Store. Argument: file_path"
     
   **upload_dir:**
   - metavar="<dir_path> : (str) = Path to the directory to be uploaded.",
   - help="Upload all files in a directory to Object Store",
   
   **verbose:**
   - help="Verbosity of logs. Primarily for debugging.",
   - action="store_true",

   **create_metadatas:**
   - metavar="<dir_path> : (str) = Path to the directory to be uploaded.",
   - help="Upload all files in a directory to Object Store and create metadatas according to constants defined in ./dina-api-config.yml",

   **create_form_template:**
   - metavar="<file_path> : (str) = Path to the file to be parsed and created.",
   - help="Create a form template according to specs defined in a yaml file such as ./form-template-sample.yml",

   **create_split_configuration:**
   - metavar="<file_path> : (str) = Path to the file to be parsed and created.",
   - help="Create a split configuration according to specs defined in a yaml file such as ./split-configuration-sample.yml",

#### TEST COVERAGE
- APIs (Unit Test with Magic Mock):
    - Collection API
      - Collecting Event
      - Managed Attributes
      - Material Sample
      - Organism
    - Object Store API
      - Metadata
      - Object Export
    - Agent API
      - Person
    - Export API
      - Data Export
- Schemas:
   - Collecting Event
   - Form Template
   - Managed Attribute
   - Material Sample
   - Metadata
   - Person
   - Split Configuration
   - Storage Unit Usage
   - Metagenomics Batch
   - Metagenomics Batch Item
   - Molecular Analysis Result
   - Molecular Analysis Run
   - Molecular Analysis Run Item
   - Project


## 🔧 Installation & Setup

### Installation

#### From PyPI (recommended)

```bash
# Latest stable release
pip install dinapy

# Upgrade to the latest version
pip install --upgrade dinapy

# With optional dependencies for Jupyter notebooks
pip install "dinapy[notebook]"

# With test dependencies
pip install "dinapy[test]"

# Multiple optional dependency groups
pip install "dinapy[notebook,test]"
```

#### From source (contributors / development)

```bash
# Clone the repository
git clone https://github.com/AAFC-BICoE/dina-py.git
cd dina-py

# Editable install (changes to source are reflected immediately)
pip install -e .

# Editable install with optional dependencies
pip install -e ".[notebook,test]"
```

**Note:** This package uses modern Python packaging with `pyproject.toml` as the single source of truth for dependencies and metadata (PEP 517/518).

### Configuration

To help you configure your environment and credentials, we've provided an interactive Jupyter notebook:

👉 [Installation & Setup Notebook](notebooks/installation_guide.ipynb)

This notebook will guide you through:
- Entering your Keycloak credentials
- Setting up environment variables
- Saving a `.env` file for future use
- Testing your connection to the DINA API
