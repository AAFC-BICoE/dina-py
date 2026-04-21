"""Class that extracts common functionality for collecting event entity"""

from .collectionapi import CollectionModuleApi
import logging

class CollectingEventAPI(CollectionModuleApi):

	def __init__(self, base_url: str = None) -> None:
		super().__init__( base_url)
		self.base_url += "collecting-event"

	def get_entities(self, include_params=None, filter_params=None):
		"""Retrieves entities

		Args:
			include_params (string, optional): comma-separated list of relationship endpoints to include in the response
			filter_params (dict, optional): dictionary of filters to apply to the request of format filter_tupe

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