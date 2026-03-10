from .collectionapi import CollectionModuleApi
from dinapy.schemas.materialsampleschema import MaterialSampleSchema
from typing import List, Optional
import logging

class MaterialSampleAPI(CollectionModuleApi):
	"""
	Class for handling object store uploading related DINA API requests.
	"""

	def __init__(self, base_url: str = None) -> None:
		"""
		Parameters:
			base_url (str, optional): URL to the URL to perform the API requests against. If not
				provided then local deployment URL is used. Should end with a forward slash.
		"""
		super().__init__( base_url)
		self.base_url += "material-sample"

	def get_relationship_entity(self, entity_id, endpoint):
		entity_id = str(entity_id) if isinstance(entity_id, int) else entity_id
		new_request_url = self.base_url + '/'+ str(entity_id) + f'/relationships/{endpoint}'
		jsn_resp = self.get_req_dina(request_url = new_request_url)
		return jsn_resp if jsn_resp else ''

	def get_entity_attachments(self, entity_id):
		return self.get_relationship_entity(entity_id, 'attachment')

	def get_entity_collecting_event(self, entity_id):
		return self.get_relationship_entity(entity_id, 'collectingEvent')

	def get_entity_collection(self, entity_id):
		return self.get_relationship_entity(entity_id, 'collection')

	def bulk_update(self, json_data: dict) -> dict:
		"""Updates material-sample records providing a bulk payload using a PATCH request.

		Parameters:
			json_data (dict): JSON data for updating the material-sample.

		Returns:
			response_data: json content of the response
		"""
		full_url = self.base_url

		try:
			response_data = self.bulk_update_req_dina(full_url, json_data)
		except Exception as exc:
			logging.error(f"Failed to perform bulk update: {exc}")
			raise  # Re-raise the exception

		return response_data.json()

	def get_by_collection(
		self, 
		collection_uuid: str, 
		include: Optional[List[str]] = None,
		page_limit: int = 1000,
		page_offset: int = 0
	) -> dict:
		"""
		Get all material samples in a collection with related entities (for ENA workflow).
		
		This method queries material samples by collection UUID and optionally includes
		related entities like collectingEvent, organism, attachment, etc.

		Parameters:
			collection_uuid (str): UUID of the collection to filter by
			include (list, optional): List of relationships to include. 
				Common values: ['collectingEvent', 'organism', 'attachment', 'collection', 'preparationType']
				If None, defaults to ['collectingEvent', 'organism', 'attachment', 'collection']
			page_limit (int): Number of results per page (default: 1000)
			page_offset (int): Starting offset for pagination (default: 0)

		Returns:
			dict: JSON response containing material samples and included relationships

		Example:
			>>> api = MaterialSampleAPI()
			>>> # Get samples with all related data for ENA submission
			>>> result = api.get_by_collection(
			...     collection_uuid="01975b31-cb4b-7865-95e0-9ae7a47c8d68",
			...     include=['collectingEvent', 'organism', 'attachment', 'collection']
			... )
			>>> 
			>>> # Access the material samples
			>>> samples = result.get('data', [])
			>>> # Access included relationships
			>>> included = result.get('included', [])
		"""
		# Default includes for ENA workflow
		if include is None:
			include = ['collectingEvent', 'organism', 'attachment', 'collection']
		
		# Build the query parameters
		params = {
			'filter[collection.uuid]': collection_uuid,
			'page[limit]': page_limit,
			'page[offset]': page_offset
		}
		
		# Add include parameter as comma-separated string
		if include:
			params['include'] = ','.join(include)
		
		# Use the parent class method to make the request
		return self.get_entity_by_param(params)
	
	def extract_sample_ids(self, api_response: dict) -> List[str]:
		"""
		Extract material sample IDs from API response.
		
		Helper method to extract just the IDs from the response, useful when you need
		to process samples individually.

		Parameters:
			api_response (dict): The JSON response from get_by_collection or similar methods

		Returns:
			list: List of material sample UUIDs

		Example:
			>>> result = api.get_by_collection("01975b31-cb4b-7865-95e0-9ae7a47c8d68")
			>>> sample_ids = api.extract_sample_ids(result)
			>>> print(sample_ids)
			['uuid1', 'uuid2', 'uuid3', ...]
		"""
		print(api_response)
		data = api_response.get('data', [])
		return [sample['id'] for sample in data if 'id' in sample]