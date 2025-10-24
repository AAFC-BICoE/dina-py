"""Class that extracts common functionality for collecting event entity"""
import json
from .collectionapi import CollectionModuleApi

class OrganismAPI(CollectionModuleApi):

	def __init__(self, base_url: str = None) -> None:
		"""
		Parameters:
			base_url (str, optional): URL to the URL to perform the API requests against. If not
				provided then local deployment URL is used. Should end with a forward slash.
		"""
		super().__init__( base_url)
		self.base_url += "organism"
	
