from .collectionapi import CollectionModuleApi
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

	def get_by_collection(
		self,
		collection_uuid: str,
		include: Optional[List[str]] = None,
		page_limit: int = 1000,
		page_offset: int = 0,
	):
		"""Retrieve all material samples belonging to a collection.

		Args:
			collection_uuid: UUID of the collection to filter by.
			include: List of relationship names to include (default: collectingEvent,
				organism, attachment, collection).
			page_limit: Maximum number of records per page.
			page_offset: Offset for pagination.

		Returns:
			Raw API response dict with ``data`` and ``included`` keys.
		"""
		default_include = ["collectingEvent", "organism", "attachment", "collection"]
		params = {
			"filter[collection.uuid]": collection_uuid,
			"include": ",".join(include if include is not None else default_include),
			"page[limit]": page_limit,
			"page[offset]": page_offset,
		}
		return self.get_entity_by_param(params)

	@staticmethod
	def extract_sample_ids(api_response: dict) -> List[str]:
		"""Extract sample UUIDs from a list API response.

		Args:
			api_response: Raw response dict with a ``data`` list.

		Returns:
			List of UUIDs for records that have an ``id`` field.
		"""
		return [item["id"] for item in api_response.get("data", []) if item.get("id")]

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