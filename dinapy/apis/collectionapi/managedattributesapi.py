"""Class that extracts common functionality for collecting event entity"""
import json
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
	
	def get_entities(self, json_data):
		"""Creates a DINA managed attribute entity

		Args:
				json_data (json object): the request body

		Returns:
				Response: The response post request
		"""
		return self.get_entity_by_param(self.base_url, json_data)
	
	def update_entity(self, json_data):
		return self.patch_req_dina(self.base_url+"/"+f'{json_data["data"]["id"]}', json.dumps(json_data))