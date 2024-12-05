from dinapy.apis.collectionapi.materialsampleapi import MaterialSampleAPI
from dinapy.entities.MaterialSample import MaterialSampleDTOBuilder
from dinapy.schemas.materialsampleschema import MaterialSampleSchema
from dinapy.entities.Relationships import RelationshipDTO

import traceback
import os
import sys

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():

    # Pre-created Project Object UUID
    # Change as needed
    project_uuid = "01939841-002e-7597-86f2-368144d714b9"

    # Build relationship to Project
    link_to_project = (
        RelationshipDTO.Builder()
            .add_relationship(
                "projects",     # Makes a projects relationship
                "project",      # The type of object to be attached
                project_uuid    # Project UUID
            )
        .build()
    )

    # Build Material Sample JSON Data
    material_sample_api = MaterialSampleAPI()
    material_sample_schema = MaterialSampleSchema()
    material_sample = MaterialSampleDTOBuilder(
        ).relationships(link_to_project).build()
    # JSON data to be passed
    serialized_material_sample = material_sample_schema.dump(material_sample)

    # File that stores Material Sample UUIDs
    file = "examples/external-resource-import-demo/material_sample_uuids.txt"
    try:
        with open(file, 'r') as f:
            for line in f:
                mat_sample_uuid = line.split("\n")[0]

                # Update DINA Material Sample Object
                response = material_sample_api.update_entity(mat_sample_uuid, serialized_material_sample)
                mat_sample_id = response.json()['data']['id']
                print(f"Material Sample {mat_sample_id} Updated")
    except:
        with open('examples/external-resource-import-demo/error_log.txt', 'a') as f:
            print(f'File Not Uploaded: {file}\n{traceback.format_exc()}', file=f)

if __name__ == '__main__':
    main()