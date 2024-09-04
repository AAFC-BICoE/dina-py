# This file contains the FormTemplateAPI class used for interacting with the Form Template endpoint of the Collection API.
from .collectionapi import CollectionModuleApi

class FormTemplateAPI(CollectionModuleApi):
	"""
	Class for handling form template related DINA API requests.
	"""

	def __init__(self, config_path: str = None, base_url: str = None) -> None:
		"""
		Parameters:
			config_path (str, optional): Path to a config file (default: None).
			base_url (str, optional): URL to the URL to perform the API requests against. If not
				provided then local deployment URL is used. Should end with a forward slash.
		"""
		super().__init__(config_path, base_url)
		self.base_url += "form-template"

	