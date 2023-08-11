# dina-py

Python access to the DINA API

## Current Features

* JSON-API serializer and deserializer with Marshmallow JSON-API (schemas.py, currently only PersonSchema)
* GET request for a Person (PersonAPI)

## How to extend functionality 

* To extend functionality, create subclasses from DinaAPI and extend the base_url attribute with the full URL for the API call required
* Then create new methods for GET, POST, PATCH, etc. and use the base DinaAPI request functions.
    * Have the methods return objects of the entity class in the future
* Create a Schema using Marshmallow JSON-API for the entity and use it for serialization and deserialization.
* Try to create tests.

## Example API Usage

In code:
```py
from dinaapi import PersonAPI

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
* A way to refresh the token when it is expired.
* A way to re-use tokens when making different API calls.
* Implement and test the other request types for Person.
* Add support for other Dina entities.
* 
## Tests

* 2 tests only, both for PersonSchema, testing deserialization only
* Can run tests directly from test file
