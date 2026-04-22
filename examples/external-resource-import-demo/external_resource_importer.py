from dinapy.apis.objectstoreapi.objectstore_api import ObjectStoreAPI
from dinapy.schemas.metadata_pydantic import MetadataDocument, MetadataData, MetadataAttributes
from dinapy.apis.collectionapi.materialsampleapi import MaterialSampleAPI
from dinapy.schemas.material_sample_pydantic import MaterialSampleDocument, MaterialSampleData, MaterialSampleAttributes
from dinapy.schemas.pydantic_base import RelationshipData, RelationshipLinkage

import traceback
import os
import sys

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():

    # File to be uploaded
    # Change as needed
    file = "examples/external-resource-import-demo/dataset.txt"

    try:
        with open(file, 'r') as f:
            for line in f:
                # Parse through file
                # Take the last split for the filename
                file_name = line.split("/")[-1].split("\n")[0]

                # Set metadata attributes and serialize
                # Change as needed
                file_metadata_api = ObjectStoreAPI()
                metadata_payload = MetadataDocument(
                    data=MetadataData(
                        type="metadata",
                        attributes=MetadataAttributes(
                            dcType="DATASET",
                            acCaption=file_name,
                            acSubtype="SEQUENCE FILE",
                            dcFormat="application/gzip",
                            resourceExternalURL=f"file:/{line}",
                            fileExtension=".fastq.gz",
                            bucket="aafc",
                            originalFilename=file_name
                        )
                    )
                ).serialize()

                # Upload to DINA instance
                extern_res_response = file_metadata_api.create_entity(metadata_payload, 'metadata')

                # Write UUIDs to file
                extern_res_uuid = extern_res_response.json()['data']['id']
                with open('examples/external-resource-import-demo/external_url_uuids.txt', 'a') as ff:
                    print(extern_res_uuid, file=ff)
                print(f"External Resource URL {extern_res_uuid} Created")

                # Get Material Sample info from file name
                # Parsing done for a sample .txt file
                # Change as needed
                sample_name = file_name.split(".")[0]

                # Create Material Samples with relationship to External Resource (attachment)
                material_sample_api = MaterialSampleAPI()
                serialized_material_sample = MaterialSampleDocument(
                    data=MaterialSampleData(
                        type="material-sample",
                        attributes=MaterialSampleAttributes(
                            createdBy="dina-admin",
                            group="aafc",
                            materialSampleName=sample_name,
                            materialSampleRemarks=f"File Name: {file_name}"
                        ),
                        relationships={
                            "attachment": RelationshipData(
                                data=[RelationshipLinkage(type="metadata", id=extern_res_uuid)]
                            )
                        }
                    )
                ).serialize()

                # Create DINA object
                mat_sample_response = material_sample_api.create_entity(serialized_material_sample)
                mat_sample_id = mat_sample_response.json()['data']['id']
                print(f"Material Sample {mat_sample_id} Created")
                print()

                # Write Material Sample UUIDs to file
                with open("examples/external-resource-import-demo/material_sample_uuids.txt", 'a') as writer:
                    print(mat_sample_id, file=writer)
            
    # Check exceptions
    except:
        with open('examples/external-resource-import-demo/error_log.txt', 'a') as f:
            print(f'File Not Uploaded: {file}\n{traceback.format_exc()}', file=f)
        if 'Duplicate File Exists' in traceback.format_exc():
            return 'Duplicate File, File not Uploaded'

if __name__ == '__main__':
    main()