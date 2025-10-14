"""Class that extracts common functionality for collecting event entity"""
import json
import logging
from .collectionapi import CollectionModuleApi

class ManagedAttributeAPI(CollectionModuleApi):

	def __init__(self, config_path: str = None, base_url: str = None) -> None:
		"""
		Parameters:
			config_path (str, optional): Path to a config file (default: None).
			base_url (str, optional): URL to the URL to perform the API requests against. If not
				provided then local deployment URL is used. Should end with a forward slash.
		"""
		super().__init__(config_path, base_url)
		self.base_url += "managed-attribute"
	
	def create_entity(self, json_data):
		"""Creates a DINA managed attribute entity

		Args:
				json_data (json object): the request body

		Returns:
				Response: The response post request
		"""
		return self.post_req_dina(self.base_url, json_data)
	
	def get_entity_by_field(self, field, value):
		"""Retrieves a DINA managed attribute entity by it's field

		Args:
			value (string): value of the field eg: 'aafc'
			field (string): name of the field eg: 'name', 'group'

		Returns:
			json response: a list of found entities with that value for that field
		"""

		new_params = {f"filter[{field}][EQ]": value}
		
		return self.get_entity_by_param(new_params)
	
	def update_entity(self, json_data):
		return self.patch_req_dina(self.base_url+"/"+f'{json_data["data"]["id"]}', json.dumps(json_data))

	def bulk_update(self, json_data: dict) -> dict:
		"""Updates managed-attribute records providing a bulk payload using a PATCH request.

		Parameters:
			json_data (dict): JSON data for updating the managed-attribute.

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