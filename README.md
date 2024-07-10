# dina-py

Python access to the DINA API

## Current Features

* JSON-API serializer and deserializer with Marshmallow JSON-API (schemas.py, currently only PersonSchema)
* GET request for a Person (PersonAPI)

## Installation Instructions

### Dina-scripts usage

From inside of the dina-scripts docker container, the dina-py library can be installed using the 
GitHub branch you wish to install:

```bash
pip install "https://github.com/AAFC-BICoE/dina-py/archive/refs/heads/dev.zip"
```

Running the command above will install the `dev` branch. Any branch name can be used.

### Local Install

Before installing, it's recommended to use a virtual environment in python but not required. create 
a virtual environment for the dependencies required.

```bash
sudo apt install python3.10-venv
python3 -m venv env
source env/bin/activate
```

Install the library and all required dependencies:

```bash
python3 -m pip install .
```

Then it can be imported using:

```py
from dinapy.api.agentapi.personapi import PersonAPI
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

## How to extend functionality 

* To extend functionality, create subclasses from DinaAPI and extend the base_url attribute with the full URL for the API call required
* Then create new methods for GET, POST, PATCH, etc. and use the base DinaAPI request functions.
    * Have the methods return objects of the entity class in the future
* Create a Schema using Marshmallow JSON-API for the entity and use it for serialization and deserialization.
* Try to create tests.

## Example API Usage

In code:
```py
from dinapy.api.agentapi.personapi import PersonAPI

// GET request
pAPI = PersonAPI("keycloak config path")
person = pAPI.find("my uuid") // returns deserialized JSON as dict

serialized_data = person_schema.dump(person) // serialize dict back to valid JSON
```

Deserialized data:
```json
    {
        "id": "bfa3c68b-8e13-4295-8e25-47dbe041cb64",
        "attributes": {
            "displayName": "testBob",
            "email": "bob.builder@agr.gc.ca",
            "createdBy": "cnc-su",
            "createdOn": datetime.datetime(
                2023, 2, 20, 16, 18, 10, 688627, tzinfo=datetime.timezone.utc
            ),
            "givenNames": "Bob",
            "familyNames": "Builder",
            "aliases": ["Yes we can"],
            "webpage": None,
            "remarks": None,
        },
        "meta": {"totalResourceCount": 1, "moduleVersion": "0.24"},
    }
```

Serialized Data:
```json
{
    "data": {
        "type": "person",
        "id": "bfa3c68b-8e13-4295-8e25-47dbe041cb64",
        "attributes": {
            "displayName": "testBob",
            "email": "bob.builder@agr.gc.ca",
            "createdBy": "cnc-su",
            "createdOn": "2023-02-20T16:18:10.688627+00:00",
            "givenNames": "Bob",
            "familyNames": "Builder",
            "aliases": ["Yes we can"],
            "webpage": None,
            "remarks": None,
        },
        "relationships": {
            "identifiers": {
                "links": {
                    "self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/relationships/identifiers",
                    "related": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/identifiers",
                }
            },
            "organizations": {
                "links": {
                    "self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/relationships/organizations",
                    "related": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64/organizations",
                }
            },
        },
        "links": {"self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64"},
    },
    "links": {"self": "/api/v1/person/bfa3c68b-8e13-4295-8e25-47dbe041cb64"},
    "meta": {"totalResourceCount": 1, "moduleVersion": "0.24"},
}
```

## Notes

* Only the find() method for PersonAPI has been tested to work. The other requests (POST, PATCH, DELETE) have not been tested and should be re-implemented or modified.
* Furthermore, the PersonSchema serializes and deserialized correctly in the context of the find() method.
* Keycloak username and password must be set as environmental variables (keycloak_username and keycloak_password). Can be set using os.environ if needed.

## Todo

* Develop models in order to have an object returned rather than a dict for the request return types.
* A way to re-use tokens when making different API calls.
* Implement and test the other request types for Person.
* Add support for other Dina entities.

## Tests

* 2 tests only, both for PersonSchema, testing deserialization only
* Can run tests directly from test file

## Object Upload Demo (Windows)

* Install Python (3.10 or above, tested with 3.12), opt to 'Add Python to PATH' when asked during installation.
* Open a command prompt terminal and clone the dina-py repo:
```py
C:\> git clone -b dev https://github.com/AAFC-BICoE/dina-py.git
```
* Change directory into the dina-py folder
```py
C:\dina-py> cd dina-py
```
* Create a Python virtual environment (venv):
```py
C:\dina-py> python -m venv <venv_name>
```
This should create a <venv_name> folder
* Activate venv by executing the .bat. You can tell the venv is active if there is a (<venv_name>) in front of the normal directory path:
```py
C:\dina-py> <venv_name>\Scripts\activate.bat
(.venv) C:\dina-py>
```
* Install the dina-py project
```py
(.venv) C:\dina-py> pip install .
```
* Make a copy of **keycloak-config-sample.yml** and rename to **keycloak-config.yml** in the root of dina-py directory
* From the dina-py directory's root, create a folder <object_upload_dir> containing the files to be uploaded
* From the dina-py directory's root, run the following command to upload all contents in <object_upload_dir>:
```py
(.venv) C:\dina-py> python .\dinapy\client\dina_api_client.py -upload_dir '<object_upload_dir>' -group <user_group>
```
* Or run the following command to upload a specific file:
```py
(.venv) C:\dina-py> python .\dinapy\client\dina_api_client.py -upload_file '<object_upload_dir>/<file_name>' -group <user_group>
```
* Note: Currently, the keycloak user that creates the resources is hardcoded to be **dina-admin**