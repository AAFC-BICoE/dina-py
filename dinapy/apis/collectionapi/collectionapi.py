"""Defines basic Collection Module API calls"""
from dinapy.dinaapi import DinaAPI

class CollectionModuleApi(DinaAPI):

	def __init__(self, base_url: str = None) -> None:
		super().__init__(base_url)
		self.base_url += "collection-api/"

	def get_entity(self, entity_id):
		"""Retrieves an entity

		Args:
			entity_id (string): entity id

		Returns:
			json response: 'result' from the json response OR nothing if entity was not found
		"""
		entity_id = str(entity_id) if isinstance(entity_id, int) else entity_id
		new_request_url = self.base_url + '/' + str(entity_id)
		jsn_resp = self.get_req_dina(new_request_url)
		return jsn_resp if jsn_resp else ''

	def create_entity(self, json_data):
		"""Creates a DINA collection module entity

		Args:
			json_data (json object): the request body

		Returns:
			Response: The response post request
		"""
		return self.post_req_dina(self.base_url, json_data)

	def create_bulk(self, json_data):
		"""Creates a DINA collection module entity as bulk

		Args:
			json_data (json object): the request body with bulk data

		Returns:
			Response: The response post request
		"""
		new_request_url = self.base_url + '/bulk/'
		return self.post_req_dina(new_request_url, json_data)

	def get_entity_by_param(self, param):
		jsn_resp = self.get_req_dina(self.base_url, param)
		return jsn_resp if jsn_resp else ''

	def get_entity_by_field(self, field, value):
		"""Get an entity by it's name

		Args:
			value (string): value of the entity

		Returns:
			json response: a list of found entities with that value for that field
		"""
		new_params = {f"filter[{field}][EQ]": value}
		return self.get_entity_by_param(new_params)

	def remove_entity(self, entity_id):
		entity_id = str(entity_id) if isinstance(entity_id, int) else entity_id
		new_request_url = self.base_url + '/' + str(entity_id)
		jsn_resp = self.delete_req_dina(new_request_url)
		return jsn_resp if jsn_resp else ''
	
	def get_entities(self, include_params=None, filter_params=None):
		"""Retrieves entities

		Args:
			include_params (string, optional): comma-separated list of relationship endpoints to include in the response
			filter_params (dict, optional): dictionary of filters to apply to the request of format filter_type[OPERATOR]: value

		Returns:
			json response: 'result' from the json response OR nothing if no entities were found
		"""
		new_request_url = self.base_url
		params = {}
		if include_params:
			params["include"] = include_params
		for key, value in (filter_params or {}).items():
			params[key] = value

		jsn_resp = self.get_req_dina(new_request_url, params=params)
		return jsn_resp if jsn_resp else ''
	
	def update_entity(self, entity_id, json_data):

		"""Updates an entity

		Args:
			entity_id (string): entity id

		Returns:
			json response: 'result' from the json response OR nothing if entity was not found
		"""

		entity_id = str(entity_id) if isinstance(entity_id, int) else entity_id
		new_request_url = self.base_url + '/' + str(entity_id)
		jsn_resp = self.patch_req_dina(new_request_url,json_data)
		return jsn_resp if jsn_resp else ''