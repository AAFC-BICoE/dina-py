from time import sleep
import json

import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.apis.collectionapi.collectingeventapi import CollectingEvent
from dinapy.entities.CollectingEvent import CollectingEventDTOBuilder,CollectingEventAttributesDTOBuilder
from dinapy.schemas.collectingeventschema import CollectingEventSchema

#TODO: Convert this into proper unit test.

def main():
	dina_collecting_event_api = CollectingEvent()
	collecting_event_attributes = CollectingEventAttributesDTOBuilder().set_group("aafc").build()
	collecting_event = CollectingEventDTOBuilder().set_attributes(collecting_event_attributes).build()
	collecting_event_schema = CollectingEventSchema()
	
	serialized_collecting_event = collecting_event_schema.dump(collecting_event)
	
	response = dina_collecting_event_api.create_entity(serialized_collecting_event)
	
	print(response.json())

	deserialized_collecting_event = collecting_event_schema.load(response.json())

	print(deserialized_collecting_event)

if __name__ == '__main__':
	main()