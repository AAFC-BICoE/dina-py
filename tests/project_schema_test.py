# This file contains tests relating to ProjectAPI.
# Currently only contains tests for the ProjectSchema (serialization and deserialization tests).
# API mock call tests should be added.

import unittest
from marshmallow.exceptions import ValidationError

import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import modules from the dinaapi package
from dinapy.schemas.project_schema import ProjectSchema
from dinapy.entities.Project import *

VALID_PROJECT_DATA = {
    "data": {
        "id": "01939377-b15d-75f6-b405-54d9e719a509",
        "type": "project",
        "attributes": {
            "createdOn": "2024-12-04T20:58:35.237491Z",
            "createdBy": "dina-admin",
            "group": "aafc",
            "name": "test project",
            "startDate": "2024-05-01",
            "endDate": "2025-12-04",
            "status": "Open",
            "multilingualDescription": {
                "descriptions": [
                    {
                        "lang": "en",
                        "desc": "test decription"
                    }
                ]
            },
            "extensionValues": {}
        },
        "relationships": {}
    }
}

class ProjectSchemaTest(unittest.TestCase):
    def test_deserialize_project(self):
        schema = ProjectSchema()
        try:
            result = schema.load(VALID_PROJECT_DATA)
            print(result.__dict__)
            self.assertIsInstance(result, ProjectDTO)
        except ValidationError as e:
            self.fail(f"Validation failed with error: {e.messages}")

    def test_serialize_project(self):
        schema = ProjectSchema()
        project_attributes = ProjectAttributesDTOBuilder(
            ).name("test project").group("aafc").build()
        project = ProjectDTOBuilder().attributes(project_attributes).build()

        try:
            serialized_project = schema.dump(project)
            expected = {
                "data": {
                    "type": "project",
                    "attributes": {
                        "name": "test project",
                        "group": "aafc"
                    }
                }
            }
            print(serialized_project)
            self.assertIsInstance(serialized_project, dict)
            self.assertDictEqual(serialized_project, expected)
        except ValidationError as e:
            self.fail(f"Validation failed with error: {e.messages}")

if __name__ == "__main__":
    unittest.main()