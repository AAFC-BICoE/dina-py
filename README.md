# dina-py

Python access to the DINA API

## Current Features

* JSON-API serializer and deserializer with Marshmallow JSON-API (schemas.py, currently only PersonSchema)
* GET request for a Person (PersonAPI)

## Example Usage

```py
from dinaapi import PersonAPI

// GET request
pAPI = PersonAPI("keycloak config path")
person = pAPI.find("my uuid") // returns deserialized JSON as dict
```

## Notes

* Only the find() method for PersonAPI has been tested to work. The other requests (POST, PATCH, DELETE) have not been tested and should be re-implemented or modified.
* Furthermore, the PersonSchema serializes and deserialized correctly in the context of the find() method.
* Keycloak username and password must be set as environemental variables (keycloak_username and keycloak_password). Can be set using os.environ if needed.

## Todo

* Develop models in order to have an object returned rather than a dictionary for the requests.
* A way to refresh the token when it is expired.
* A way to re-use tokens when making different API calls.
