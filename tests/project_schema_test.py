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
            "id": "01949469-fd77-7733-84cf-ea7eb1bd21ac",
            "type": "project",
            "links": {
                "self": "/api/v1/project/01949469-fd77-7733-84cf-ea7eb1bd21ac"
            },
            "attributes": {
                "createdOn": "2025-01-23T18:26:01.719936Z",
                "createdBy": "s-seqdbsoil",
                "group": "aafc",
                "name": "GRDI",
                "startDate": None,
                "endDate": None,
                "status": None,
                "contributors": [{
                    "agent": "6d59d480-e90a-459c-9eb4-b0c97a2cb4c6",
                    "roles": [
                    "project_leader"
                    ],
                    "remarks": "string"
                    }],
                "multilingualDescription": {
                    "descriptions": [
                        {
                            "lang": "en",
                            "desc": "Genomics Research and Development Initiative🎯"
                        }
                    ]
                },
                "extensionValues": {}
            },
            "relationships": {
                "attachment": {
                    "links": {
                        "self": "/api/v1/project/01949469-fd77-7733-84cf-ea7eb1bd21ac/relationships/attachment",
                        "related": "/api/v1/project/01949469-fd77-7733-84cf-ea7eb1bd21ac/attachment"
                    }
                }
            }
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
            ).name("test project").group("aafc").contributors().build()
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