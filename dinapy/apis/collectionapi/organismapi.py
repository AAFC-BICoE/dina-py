"""Class that extracts common functionality for collecting event entity"""
import json
from .collectionapi import CollectionModuleApi

class OrganismAPI(CollectionModuleApi):

	def __init__(self, config_path: str = None, base_url: str = None) -> None:
		"""
		Parameters:
			config_path (str, optional): Path to a config file (default: None).
			base_url (str, optional): URL to the URL to perform the API requests against. If not
				provided then local deployment URL is used. Should end with a forward slash.
		"""
		super().__init__(config_path, base_url)
		self.base_url += "organism"
	
