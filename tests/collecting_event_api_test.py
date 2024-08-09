import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.apis.collectionapi.collectingeventapi import CollectingEventAPI
from dinapy.entities.CollectingEvent import CollectingEventDTOBuilder, CollectingEventAttributesDTOBuilder
from dinapy.schemas.collectingeventschema import CollectingEventSchema
from mock_responses import *

class TestCollectingEventAPI(unittest.TestCase):

	@patch('dinapy.apis.collectionapi.collectingeventapi.CollectingEventAPI.update_entity')
	def test_update_collecting_event(self, mock_update_entity):

		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.json.return_value = MOCK_VALID_COLLECTING_EVENT_DATA
		
		mock_update_entity.return_value = mock_response

		dina_collecting_event_api = CollectingEventAPI()
		collecting_event_attributes = CollectingEventAttributesDTOBuilder().group("aafc").build()
		collecting_event = CollectingEventDTOBuilder().attributes(collecting_event_attributes).build()
		collecting_event_schema = CollectingEventSchema()

		# Serialize the collecting event
		serialized_collecting_event = collecting_event_schema.dump(collecting_event)

		# Update the entity
		response = dina_collecting_event_api.update_entity(id, serialized_collecting_event)

		# Assertions
		self.assertEqual(response.status_code, 200)
		deserialized_collecting_event = collecting_event_schema.load(response.json())
		self.assertEqual(deserialized_collecting_event.id, "f08516e5-add2-4baa-89bc-5b8abd0ec8ba")
		self.assertEqual(deserialized_collecting_event.attributes["group"], "phillips-lab")

if __name__ == '__main__':
	unittest.main()
