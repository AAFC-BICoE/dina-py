import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.apis.collectionapi.collectingeventapi import CollectingEventAPI
from dinapy.apis.collectionapi.collectionapi import CollectionModuleApi
from dinapy.schemas.collecting_event_pydantic import CollectingEventDocument, CollectingEventData, CollectingEventAttributes
from .mock_responses import *

class TestCollectingEventAPI(unittest.TestCase):

	@patch('dinapy.apis.collectionapi.collectionapi.CollectionModuleApi')
	def test_update_collecting_event(self, MockCollectionModuleApi):

		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.json.return_value = MOCK_VALID_COLLECTING_EVENT_DATA
		MockCollectionModuleApi.return_value.update_entity.return_value = mock_response

		dina_collecting_event_api = MockCollectionModuleApi.return_value

		serialized_collecting_event = CollectingEventDocument(
			data=CollectingEventData(
				type="collecting-event",
				attributes=CollectingEventAttributes(group="aafc"),
			)
		).serialize()

		# Update the entity
		response = dina_collecting_event_api.update_entity(id, serialized_collecting_event)

		# Assertions
		self.assertEqual(response.status_code, 200)
		deserialized_collecting_event = CollectingEventDocument.deserialize(response.json())
		self.assertEqual(deserialized_collecting_event.data.id, "f08516e5-add2-4baa-89bc-5b8abd0ec8ba")
		self.assertEqual(deserialized_collecting_event.data.attributes.group, "phillips-lab")

if __name__ == '__main__':
	unittest.main()
