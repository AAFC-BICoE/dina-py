"""Class that extracts common functionality for collecting event entity"""

from .collectionapi import CollectionModuleApi

class CollectingEvent(CollectionModuleApi):

	def __init__(self, config_path: str = None, base_url: str = None) -> None:
		super().__init__(config_path, base_url)
		self.base_url += "collecting-event/"

	def map_specimen(self, json_resp):
		"""Map a specimen from SeqDB to dina's collecting event

		Args:
			json_resp (json response): the json response when getting a specimen

		Returns:
			json object: dina entity attributes filled by SeqDB fields
		"""
		dina_attributes = {}

		dina_attributes['managedAttributes'] = {'test_managed_attribute': str(json_resp.get('id'))}

		dina_attributes['dwcRecordNumber'] = json_resp.get('number')

		dwcOtherRecordNumbers = self.get_list_from_string(json_resp.get('otherIds'))

		dina_attributes['dwcOtherRecordNumbers'] = dwcOtherRecordNumbers

		return dina_attributes

	def map_collection_info(self, json_resp):
		"""Map a specimen's collectionInfo from SeqDB to dina's collecting event

		Args:
			json_resp (json response): the json reponse when getting a specimen's collectionInfo

		Returns:
			json object: dina entity attributes filled by SeqDB fields
		"""
		dina_attributes = {}

		dina_attributes['dwcCountry'] = json_resp.get('country')
		dina_attributes['dwcStateProvince'] = json_resp.get('province')
		dina_attributes['verbatimEventDateTime'] = self.format_date(json_resp.get('year'), json_resp.get('month'), json_resp.get('day'))
		dina_attributes['endEventDateTime'] = self.format_date(json_resp.get('endYear'), json_resp.get('endMonth'), json_resp.get('endDay'))
		dina_attributes['dwcVerbatimElevation'] = json_resp.get('elevation')
		dina_attributes['dwcVerbatimDepth'] = json_resp.get('depth')
		dina_attributes['dwcVerbatimLatitude'] = json_resp.get('latitude')
		dina_attributes['dwcVerbatimLongitude'] = json_resp.get('longitude')
		dina_attributes['dwcVerbatimLocality'] = json_resp.get('site')

		return dina_attributes

	def map_host(self, json_resp):
		"""Map a specimen's host from SeqDB to dina's collecting event

		Args:
			json_resp (json response): the json reponse when getting a specimen's host

		Returns:
			json object: dina entity attributes filled by SeqDB fields
		"""
		dina_attributes = {}

		dina_attributes['habitat'] = json_resp.get('habitat')
		dina_attributes['host'] = json_resp.get('hostETC')

		return dina_attributes
		