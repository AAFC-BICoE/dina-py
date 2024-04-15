from time import sleep
import json

import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.apis.collectionapi.materialsampleapi import MaterialSampleAPI
from dinapy.entities.MaterialSample import MaterialSampleAttributesDTOBuilder,MaterialSampleDTOBuilder
from dinapy.schemas.materialsampleschema import MaterialSampleSchema
from dinapy.utils import get_dina_records_by_field

#TODO: Convert this into proper unit test.

os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

def main():

	dina_material_sample_api = MaterialSampleAPI()

	material_sample_schema = MaterialSampleSchema()
	
	
	#response = dina_material_sample_api.get_entity_by_field("group","aafc")
	list = get_dina_records_by_field(dina_material_sample_api,"group","aafc")

	id = list[0]["id"]

	material_sample_attributes = MaterialSampleAttributesDTOBuilder().group("aafc").createdBy("dina-admin").build()
	material_sample = MaterialSampleDTOBuilder().id(id).attributes(material_sample_attributes).build()
	serialized_material_sample = material_sample_schema.dump(material_sample)

	response = dina_material_sample_api.update_entity(id,serialized_material_sample)

	print(response.status_code)

	deserialized_material_sample = material_sample_schema.load(response.json())

	print(deserialized_material_sample)

	
	
if __name__ == '__main__':
	main()