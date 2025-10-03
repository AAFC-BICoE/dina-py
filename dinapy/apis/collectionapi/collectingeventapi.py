"""Class that extracts common functionality for collecting event entity"""

from .collectionapi import CollectionModuleApi
from dinapy.schemas.collectingeventschema import CollectingEventSchema
import logging

class CollectingEventAPI(CollectionModuleApi):

	def __init__(self, config_path: str = None, base_url: str = None) -> None:
		super().__init__(config_path, base_url)
		self.base_url += "collecting-event"

	def bulk_update(self, json_data: dict):
		"""Updates collecting-event records providing a bulk payload using a PATCH request.

		Parameters:
			json_data (dict): JSON data for updating the collecting-event.

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