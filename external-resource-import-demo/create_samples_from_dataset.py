from dinapy.apis.collectionapi.materialsampleapi import MaterialSampleAPI
from dinapy.entities.MaterialSample import MaterialSampleDTOBuilder, MaterialSampleAttributesDTOBuilder
from dinapy.schemas.materialsampleschema import MaterialSampleSchema
from dinapy.entities.Relationships import RelationshipDTO

import traceback
import os
import sys

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Method Main
def main():
    # File to be parsed for samples
    file = "external-resource-import-demo/dataset1.txt"

    try:
        with open(file, 'r') as f:
            count = 0
            # Get Material Sample info from file name
            for line in f:
                # Parsing done for dataset1.txt
                sample_name = line.split(".")[-3]
                file_name = line.split("/")[-1].split("\n")[0]
                sample_type = "rumen"
                if line.split("-")[-1].split("_")[0] == "M":
                    sample_type = "milk"
                day = line.split("-")[-2].split("d")[1]

                create_sample(count, sample_name, file_name, sample_type, day)
                count += 1
    # Check exceptions
    except:
        with open('external-resource-import-demo/error_log.txt', 'a') as e:
            print(f'File Not Uploaded: {file}\n{traceback.format_exc()}', file=e)
        if 'Duplicate File Exists' in traceback.format_exc():
            return 'Duplicate File, File not Uploaded'
   
def create_sample(count, sample_name, file_name, sample_type, day):
    # Create Material Sample and match with External Resource URL
    count_match = 0
    with open("external-resource-import-demo/external_url_uuids.txt", 'r') as uuids:
        for uuid in uuids:
            # Linear search for next External URL UUID
            if count == count_match:
                # Build relationship to External Resource
                link_to_url = (
                    RelationshipDTO.Builder()
                        .add_relationship(
                            "attachment",           # Makes an attachment relationship
                            "metadata",             # The type of object to be attached
                            uuid.split("\n")[0]     # Object UUID
                        ).build()
                )

                material_sample_api = MaterialSampleAPI()
                material_sample_schema = MaterialSampleSchema()
                # Define Material Sample Attributes
                material_sample_attributes = MaterialSampleAttributesDTOBuilder(
                    ).createdBy("dina-admin").group("aafc").materialSampleName(sample_name
                    ).materialSampleRemarks(f"File Name: {file_name}\nDay: {day}\nType: {sample_type}").build()
                # Build Material Sample
                material_sample = MaterialSampleDTOBuilder(
                    ).attributes(material_sample_attributes).relationships(link_to_url).build()
                
                serialized_material_sample = material_sample_schema.dump(material_sample)

                # Create DINA object
                response = material_sample_api.create_entity(serialized_material_sample)
                id = response.json()['data']['id']
                print(f"Material Sample {id} created")

                # Write Material Sample UUIDs to file
                with open("external-resource-import-demo/material_sample_uuids.txt", 'a') as writer:
                    print(id, file=writer)
                return
            else:
                count_match += 1

# Execute main
if __name__ == "__main__":
    main()