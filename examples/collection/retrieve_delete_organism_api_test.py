from time import sleep
import json
import pprint
import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.apis.collectionapi.organismapi import OrganismAPI
from dinapy.utils import get_dina_records_by_field

#TODO: Convert this into proper unit test.
os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

def main():
	dina_organism_api = OrganismAPI()

	response = dina_organism_api.get_entity("d3e87a62-558d-4261-bb14-7d83f0523342")
	print(response.json()['data'])
	
	response = dina_organism_api.remove_entity("d3e87a62-558d-4261-bb14-7d83f0523342")
	print(response.status_code)

if __name__ == '__main__':
	main()