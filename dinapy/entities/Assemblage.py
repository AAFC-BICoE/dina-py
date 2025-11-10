from typing import Dict, List, Optional, Union


class AssemblageDTO:
	def __init__(self, id = None, type = "assemblage", attributes = None, relationships = 'undefined'):
		self.id = id
		self.type = type
		self.attributes = attributes or {}
		self.relationships = relationships

	def get_id(self):
		return self.id
	def get_type(self):
		return self.type
	def get_attributes(self):
		return self.attributes 
	def get_relationships(self):
		return self.relationships 

class AssemblageDTOBuilder:
	def __init__(self):
		self.managed_attribute = AssemblageDTO(
			id=None,
			type="assemblage",
			attributes=None
		)

	def id(self, id):
		self.managed_attribute.id = id
		return self
	
	def attributes(self, attributes):
		self.managed_attribute.attributes = attributes
		return self

	def build(self):
		return self.managed_attribute

	def to_dict(self):
		return self.__dict__
		
class AssemblageAttributesDTO:
	def __init__(self, name=None, createdOn=None, createdBy=None, group=None, multilingualTitle = {}, multilingualDescription={}):
		self.name = name
		self.createdOn = createdOn
		self.createdBy = createdBy
		self.group = group

		# Normalize to required shapes
		self.multilingualTitle = self._normalize_titles(multilingualTitle)
		self.multilingualDescription = self._normalize_descriptions(multilingualDescription)


	@staticmethod
	def _normalize_titles(value) -> dict:
		"""
		Accept None, {}, [], {'titles': [...]}, a list of entries, or even a single entry dict.
		Coerce to: {'titles': [ ... ]}.
		"""
		# Treat any falsy input as empty
		if not value:
			return {"titles": []}

		# If already wrapped with 'titles'
		if isinstance(value, dict):
			# Single-entry dict (rare but convenient): {"lang": "...", "title": "..."}
			if "lang" in value and "title" in value:
				return {"titles": [AssemblageAttributesDTO._validate_title_entry(value)]}

			if "titles" in value:
				titles = value.get("titles", [])
				if not titles:
					return {"titles": []}
				return {"titles": [AssemblageAttributesDTO._validate_title_entry(e) for e in titles]}

			# Any other dict → treat as empty to be lenient
			return {"titles": []}

		# Plain iterable list/tuple of entries
		if isinstance(value, (list, tuple)):
			return {"titles": [AssemblageAttributesDTO._validate_title_entry(e) for e in value]}

		raise TypeError(
			"multilingualTitle must be None/empty, a dict with 'titles', a single {lang,title}, or a list of entries."
		)

	@staticmethod
	def _normalize_descriptions(value) -> dict:
		"""
		Accept None, {}, [], {'descriptions': [...]}, a list of entries, or even a single entry dict.
		Coerce to: {'descriptions': [ ... ]}.
		"""
		if not value:
			return {"descriptions": []}

		if isinstance(value, dict):
			# Single-entry dict convenience: {"lang": "...", "desc": "..."}
			if "lang" in value and "desc" in value:
				return {"descriptions": [AssemblageAttributesDTO._validate_desc_entry(value)]}

			if "descriptions" in value:
				descs = value.get("descriptions", [])
				if not descs:
					return {"descriptions": []}
				return {"descriptions": [AssemblageAttributesDTO._validate_desc_entry(e) for e in descs]}

			# Any other dict → treat as empty
			return {"descriptions": []}

		if isinstance(value, (list, tuple)):
			return {"descriptions": [AssemblageAttributesDTO._validate_desc_entry(e) for e in value]}

		raise TypeError(
			"multilingualDescription must be None/empty, a dict with 'descriptions', a single {lang,desc}, or a list of entries."
		)

	@staticmethod
	def _validate_title_entry(entry: dict) -> dict:
		if not isinstance(entry, dict) or "lang" not in entry or "title" not in entry:
			raise ValueError("Each title entry must be a dict with 'lang' and 'title'.")
		lang = str(entry["lang"]).strip()
		title = str(entry["title"]).strip()
		if not lang or not title:
			raise ValueError("Both 'lang' and 'title' must be non-empty strings.")
		return {"lang": lang, "title": title}

	@staticmethod
	def _validate_desc_entry(entry: dict) -> dict:
		if not isinstance(entry, dict) or "lang" not in entry or "desc" not in entry:
			raise ValueError("Each description entry must be a dict with 'lang' and 'desc'.")
		lang = str(entry["lang"]).strip()
		desc = str(entry["desc"]).strip()
		if not lang or not desc:
			raise ValueError("Both 'lang' and 'desc' must be non-empty strings.")
		return {"lang": lang, "desc": desc}

class AssemblageAttributesDTOBuilder:
	def __init__(self):
		self.dto = AssemblageAttributesDTO()

	def name(self, name):
		self.dto.name = name
		return self

	def createdOn(self, createdOn):
		self.dto.createdOn = createdOn
		return self

	def createdBy(self, createdBy):
		self.dto.createdBy = createdBy
		return self

	def group(self, group):
		self.dto.group = group
		return self
	
   
   # ----- Multilingual Title -----
	def multilingualTitle(self, multilingualTitle: Union[dict, List[Dict[str, str]]]):
		"""
		Accepts:
		  - {"titles": [ { "lang": "...", "title": "..." }, ... ]}
		  - [ { "lang": "...", "title": "..." }, ... ]
		"""
		self.dto.multilingualTitle = AssemblageAttributesDTO._normalize_titles(multilingualTitle)
		return self

	def addTitle(self, lang: str, title: str):
		"""
		Adds a single title entry (e.g., "en", "Wheat Assemblage").
		"""
		entry = AssemblageAttributesDTO._validate_title_entry({"lang": lang, "title": title})
		if "titles" not in self.dto.multilingualTitle or not isinstance(self.dto.multilingualTitle["titles"], list):
			self.dto.multilingualTitle = {"titles": []}
		self.dto.multilingualTitle["titles"].append(entry)
		return self

	# ----- Multilingual Description -----
	def multilingualDescription(self, multilingualDescription: Union[dict, List[Dict[str, str]]]):
		"""
		Accepts:
		  - {"descriptions": [ { "lang": "...", "desc": "..." }, ... ]}
		  - [ { "lang": "...", "desc": "..." }, ... ]
		"""
		self.dto.multilingualDescription = AssemblageAttributesDTO._normalize_descriptions(multilingualDescription)
		return self

	def addDescription(self, lang: str, desc: str):
		"""
		Adds a single description entry (e.g., "fr", "Assemblage de blé").
		"""
		entry = AssemblageAttributesDTO._validate_desc_entry({"lang": lang, "desc": desc})
		if "descriptions" not in self.dto.multilingualDescription or not isinstance(self.dto.multilingualDescription["descriptions"], list):
			self.dto.multilingualDescription = {"descriptions": []}
		self.dto.multilingualDescription["descriptions"].append(entry)
		return self


	def build(self):
		return self.dto

		# {
		#     "id": "c1e66a36-bf48-40b5-885e-118e6507c2bd",
		#     "type": "assemblage",
		#     "links": {
		#         "self": "/api/v1/assemblage/c1e66a36-bf48-40b5-885e-118e6507c2bd"
		#     },
		#     "attributes": {
		#         "createdOn": "2022-11-29T13:36:56.451132Z",
		#         "createdBy": "dina-admin",
		#         "group": "aafc",
		#         "name": "assemblage test",
		#         "managedAttributes": {},
		#         "multilingualTitle": {
		#             "titles": []
		#         },
		#         "multilingualDescription": {
		#             "descriptions": []
		#         }
		#     },
		#     "relationships": {
		#         "attachment": {
		#             "links": {
		#                 "self": "/api/v1/assemblage/c1e66a36-bf48-40b5-885e-118e6507c2bd/relationships/attachment",
		#                 "related": "/api/v1/assemblage/c1e66a36-bf48-40b5-885e-118e6507c2bd/attachment"
		#             }
		#         }
		#     }
		# }