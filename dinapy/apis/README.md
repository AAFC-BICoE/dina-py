# apis

* Currently supported apis are for collection-module (material-sample & collecting-event) and person-api in agent-module.

## Current Features

* JSON-API serializer and deserializer with Marshmallow JSON-API (present in schemas folder)
* GET request for all apis (PersonAPI, CollectingEventAPI, MaterialSampleAPI) - Includes get by param
* POST and DELETE request for collection-module apis (CollectingEventAPI, MaterialSampleAPI) 
* DELETE request for collection-module apis (CollectingEventAPI, MaterialSampleAPI) 
* GET entity by param, or field, as part of collection-module API.

* utils.py includes method "get_dina_records_by_field" which allows user to retrieve all records matching a certain criteria using [rsql] filters.

## Examples

* GET entity by field (returns a list of material sample records):
    material_sample_list = get_dina_records_by_field(dina_material_sample_api,"group","aafc")
    first_record_id = list[0]["id]

* GET entity by param (returns a list of material sample records):
    params = {"filter[rsql]": "group"=="aafc", "sort": "-createdOn","page[limit]": step, "page[offset]": 300}
    material_sample_list = api.get_entity_by_param(params)
    first_record_id = list[0]["id]

* DELETE entity by id (removes an entity by id):
	dina_material_sample_api.remove_entity("uuid_string")

## Todo

* Develop models in order to have an object returned rather than a dict for the request return types.
* A way to re-use tokens when making different API calls.
* Implement and test the other request types for Person.
* Add support for other Dina entities.

## Tests
* Unit tests implemented for PersonSchema, MaterialSampleSchema, CollectingEventSchema
* API tests are currently done manually with a running local instance of DINA and still have to be converted to unittests

