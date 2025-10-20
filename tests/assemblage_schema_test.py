# Currently only contains tests for the AssemblageSchema (serialization and deserialization tests).

import unittest
import pprint
import copy
from marshmallow.exceptions import ValidationError

import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now you can import modules from the dinaapi package
from dinapy.schemas.assemblageschema import AssemblageSchema
from dinapy.entities.Assemblage	import *


KEYCLOAK_CONFIG_PATH = "tests/keycloak-config.yml"

VALID_ASSEMBLAGE_DATA = {
	"data": {
		"id": "c1e66a36-bf48-40b5-885e-118e6507c2bd",
		"type": "assemblage",
		"attributes": {
			"createdOn": "2022-11-29T13:36:56.451132Z",
			"createdBy": "dina-admin",
			"group": "aafc",
			"name": "assemblage test",
			"managedAttributes": {},
			"multilingualTitle": {
				"titles": [
					{"lang": "en", "title": "Wheat Assemblage"},
					{"lang": "fr", "title": "Assemblage de blé"}
				]
			},
			"multilingualDescription": {
				"descriptions": [
					{"lang": "en", "desc": "Collection of wheat-related items."},
					{"lang": "fr", "desc": "Collection d’éléments liés au blé."}
				]
			}
		},
		"relationships": {
			"attachment": {
				"links": {
					"self": "/api/v1/assemblage/c1e66a36-bf48-40b5-885e-118e6507c2bd/relationships/attachment",
					"related": "/api/v1/assemblage/c1e66a36-bf48-40b5-885e-118e6507c2bd/attachment"
				},
				"data": [
					{"type": "metadata", "id": "a9f3d2b4-1234-5678-9876-abcdef123456"},
					{"type": "metadata", "id": "b7e8f9c0-2345-6789-8765-fedcba654321"}
				]
			}
		}
	}
}

INVALID_ASSEMBLAGE_DATA = {
	"data": 
		{
			"id": "c1e66a36-bf48-40b5-885e-118e6507c2bd",
			"type": "assemblage",
			"links": {
				"self": "/api/v1/assemblage/c1e66a36-bf48-40b5-885e-118e6507c2bd"
			},
			"attributes": {
				"createdOn": "2022-11-29T13:36:56.451132Z",
				"createdBy": "dina-admin",
				"group": "aafc",
				"namee": "assemblage test",
				"managedAttributes": {},
				"multilingualTitle": {
					"titless": []
				},
				"multilingualDescription": {
					"descriptions": []
				}
			},
			"relationships": {
				"attachment": {
					"links": {
						"self": "/api/v1/assemblage/c1e66a36-bf48-40b5-885e-118e6507c2bd/relationships/attachment",
						"related": "/api/v1/assemblage/c1e66a36-bf48-40b5-885e-118e6507c2bd/attachment"
					}
				}
			}
		}
		}

class AssemblageSchemaTest(unittest.TestCase):

	def test_serialize_assemblage(self):
		schema = AssemblageSchema()

		attrs = (
			AssemblageAttributesDTOBuilder()
			.name("Assemblage-123")
			.group("aafc")
			.addTitle("en", "Wheat Assemblage")
			.addTitle("fr", "Assemblage de blé")
			.addDescription("en", "Collection of wheat-related items.")
			.addDescription("fr", "Collection d’éléments liés au blé.")
			.build()
		)
		assemblage = AssemblageDTOBuilder().attributes(attrs).build()
		serialized_assemblage = schema.dump(assemblage)
		
		print("Serialized:", serialized_assemblage)

		# Assert envelope
		self.assertIsInstance(serialized_assemblage, dict)

		# Support both JSON:API ("data" envelope) and flat dicts
		payload = serialized_assemblage.get("data", serialized_assemblage)
		self.assertIsInstance(payload, dict)

		# If JSON:API, make sure type is correct
		if "data" in serialized_assemblage:
			self.assertEqual(payload.get("type"), "assemblage")

		# Extract attributes
		attrs_out = payload.get("attributes", payload)
		self.assertIsInstance(attrs_out, dict)

		# Basic attribute checks
		self.assertEqual(attrs_out.get("name"), "Assemblage-123")
		self.assertEqual(attrs_out.get("group"), "aafc")

		# ---- multilingualTitle assertions ----
		self.assertIn("multilingualTitle", attrs_out)
		mt = attrs_out["multilingualTitle"]
		self.assertIsInstance(mt, dict)
		self.assertIn("titles", mt)
		self.assertIsInstance(mt["titles"], list)
		self.assertGreaterEqual(len(mt["titles"]), 2)

		titles_map = {e["lang"]: e["title"] for e in mt["titles"]}
		self.assertIn("en", titles_map)
		self.assertIn("fr", titles_map)
		self.assertEqual(titles_map["en"], "Wheat Assemblage")
		self.assertEqual(titles_map["fr"], "Assemblage de blé")

		# ---- multilingualDescription assertions ----
		self.assertIn("multilingualDescription", attrs_out)
		md = attrs_out["multilingualDescription"]
		self.assertIsInstance(md, dict)
		self.assertIn("descriptions", md)
		self.assertIsInstance(md["descriptions"], list)
		self.assertGreaterEqual(len(md["descriptions"]), 2)

		descs_map = {e["lang"]: e["desc"] for e in md["descriptions"]}
		self.assertIn("en", descs_map)
		self.assertIn("fr", descs_map)
		self.assertEqual(descs_map["en"], "Collection of wheat-related items.")
		self.assertEqual(descs_map["fr"], "Collection d’éléments liés au blé.")



	def test_valid_assemblage_schema(self):
		schema = AssemblageSchema()
		try:
			result = schema.load(VALID_ASSEMBLAGE_DATA)
		except ValidationError as e:
			self.fail(f"Validation failed with error: {e.messages}")

		# Result should be an AssemblageDTO (@post_load constructs it)
		self.assertIsInstance(result, AssemblageDTO)

		attrs = result.get_attributes() if hasattr(result, "get_attributes") else result.attributes
		rels = result.get_relationships() if hasattr(result, "get_relationships") else result.relationships

		self.assertEqual(attrs.get("name"), "assemblage test")
		self.assertEqual(attrs["multilingualTitle"]["titles"][0]["lang"], "en")
		self.assertEqual(attrs["multilingualDescription"]["descriptions"][0]["lang"], "en")
		self.assertEqual(attrs["multilingualDescription"]["descriptions"][0]["lang"], "en")
		self.assertEqual(len(rels['attachment']),2)

	def test_invalid_assemblage_schema(self):
		schema = AssemblageSchema()

		# Start from valid baseline
		base = copy.deepcopy(VALID_ASSEMBLAGE_DATA)

		cases = []

		# 1) Relationship cardinality: attachment is to-many, but we provide a single object
		def make_not_list(payload):
			payload["data"]["relationships"]["attachment"]["data"] = {
				"type": "metadata",  # keep type consistent with your schema
				"id": "11111111-2222-3333-4444-555555555555",
			}
		cases.append(("attachment is to-many but received a single object", make_not_list))

		# 2) Attribute type mismatch: 'group' should be a string
		def make_group_wrong_type(payload):
			payload["data"]["attributes"]["group"] = 123
		cases.append(("attribute 'group' has wrong type (expected string)", make_group_wrong_type))

		# 3) Attribute type mismatch: 'managedAttributes' should be a dict
		def make_managed_attributes_wrong_type(payload):
			payload["data"]["attributes"]["managedAttributes"] = "not-a-dict"
		cases.append(("attribute 'managedAttributes' has wrong type (expected dict)", make_managed_attributes_wrong_type))

		# 4) DateTime format invalid for 'createdOn'
		def make_bad_created_on(payload):
			payload["data"]["attributes"]["createdOn"] = "16-10-2025 10:00"
		cases.append(("attribute 'createdOn' has invalid datetime format", make_bad_created_on))

		# 5) multilingualTitle: 'titles' must be a list
		def make_bad_multilingual_title_container(payload):
			payload["data"]["attributes"]["multilingualTitle"] = {
				"titles": {"lang": "en", "title": "Wheat"}
			}
		cases.append(("multilingualTitle.titles must be a list", make_bad_multilingual_title_container))

		# 6) multilingualDescription: 'desc' must be a string (wrong type in one entry)
		def make_bad_multilingual_desc_entry(payload):
			attrs = payload["data"]["attributes"]
			attrs.setdefault("multilingualDescription", {}).setdefault("descriptions", [])
			# Ensure there's at least one valid entry, then add an invalid one
			if not attrs["multilingualDescription"]["descriptions"]:
				attrs["multilingualDescription"]["descriptions"].append(
					{"lang": "en", "desc": "Valid description"}
				)
			attrs["multilingualDescription"]["descriptions"].append(
				{"lang": "en", "desc": 123}
			)
		cases.append(("multilingualDescription entry has wrong type for 'desc'", make_bad_multilingual_desc_entry))

		for label, mut in cases:
			with self.subTest(label=label):
				payload = copy.deepcopy(base)
				mut(payload)
				with self.assertRaises(ValidationError) as cm:
					schema.load(payload)

				# Show the error to help with debugging
				print(f"\n[{label}] ValidationError:\n", pprint.pformat(cm.exception.messages, indent=2))
				self.assertTrue(cm.exception.messages)  # Ensure there are error details

if __name__ == "__main__":
	unittest.main()
