import unittest
from unittest.mock import patch, MagicMock, Mock
import os
import sys

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.apis.collectionapi.materialsampleapi import MaterialSampleAPI
from dinapy.apis.collectionapi.collectionapi import CollectionModuleApi
from dinapy.schemas.material_sample_pydantic import MaterialSampleDocument, MaterialSampleData, MaterialSampleAttributes
from .mock_responses import *

# Environment variables for testing
TEST_ENV_VARS = {
	'KEYCLOAK_USERNAME': 'test_user',
	'KEYCLOAK_PASSWORD': 'test_password',
	'KEYCLOAK_URL': 'http://test.dina.local',
	'CLIENT_ID': 'test_client',
	'REALM_NAME': 'test_realm',
	'SECURE': 'false'
}

class TestMaterialSampleAPI(unittest.TestCase):

	@patch('dinapy.apis.collectionapi.collectionapi.CollectionModuleApi')
	def test_update_material_sample(self,MockCollectionModuleApi):

		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.json.return_value = MOCK_MATERIAL_SAMPLE
		MockCollectionModuleApi.return_value.update_entity.return_value = mock_response

		collection_module_api = MockCollectionModuleApi.return_value

		serialized_material_sample = MaterialSampleDocument(
			data=MaterialSampleData(
				type="material-sample",
				attributes=MaterialSampleAttributes(group="aafc", createdBy="dina-admin"),
			)
		).serialize()

		response = collection_module_api.update_entity(id, serialized_material_sample)

		self.assertEqual(response.status_code, 200)
		deserialized_material_sample = MaterialSampleDocument.deserialize(response.json())
		self.assertEqual(deserialized_material_sample.data.id, "019137c0-2027-7bcf-ac92-3844dd80466e")
		self.assertEqual(deserialized_material_sample.data.attributes.group, "aafc")
		self.assertEqual(deserialized_material_sample.data.attributes.createdBy, "dina-admin")
	@patch('dinapy.dinaapi.DinaAPI.set_keycloak')
	@patch('dinapy.dinaapi.DinaAPI._check_env_vars', return_value=True)
	@patch.dict(os.environ, TEST_ENV_VARS, clear=False)
	@patch.object(MaterialSampleAPI, 'get_entity_by_param')
	def test_get_by_collection(self, mock_get_entity_by_param, mock_check_env, mock_set_keycloak):
		"""Test getting material samples by collection UUID"""
		
		# Setup mocks to prevent actual authentication
		mock_set_keycloak.return_value = None
		
		# Mock response
		mock_response = {
			'data': [
				{
					'id': 'sample-uuid-1',
					'type': 'material-sample',
					'attributes': {
						'materialSampleName': 'Sample 1',
						'group': 'aafc'
					},
					'relationships': {
						'collectingEvent': {'data': {'id': 'ce-uuid-1', 'type': 'collecting-event'}},
						'organism': {'data': [{'id': 'org-uuid-1', 'type': 'organism'}]},
						'collection': {'data': {'id': 'coll-uuid-1', 'type': 'collection'}}
					}
				},
				{
					'id': 'sample-uuid-2',
					'type': 'material-sample',
					'attributes': {
						'materialSampleName': 'Sample 2',
						'group': 'aafc'
					}
				}
			],
			'included': [
				{
					'id': 'ce-uuid-1',
					'type': 'collecting-event',
					'attributes': {'dwcVerbatimLocality': 'Test Location'}
				},
				{
					'id': 'org-uuid-1',
					'type': 'organism',
					'attributes': {'determination': []}
				},
				{
					'id': 'coll-uuid-1',
					'type': 'collection',
					'attributes': {'name': 'Test Collection'}
				}
			]
		}
		
		mock_get_entity_by_param.return_value = mock_response
		
		# Test the method
		api = MaterialSampleAPI()
		collection_uuid = '01975b31-cb4b-7865-95e0-9ae7a47c8d68'
		
		result = api.get_by_collection(
			collection_uuid=collection_uuid,
			include=['collectingEvent', 'organism', 'attachment', 'collection']
		)
		
		# Verify the method was called with correct parameters
		mock_get_entity_by_param.assert_called_once()
		call_args = mock_get_entity_by_param.call_args[0][0]
		
		self.assertEqual(call_args['filter[collection.uuid]'], collection_uuid)
		self.assertEqual(call_args['include'], 'collectingEvent,organism,attachment,collection')
		self.assertEqual(call_args['page[limit]'], 1000)
		self.assertEqual(call_args['page[offset]'], 0)
		
		# Verify response
		self.assertEqual(len(result['data']), 2)
		self.assertEqual(len(result['included']), 3)
		self.assertEqual(result['data'][0]['id'], 'sample-uuid-1')
		self.assertEqual(result['data'][0]['attributes']['materialSampleName'], 'Sample 1')

	@patch('dinapy.dinaapi.DinaAPI.set_keycloak')
	@patch('dinapy.dinaapi.DinaAPI._check_env_vars', return_value=True)
	@patch.dict(os.environ, TEST_ENV_VARS, clear=False)
	def test_extract_sample_ids(self, mock_check_env, mock_set_keycloak):
		"""Test extracting sample IDs from API response"""
		
		mock_set_keycloak.return_value = None
		api = MaterialSampleAPI()
		
		# Test response
		api_response = {
			'data': [
				{'id': 'sample-uuid-1', 'type': 'material-sample'},
				{'id': 'sample-uuid-2', 'type': 'material-sample'},
				{'id': 'sample-uuid-3', 'type': 'material-sample'}
			]
		}
		
		sample_ids = api.extract_sample_ids(api_response)
		
		self.assertEqual(len(sample_ids), 3)
		self.assertIn('sample-uuid-1', sample_ids)
		self.assertIn('sample-uuid-2', sample_ids)
		self.assertIn('sample-uuid-3', sample_ids)
		
		# Test empty response
		empty_response = {'data': []}
		empty_ids = api.extract_sample_ids(empty_response)
		self.assertEqual(len(empty_ids), 0)
		
		# Test response with missing IDs
		partial_response = {
			'data': [
				{'id': 'sample-uuid-1', 'type': 'material-sample'},
				{'type': 'material-sample'},  # Missing id
				{'id': 'sample-uuid-3', 'type': 'material-sample'}
			]
		}
		partial_ids = api.extract_sample_ids(partial_response)
		self.assertEqual(len(partial_ids), 2)

	@patch('dinapy.dinaapi.DinaAPI.set_keycloak')
	@patch('dinapy.dinaapi.DinaAPI._check_env_vars', return_value=True)
	@patch.dict(os.environ, TEST_ENV_VARS, clear=False)
	@patch.object(MaterialSampleAPI, 'get_entity_by_param')
	def test_get_by_collection_with_defaults(self, mock_get_entity_by_param, mock_check_env, mock_set_keycloak):
		"""Test get_by_collection uses default includes when none specified"""
		
		mock_set_keycloak.return_value = None
		mock_get_entity_by_param.return_value = {'data': [], 'included': []}
		
		api = MaterialSampleAPI()
		collection_uuid = '01975b31-cb4b-7865-95e0-9ae7a47c8d68'
		
		# Call without specifying includes
		api.get_by_collection(collection_uuid=collection_uuid)
		
		# Verify default includes are used
		call_args = mock_get_entity_by_param.call_args[0][0]
		self.assertEqual(
			call_args['include'], 
			'collectingEvent,organism,attachment,collection'
		)

	@patch('dinapy.dinaapi.DinaAPI.set_keycloak')
	@patch('dinapy.dinaapi.DinaAPI._check_env_vars', return_value=True)
	@patch.dict(os.environ, TEST_ENV_VARS, clear=False)
	@patch.object(MaterialSampleAPI, 'get_entity_by_param')
	def test_get_by_collection_pagination(self, mock_get_entity_by_param, mock_check_env, mock_set_keycloak):
		"""Test get_by_collection with custom pagination"""
		
		mock_set_keycloak.return_value = None
		mock_get_entity_by_param.return_value = {'data': [], 'included': []}
		
		api = MaterialSampleAPI()
		collection_uuid = '01975b31-cb4b-7865-95e0-9ae7a47c8d68'
		
		# Call with custom pagination
		api.get_by_collection(
			collection_uuid=collection_uuid,
			page_limit=50,
			page_offset=100
		)
		
		# Verify pagination parameters
		call_args = mock_get_entity_by_param.call_args[0][0]
		self.assertEqual(call_args['page[limit]'], 50)
		self.assertEqual(call_args['page[offset]'], 100)

	@patch('dinapy.dinaapi.DinaAPI.set_keycloak')
	@patch('dinapy.dinaapi.DinaAPI._check_env_vars', return_value=True)
	@patch.dict(os.environ, TEST_ENV_VARS, clear=False)
	@patch.object(MaterialSampleAPI, 'get_entity_by_param')
	def test_get_by_collection(self, mock_get_entity_by_param, mock_check_env, mock_set_keycloak):
		"""Test getting material samples by collection UUID"""
		
		# Setup mocks to prevent actual authentication
		mock_set_keycloak.return_value = None
		
		# Mock response
		mock_response = {
			'data': [
				{
					'id': 'sample-uuid-1',
					'type': 'material-sample',
					'attributes': {
						'materialSampleName': 'Sample 1',
						'group': 'aafc'
					},
					'relationships': {
						'collectingEvent': {'data': {'id': 'ce-uuid-1', 'type': 'collecting-event'}},
						'organism': {'data': [{'id': 'org-uuid-1', 'type': 'organism'}]},
						'collection': {'data': {'id': 'coll-uuid-1', 'type': 'collection'}}
					}
				},
				{
					'id': 'sample-uuid-2',
					'type': 'material-sample',
					'attributes': {
						'materialSampleName': 'Sample 2',
						'group': 'aafc'
					}
				}
			],
			'included': [
				{
					'id': 'ce-uuid-1',
					'type': 'collecting-event',
					'attributes': {'dwcVerbatimLocality': 'Test Location'}
				},
				{
					'id': 'org-uuid-1',
					'type': 'organism',
					'attributes': {'determination': []}
				},
				{
					'id': 'coll-uuid-1',
					'type': 'collection',
					'attributes': {'name': 'Test Collection'}
				}
			]
		}
		
		mock_get_entity_by_param.return_value = mock_response
		
		# Test the method
		api = MaterialSampleAPI()
		collection_uuid = '01975b31-cb4b-7865-95e0-9ae7a47c8d68'
		
		result = api.get_by_collection(
			collection_uuid=collection_uuid,
			include=['collectingEvent', 'organism', 'attachment', 'collection']
		)
		
		# Verify the method was called with correct parameters
		mock_get_entity_by_param.assert_called_once()
		call_args = mock_get_entity_by_param.call_args[0][0]
		
		self.assertEqual(call_args['filter[collection.uuid]'], collection_uuid)
		self.assertEqual(call_args['include'], 'collectingEvent,organism,attachment,collection')
		self.assertEqual(call_args['page[limit]'], 1000)
		self.assertEqual(call_args['page[offset]'], 0)
		
		# Verify response
		self.assertEqual(len(result['data']), 2)
		self.assertEqual(len(result['included']), 3)
		self.assertEqual(result['data'][0]['id'], 'sample-uuid-1')
		self.assertEqual(result['data'][0]['attributes']['materialSampleName'], 'Sample 1')

	@patch('dinapy.dinaapi.DinaAPI.set_keycloak')
	@patch('dinapy.dinaapi.DinaAPI._check_env_vars', return_value=True)
	@patch.dict(os.environ, TEST_ENV_VARS, clear=False)
	def test_extract_sample_ids(self, mock_check_env, mock_set_keycloak):
		"""Test extracting sample IDs from API response"""
		
		mock_set_keycloak.return_value = None
		api = MaterialSampleAPI()
		
		# Test response
		api_response = {
			'data': [
				{'id': 'sample-uuid-1', 'type': 'material-sample'},
				{'id': 'sample-uuid-2', 'type': 'material-sample'},
				{'id': 'sample-uuid-3', 'type': 'material-sample'}
			]
		}
		
		sample_ids = api.extract_sample_ids(api_response)
		
		self.assertEqual(len(sample_ids), 3)
		self.assertIn('sample-uuid-1', sample_ids)
		self.assertIn('sample-uuid-2', sample_ids)
		self.assertIn('sample-uuid-3', sample_ids)
		
		# Test empty response
		empty_response = {'data': []}
		empty_ids = api.extract_sample_ids(empty_response)
		self.assertEqual(len(empty_ids), 0)
		
		# Test response with missing IDs
		partial_response = {
			'data': [
				{'id': 'sample-uuid-1', 'type': 'material-sample'},
				{'type': 'material-sample'},  # Missing id
				{'id': 'sample-uuid-3', 'type': 'material-sample'}
			]
		}
		partial_ids = api.extract_sample_ids(partial_response)
		self.assertEqual(len(partial_ids), 2)

	@patch('dinapy.dinaapi.DinaAPI.set_keycloak')
	@patch('dinapy.dinaapi.DinaAPI._check_env_vars', return_value=True)
	@patch.dict(os.environ, TEST_ENV_VARS, clear=False)
	@patch.object(MaterialSampleAPI, 'get_entity_by_param')
	def test_get_by_collection_with_defaults(self, mock_get_entity_by_param, mock_check_env, mock_set_keycloak):
		"""Test get_by_collection uses default includes when none specified"""
		
		mock_set_keycloak.return_value = None
		mock_get_entity_by_param.return_value = {'data': [], 'included': []}
		
		api = MaterialSampleAPI()
		collection_uuid = '01975b31-cb4b-7865-95e0-9ae7a47c8d68'
		
		# Call without specifying includes
		api.get_by_collection(collection_uuid=collection_uuid)
		
		# Verify default includes are used
		call_args = mock_get_entity_by_param.call_args[0][0]
		self.assertEqual(
			call_args['include'], 
			'collectingEvent,organism,attachment,collection'
		)

	@patch('dinapy.dinaapi.DinaAPI.set_keycloak')
	@patch('dinapy.dinaapi.DinaAPI._check_env_vars', return_value=True)
	@patch.dict(os.environ, TEST_ENV_VARS, clear=False)
	@patch.object(MaterialSampleAPI, 'get_entity_by_param')
	def test_get_by_collection_pagination(self, mock_get_entity_by_param, mock_check_env, mock_set_keycloak):
		"""Test get_by_collection with custom pagination"""
		
		mock_set_keycloak.return_value = None
		mock_get_entity_by_param.return_value = {'data': [], 'included': []}
		
		api = MaterialSampleAPI()
		collection_uuid = '01975b31-cb4b-7865-95e0-9ae7a47c8d68'
		
		# Call with custom pagination
		api.get_by_collection(
			collection_uuid=collection_uuid,
			page_limit=50,
			page_offset=100
		)
		
		# Verify pagination parameters
		call_args = mock_get_entity_by_param.call_args[0][0]
		self.assertEqual(call_args['page[limit]'], 50)
		self.assertEqual(call_args['page[offset]'], 100)

if __name__ == '__main__':
	unittest.main()