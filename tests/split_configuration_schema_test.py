import sys
import os
import unittest
import pprint

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.entities.SplitConfiguration import *
from dinapy.schemas.splitconfigurationschema import SplitConfigurationSchema

from dinapy.utils import *

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

        schema = SplitConfigurationSchema()
        serialized_split_configuration = schema.dump(schema.load(dto))
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

        schema = SplitConfigurationSchema()

        deserialized_split_configuration = schema.load(data)
        pp = pprint.PrettyPrinter(indent=0)
        pp.pprint(deserialized_split_configuration)
        self.assertIsInstance(deserialized_split_configuration, SplitConfigurationDTO)

if __name__ == "__main__":
    unittest.main()
