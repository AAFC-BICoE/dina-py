"""Class that extracts common functionality for collecting event entity"""

from .collectionapi import CollectionModuleApi

class CollectingEventAPI(CollectionModuleApi):

	def __init__(self, config_path: str = None, base_url: str = None) -> None:
		super().__init__(config_path, base_url)
		self.base_url += "collecting-event"

		