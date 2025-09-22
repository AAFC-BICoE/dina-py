from .collectionapi import CollectionModuleApi
from dinapy.schemas.materialsampleschema import MaterialSampleSchema
import logging

class MaterialSampleAPI(CollectionModuleApi):
	"""
	Class for handling object store uploading related DINA API requests.
	"""

	def __init__(self, config_path: str = None, base_url: str = None) -> None:
		"""
		Parameters:
			config_path (str, optional): Path to a config file (default: None).
			base_url (str, optional): URL to the URL to perform the API requests against. If not
				provided then local deployment URL is used. Should end with a forward slash.
		"""
		super().__init__(config_path, base_url)
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
		"""Updates person records providing a bulk payload using a PATCH request.

		Parameters:
			json_data (dict): JSON data for updating the person.

		Returns:
			dict: A deserialized object of the PATCH response.
		"""
		full_url = self.base_url

		try:
			response_data = self.bulk_update_req_dina(full_url, json_data)
		except Exception as exc:
			logging.error(f"Failed to perform bulk update: {exc}")
			raise  # Re-raise the exception

		material_sample_schema = MaterialSampleSchema()
		deserialized_data = material_sample_schema.load(response_data.json())

		return deserialized_data