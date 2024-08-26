import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.apis.collectionapi.splitconfigurationapi import SplitConfigurationAPI
from dinapy.entities.SplitConfiguration import SplitConfigurationDTOBuilder, SplitConfigurationAttributesDTOBuilder
from dinapy.schemas.splitconfigurationschema import SplitConfigurationSchema
from mock_responses import *

class TestSplitConfigurationAPI(unittest.TestCase):

	@patch('dinapy.apis.collectionapi.splitconfigurationapi.SplitConfigurationAPI.update_entity')
	def test_update_split_configuration(self, mock_update_entity):

		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.json.return_value = MOCK_SPLIT_CONFIGURATION
		
		mock_update_entity.return_value = mock_response

		dina_split_configuration_api = SplitConfigurationAPI()
		split_configuration_attributes = SplitConfigurationAttributesDTOBuilder().set_group("phillips-lab").build()
		split_configuration = SplitConfigurationDTOBuilder().set_attributes(split_configuration_attributes).build()
		split_configuration_schema = SplitConfigurationSchema()

		# Serialize the split configuration
		serialized_split_configuration = split_configuration_schema.dump(split_configuration)

		# Update the entity
		response = dina_split_configuration_api.update_entity(id, serialized_split_configuration)

		# Assertions
		self.assertEqual(response.status_code, 200)
		deserialized_split_configuration = split_configuration_schema.load(response.json())
		self.assertEqual(deserialized_split_configuration.id, "01918f0d-4261-770d-8fce-e240799cceb8")
		self.assertEqual(deserialized_split_configuration.attributes["group"], "aafc")

if __name__ == '__main__':
	unittest.main()
