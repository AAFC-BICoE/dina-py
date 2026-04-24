from time import sleep
import json
import pprint
import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.apis.collectionapi.managedattributesapi import ManagedAttributeAPI
from dinapy.schemas.managed_attribute_pydantic import (
    ManagedAttributeDocument, ManagedAttributeData, ManagedAttributeAttributes
)
from dinapy.utils import get_dina_records_by_field

#TODO: Convert this into proper unit test.
#os.environ["keycloak_username"] = "dina-admin"
#os.environ["keycloak_password"] = "dina-admin"

def main():
        dina_managed_attribute_api = ManagedAttributeAPI()
        for i in range(1, 16):
                # Build and serialize the managed attribute document
                serialized_managed_attribute = ManagedAttributeDocument(
                        data=ManagedAttributeData(
                                type="managed-attribute",
                                attributes=ManagedAttributeAttributes(
                                        name=f"test attribute {i}",
                                        vocabularyElementType="STRING",
                                        group="aafc",
                                        managedAttributeComponent="MATERIAL_SAMPLE"
                                )
                        )
                ).serialize()
        response = dina_managed_attribute_api.create_entity(serialized_managed_attribute)
        print("Create Managed Attribute Response:")
        pprint.pprint(response.json()['data']['id'])