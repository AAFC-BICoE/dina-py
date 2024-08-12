"""Defines basic Sequence Module API calls"""
from dinapy.dinaapi import DinaAPI

class SeqDBApi(DinaAPI):

	def __init__(self, config_path: str = None, base_url: str = None) -> None:
		super().__init__(config_path, base_url)
		self.base_url += "seqdb-api/"

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
	
	def remove_entity(self, entity_id):
		entity_id = str(entity_id) if isinstance(entity_id, int) else entity_id
		new_request_url = self.base_url + '/' + str(entity_id)
		jsn_resp = self.delete_req_dina(new_request_url)
		return jsn_resp if jsn_resp else ''

	def create_entity(self, json_data):
		"""Creates a DINA collection module entity

		Args:
			json_data (json object): the request body

		Returns:
			Response: The response post request
		"""
		return self.post_req_dina(self.base_url, json_data)

		
	def get_entity_with_param(self, entity_id,param):
		entity_id = str(entity_id) if isinstance(entity_id, int) else entity_id
		new_request_url = self.base_url + '/' + entity_id
		jsn_resp = self.get_req_dina(new_request_url, param)
		return jsn_resp if jsn_resp else '' 
	
	def get_entity_by_param(self, param = None):
		jsn_resp = self.get_req_dina(self.base_url, param)
		return jsn_resp if jsn_resp else ''
		
	def get_entity_by_field(self, field = None, value = None):
		"""Get an entity by it's name

		Args:
			value (string): value of the entity

		Returns:
			json response: a list of found entities with that value for that field
		"""
		if (field and value):
			new_params = {'filter[rsql]': "{}=='{}'".format(field, value)}
			return self.get_entity_by_param(new_params)
		
		return self.get_entity_by_param(None)


	def get_entity_by_fields(self, fields):
		"""Get an entity by it's name

		Args:
		value (string): value of the entity

		Returns:
		json response: a list of found entities with that value for that field
		"""
		filter_value = ''
		for k in fields:
			filter_value += f'{k}=={fields[k]};'
		new_params = {'filter[rsql]': filter_value[0:-1]}
		return self.get_entity_by_param(new_params)
