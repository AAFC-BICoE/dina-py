from time import sleep
import json
import pprint
import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.apis.collectionapi.managedattributesapi import ManagedAttributeAPI
from dinapy.entities.ManagedAttribute import ManagedAttributesDTOBuilder,ManagedAttributeAttributesDTOBuilder
from dinapy.schemas.managedattributeschema import ManagedAttributesSchema
from dinapy.utils import get_dina_records_by_field

#TODO: Convert this into proper unit test.
os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

def main():
	dina_managed_attribute_api = ManagedAttributeAPI()
	for i in range(1, 16):
		# Build the attribute DTO
		managed_attribute_attributes = (
			ManagedAttributeAttributesDTOBuilder()
			.name(f"test attribute {i}")
			.vocabularyElementType("STRING")
			.group("aafc")
			.managedAttributeComponent("MATERIAL_SAMPLE")
			.build()
		)

		# Wrap it in the managed attribute DTO
		managed_attribute = ManagedAttributesDTOBuilder().attributes(managed_attribute_attributes).build()

		# Serialize using schema
		managed_attribute_schema = ManagedAttributesSchema()
		serialized_managed_attribute = managed_attribute_schema.dump(managed_attribute)

		# Send to API
		response = dina_managed_attribute_api.create_entity(serialized_managed_attribute)

		# Print the resulting ID
		print(response.json()['data']['id'])

if __name__ == '__main__':
	main()