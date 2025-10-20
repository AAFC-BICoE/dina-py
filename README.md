# dina-py

Python access to the DINA API

## Recommended Python and pip Versions

The features, tests, and installations were tested with Python 3.12 and pip 24.0 and are recommended for users to install. To do this, run the following commands:
```bash
sudo apt install python3
sudo apt install python3-pip
```

## Current Features

#### JSON-API serializer and deserializer with Marshmallow JSON-API
- Currently supported schemas:
    - Collecting Event
    - Storage Unit Usage
    - Person
    - Material Sample
    - Metadata
    - Storage Unit
    - Form Template
    - Split Configuration
    - Metagenomics Batch
    - Metagenomics Batch Item
    - Molecular Analysis Result
    - Molecular Analysis Run
    - Molecular Analysis Run Item
    - Project
#### DINA APIs
- Currently supported APIs:
    - Agent API
      - Person
    - Collection API
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

To help you configure your environment and credentials, we've provided an interactive Jupyter notebook:

👉 [Installation & Setup Notebook](notebooks/installation_guide.ipynb)


This notebook will guide you through:
- Entering your Keycloak credentials
- Setting up environment variables
- Saving a `.env` file for future use
- Testing your connection to the DINA API
