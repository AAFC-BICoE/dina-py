import sys
import os
import unittest
import pprint

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.entities.FormTemplate import *
from dinapy.schemas.formtemplateschema import FormTemplateSchema

from dinapy.utils import *

class FormTemplateSchemaTest(unittest.TestCase):
		def test_serialization(self):
				self.maxDiff = None
				# Create a schema instance and validate the data
				attributes = (
						FormTemplateAttributesDTOBuilder()
						.set_createdBy("dina-admin")
						.set_group("aafc")
						.set_name("test-form-template")
						.set_restrictToCreatedBy(True)
						.set_viewConfiguration({
								"type": "material-sample-form-template"
						})
						.set_components([{
								"name": "show-parent-attributes-component",
										"order": 0,
										"visible": False,
										"gridSizeX": None,
										"sections": [
												{
														"name": "parent-attributes-section",
														"visible": True,
														"gridPositionX": None,
														"gridPositionY": None,
														"items": [
																{
																		"name": "parentAttributes",
																		"visible": True,
																		"gridPositionX": None,
																		"gridPositionY": None,
																		"defaultValue": []
																}
														]
												}
										]
								}
						])
						.build()
				)

				dto = (
						FormTemplateDTOBuilder()
						.set_attributes(attributes)
						.build()
				)

				schema = FormTemplateSchema()
				serialized_formTemplate = schema.dump(dto)
				expected = {
						"data": {
								"type": "form-template",
								"attributes": {
										"createdBy": "dina-admin",
										"group": "aafc",
										"name": "test-form-template",
										"restrictToCreatedBy": True,
										"viewConfiguration": {"type": "material-sample-form-template"},
										"components": [
												{
														"gridSizeX": None,
														"name": "show-parent-attributes-component",
														"order": 0,
														"sections": [
																{
																		"gridPositionX": None,
																		"gridPositionY": None,
																		"items": [
																				{
																						"defaultValue": [],
																						"gridPositionX": None,
																						"gridPositionY": None,
																						"name": "parentAttributes",
																						"visible": True
																				}
																		],
																		"name": "parent-attributes-section",
																		"visible": True
																}
														],
														"visible": False
												}
										]
								}
						}
				}
				
				pp = pprint.PrettyPrinter(indent=0)
				pp.pprint(serialized_formTemplate)
				self.assertIsInstance(serialized_formTemplate, dict)
				self.assertDictEqual(serialized_formTemplate, expected)

		def test_undefined_vs_null_serialization(self):
				# Pretend we are just updating one of the fields.
				attributes = (
						FormTemplateAttributesDTOBuilder()
						.set_restrictToCreatedBy(False)
						.set_group(None)
						.build()
				)

				dto = (
						FormTemplateDTOBuilder()
						.set_attributes(attributes)
						.build()
				)

				schema = FormTemplateSchema()
				serialized_formTemplate = schema.dump(dto)
				expected = {
						"data": {
								"type": "form-template",
								"attributes": {
									"restrictToCreatedBy": False,
									"group": None
								}
						}
				}
				pp = pprint.PrettyPrinter(indent=0)
				pp.pprint(serialized_formTemplate)
				self.assertIsInstance(serialized_formTemplate, dict)
				self.assertDictEqual(serialized_formTemplate, expected)

		def test_deserialization(self):
				data = {
						"data": {
								"type": "form-template",
								"attributes": {
										"createdBy": "dina-admin",
										"group": "aafc",
										"name": "test-form-template",
										"restrictToCreatedBy": True,
										"viewConfiguration": {"type": "material-sample-form-template"},
										"components": [
												{
														"gridSizeX": None,
														"name": "show-parent-attributes-component",
														"order": 0,
														"sections": [
																{
																		"gridPositionX": None,
																		"gridPositionY": None,
																		"items": [
																				{
																						"defaultValue": [],
																						"gridPositionX": None,
																						"gridPositionY": None,
																						"name": "parentAttributes",
																						"visible": True
																				}
																		],
																		"name": "parent-attributes-section",
																		"visible": True
																}
														],
														"visible": False
												}
										]
								}
						},
						"meta": {"totalResourceCount": 1, "moduleVersion": "0.91"},
				}

				schema = FormTemplateSchema()

				deserialized_form_template = schema.load(data)
				pp = pprint.PrettyPrinter(indent=0)
				pp.pprint(deserialized_form_template)
				self.assertIsInstance(deserialized_form_template, FormTemplateDTO)

if __name__ == "__main__":
		unittest.main()
