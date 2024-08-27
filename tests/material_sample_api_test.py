import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.apis.collectionapi.materialsampleapi import MaterialSampleAPI
from dinapy.apis.collectionapi.collectionapi import CollectionModuleApi

from dinapy.entities.MaterialSample import MaterialSampleAttributesDTOBuilder, MaterialSampleDTOBuilder
from dinapy.schemas.materialsampleschema import MaterialSampleSchema
from mock_responses import *

class TestMaterialSampleAPI(unittest.TestCase):

	@patch('dinapy.apis.collectionapi.collectionapi.CollectionModuleApi')
	def test_update_material_sample(self,MockCollectionModuleApi):

		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.json.return_value = MOCK_MATERIAL_SAMPLE
		MockCollectionModuleApi.return_value.update_entity.return_value = mock_response

		collection_module_api = MockCollectionModuleApi.return_value
		material_sample_schema = MaterialSampleSchema()

		material_sample_attributes = MaterialSampleAttributesDTOBuilder().group("aafc").createdBy("dina-admin").build()
		material_sample = MaterialSampleDTOBuilder().id(id).attributes(material_sample_attributes).build()
		serialized_material_sample = material_sample_schema.dump(material_sample)

		response = collection_module_api.update_entity(id, serialized_material_sample)

		self.assertEqual(response.status_code, 200)
		deserialized_material_sample = material_sample_schema.load(response.json())
		self.assertEqual(deserialized_material_sample.id, "019137c0-2027-7bcf-ac92-3844dd80466e")
		self.assertEqual(deserialized_material_sample.attributes['group'], "aafc")
		self.assertEqual(deserialized_material_sample.attributes['createdBy'], "dina-admin")

if __name__ == '__main__':
	unittest.main()