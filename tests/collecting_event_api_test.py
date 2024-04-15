from time import sleep
import json

import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.apis.collectionapi.collectingeventapi import CollectingEventAPI
from dinapy.entities.CollectingEvent import CollectingEventDTOBuilder,CollectingEventAttributesDTOBuilder
from dinapy.schemas.collectingeventschema import CollectingEventSchema
from dinapy.utils import get_dina_records_by_field

#TODO: Convert this into proper unit test.
os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

def main():
	dina_collecting_event_api = CollectingEventAPI()
	collecting_event_attributes = CollectingEventAttributesDTOBuilder().group("aafc").build()
	collecting_event = CollectingEventDTOBuilder().attributes(collecting_event_attributes).build()
	collecting_event_schema = CollectingEventSchema()

	
	serialized_collecting_event = collecting_event_schema.dump(collecting_event)
	
	#response = dina_collecting_event_api.get_entity("cce513a7-0797-4d6e-ae88-34043e552434")
	list = get_dina_records_by_field(dina_collecting_event_api,"group","aafc")

	print(list)
	#print(response.status_code)

	# deserialized_collecting_event = collecting_event_schema.load(response.json())

	# print(deserialized_collecting_event)

if __name__ == '__main__':
	main()