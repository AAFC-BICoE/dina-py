from dinapy.apis.objectstoreapi.objectstore_api import ObjectStoreApi
from dinapy.entities.Metadata import MetadataAttributesDTOBuilder, MetadataDTOBuilder
from dinapy.schemas.metadata_schema import MetadataSchema
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

def main():

    # File to be uploaded
    # Change as needed
    file = "examples/external-resource-import-demo/dataset2.txt"

    try:
        with open(file, 'r') as f:
            for line in f:
                # Parse through file
                # Take the last split for the filename
                file_name = line.split("/")[-1].split("\n")[0]

                # Set metadata attributes
                # Change as needed
                metadata_attributes = MetadataAttributesDTOBuilder(                        
                    ).set_dcType("DATASET").set_acCaption(file_name).set_acSubtype("SEQUENCE FILE"
                    ).set_dcFormat("application/gzip").set_resourceExternalURL(f"file:/{line}").set_fileExtension(".fastq.gz"
                    ).set_bucket("aafc").set_originalFilename(file_name).set_acTags('piglet_gut_microbiome_pre_vs_post_weaned').build()
                file_metadata = MetadataDTOBuilder().set_attributes(metadata_attributes).build()

                file_metadata_api = ObjectStoreApi()
                file_metadata_schema = MetadataSchema()

                # Build Metadata JSON object
                metadata_payload = file_metadata_schema.dump(file_metadata)
                # Upload to DINA instance
                extern_res_response = file_metadata_api.create_entity(metadata_payload, 'metadata')

                # Write UUIDs to file
                extern_res_uuid = extern_res_response.json()['data']['id']
                with open('examples/external-resource-import-demo/external_url_uuids.txt', 'a') as ff:
                    print(extern_res_uuid, file=ff)
                print(f"External Resource URL {extern_res_uuid} Created")

                # Build relationship to External Resource
                link_to_url = (
                    RelationshipDTO.Builder()
                        .add_relationship(
                            "attachment",       # Makes an attachment relationship
                            "metadata",         # The type of object to be attached
                            extern_res_uuid     # Object UUID
                        )
                    .build()
                )

                # Get Material Sample info from file name
                # Parsing done for a sample .txt file
                # Change as needed
                sample_name = file_name.split(".")[0]

                # Create Material Samples
                material_sample_api = MaterialSampleAPI()
                material_sample_schema = MaterialSampleSchema()
                # Define Material Sample Attributes based on variables
                # Change as needed
                material_sample_attributes = MaterialSampleAttributesDTOBuilder(
                    ).createdBy("dina-admin").group("aafc").materialSampleName(sample_name
                    ).materialSampleRemarks(f"File Name: {file_name}").build()
                # Build Material Sample
                material_sample = MaterialSampleDTOBuilder(
                    ).attributes(material_sample_attributes).relationships(link_to_url).build()
                
                serialized_material_sample = material_sample_schema.dump(material_sample)

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