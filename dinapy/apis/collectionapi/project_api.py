"""Class that extracts common functionality for Project entity"""

from .collectionapi import CollectionModuleApi

class ProjectAPI(CollectionModuleApi):

	def __init__(self, base_url: str = None) -> None:
		super().__init__( base_url)
		self.base_url += "collecting-event"
