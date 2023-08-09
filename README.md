# dina-py

Python access to the DINA API

## Current Features

* JSON-API serializer and deserializer with Marshmallow JSON-API (schemas.py)
* GET, POST, PATCH, and DELETE requests for a Person (PersonAPI)

## Example Usage

```py
from dinaapi import PersonAPI

// GET request
pAPI = PersonAPI("keycloak config path")
person = pAPI.find("my uuid") // returns deserialized JSON as dict
```