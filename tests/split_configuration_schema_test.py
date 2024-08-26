import sys
import os
import unittest
import pprint

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.entities.SplitConfiguration import *
from dinapy.entities.Relationships import *
from dinapy.apis.collectionapi.splitconfigurationapi import SplitConfigurationAPI
from dinapy.schemas.splitconfigurationschema import SplitConfiguration

from dinapy.utils import *
from dinapy.utils import *

os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

class SplitConfigurationSchemaTest(unittest.TestCase):
    def test_serialization(self):
        # Create a schema instance and validate the data
        attributes = (
            SplitConfigurationAttributesDTOBuilder()
            .set_createdOn("2024-08-26T14:18:17.030325Z")
            .set_createdBy("dina-admin")
            .set_group("aafc")
            .set_name("test-split-configuration")
            .set_strategy("DIRECT_PARENT")
            .set_conditionalOnMaterialSampleTypes(["WHOLE_ORGANISM", "CULTURE_STRAIN"])
            .set_characterType("LOWER_LETTER")
            .set_separator("SPACE")
            .set_materialSampleTypeCreatedBySplit("CULTURE_STRAIN")
            .build()
        )

        dto = (
            SplitConfigurationDTOBuilder()
            .set_attributes(attributes)
            .build()
        )

        schema = SplitConfiguration()

        serialized_split_configuration = schema.dump(dto)
        expected = {
            "data": {
                "type": "split-configruation",
                "attributes": {
									"createdOn": "2024-08-26T14:18:17.030325Z",
									"createdBy": "dina-admin",
									"group": "aafc",
									"name": "test-split-configuration",
									"strategy": "DIRECT_PARENT",
									"conditionalOnMaterialSampleTypes": ["WHOLE_ORGANISM", "CULTURE_STRAIN"],
									"characterType": "LOWER_LETTER",
									"separator": "SPACE",
									"materialSampleTypeCreatedBySplit": "CULTURE_STRAIN"
                }
            }
        }
        pp = pprint.PrettyPrinter(indent=0)
        pp.pprint(serialized_split_configuration)
        self.assertIsInstance(serialized_split_configuration, dict)
        self.assertDictEqual(serialized_split_configuration, expected)

    def test_deserialization(self):
        data = {
            "data": {
                "id": "01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe",
                "type": "split-configuration",
                "links": {
                    "self": "/api/v1/split-configuration/01902d3c-69ae-7ad2-9bbe-e9c8bcf223fe"
                },
                "attributes": {
									"createdOn": "2024-08-26T14:18:17.030325Z",
									"createdBy": "dina-admin",
									"group": "aafc",
									"name": "test-split-configuration",
									"strategy": "DIRECT_PARENT",
									"conditionalOnMaterialSampleTypes": ["WHOLE_ORGANISM", "CULTURE_STRAIN"],
									"characterType": "LOWER_LETTER",
									"separator": "SPACE",
									"materialSampleTypeCreatedBySplit": "CULTURE_STRAIN"
                }
            },
            "meta": {"totalResourceCount": 1, "moduleVersion": "0.91"},
        }

        schema = SplitConfiguration()

        deserialized_split_configuration = schema.load(data)
        pp = pprint.PrettyPrinter(indent=0)
        pp.pprint(deserialized_split_configuration)
        self.assertIsInstance(deserialized_split_configuration, SplitConfigurationDTO)

if __name__ == "__main__":
    unittest.main()
