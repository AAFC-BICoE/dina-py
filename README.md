# dina-py

Python access to the DINA API

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
    - Object Store API
      - Any Object Store API endpoint using ObjectStoreApi's CRUD methods 
    - SeqDB API
      - PCR Batch
      - PCR Batch Item
      - SEQ Reaction
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

## Installation Instructions
### Local Install

Before installing, it's recommended to use a virtual environment in python but not required. create 
a virtual environment for the dependencies required.

```bash
sudo apt install python3.10-venv
python3 -m venv env
source env/bin/activate
```
From inside of the dina-py root folder, install the library and all required dependencies:

```bash
pip install -e .
pip install -r requirements.txt
```

The username and password are set via environment variables. This can be done via the command line:

```bash
set keycloak_username=username
set keycloak_password=password
```

Or programmatically using:

```py
os.environ["keycloak_username"] = "username"
os.environ["keycloak_password"] = "password"
```

* Make a copy of **keycloak-config-sample.yml** and rename to **keycloak-config.yml** in the root of dina-py directory, open **keycloak-config.yml** using Notepad
* In **keycloak-config.yml**, change **url, keycloak_username, keycloak_password** as needed
* Make a copy of **dina-api-config-sample.yml** and rename to **dina-api-config.yml** in the root of dina-py directory, open **dina-api-config.yml** using Notepad

Sample usage of DINA_API_CLIENT:
```py
(.venv) C:\Users\<your_account>\dina-py> python .\dinapy\client\dina_api_client.py -upload_dir '<object_upload_dir>'
```
* Or run the following command to upload a specific file:
```py
(.venv) C:\Users\<your_account>\dina-py> python .\dinapy\client\dina_api_client.py -upload_file '<object_upload_dir>/<file_name>'
```

## Example API Usage

In code:
```py

def test_create_delete_entity(self):
   schema = MaterialSampleSchema()
   material_sample_api = MaterialSampleAPI()
   try:
      material_sample_attributes = MaterialSampleAttributesDTOBuilder().group("aafc").materialSampleName("test").materialSampleType("WHOLE_ORGANISM")\
      .build()
      material_sample = MaterialSampleDTOBuilder().attributes(material_sample_attributes).build()
      serialized_material_sample = schema.dump(material_sample)
      pp = pprint.PrettyPrinter(indent=0)
      pp.pprint(serialized_material_sample)
      response = material_sample_api.create_entity(serialized_material_sample)
      id = response.json()['data']['id']
      if response.status_code == 201:
         response = material_sample_api.remove_entity(id)
         self.assertEqual(response.status_code,204)
   except ValidationError as e:
      self.fail(f"Validation failed with error: {e.messages}")