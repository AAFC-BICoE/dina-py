# This file contains tests relating to PersonAPI.
# Currently only contains tests for the PersonSchema (serialization and deserialization tests).
# API mock call tests should be added.

import unittest
import pprint

from marshmallow.exceptions import ValidationError

import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now you can import modules from the dinaapi package
from dinapy.schemas.managedattributeschema import ManagedAttributesSchema
from dinapy.entities.ManagedAttribute import ManagedAttributesDTO

KEYCLOAK_CONFIG_PATH = "tests/keycloak-config.yml"

VALID_MANAGED_ATTRIBUTES_DATA = {'data': {'attributes': {'acceptedValues': None,
                         'createdBy': 'dina-admin',
                         'createdOn': '2024-04-16T15:47:10.018813Z',
                         'group': 'aafc',
                         'key': 'test_attribute',
                         'managedAttributeComponent': 'COLLECTING_EVENT',
                         'multilingualDescription': {'descriptions': [{'desc': 'sample '
                                                                               'description',
                                                                       'lang': 'en'},
                                                                      {'desc': 'Je '
                                                                               "m'appelle "
                                                                               'Henry',
                                                                       'lang': 'fr'}]},
                         'name': 'test_attribute',
                         'unit': None,
                         'vocabularyElementType': 'STRING'},
          'id': '6881d9ac-621f-45b9-9bd8-16c9592a50b9',
          'links': {'self': '/api/v1/managed-attribute/6881d9ac-621f-45b9-9bd8-16c9592a50b9'},
          'type': 'managed-attribute'},
 'meta': {'moduleVersion': '0.84', 'totalResourceCount': 1}}


class ManagedAttributesSchemaTest(unittest.TestCase):
    def test_valid_managedattribute_schema(self):
        # Create a schema instance and validate the data
        schema = ManagedAttributesSchema()
        try:
            deserialized = schema.load(VALID_MANAGED_ATTRIBUTES_DATA)
            self.assertIsInstance(deserialized, ManagedAttributesDTO)
            serialized = schema.dump(deserialized)
            pp = pprint.PrettyPrinter(indent=0)
            pp.pprint(serialized)
            self.assertIsInstance(serialized, dict)
        except ValidationError as e:
            self.fail(f"Validation failed with error: {e.messages}")

if __name__ == "__main__":
    unittest.main()