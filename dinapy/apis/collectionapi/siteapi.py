"""Defines basic Collection Module API calls"""
from .collectionapi import CollectionModuleApi

class SiteApi(CollectionModuleApi):

	def __init__(self, base_url: str = None) -> None:
		super().__init__(base_url)
		self.base_url += "site"

        