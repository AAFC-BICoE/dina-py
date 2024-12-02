from dinapy.apis.objectstoreapi.objectstore_api import ObjectStoreApi
from dinapy.entities.Metadata import MetadataAttributesDTOBuilder, MetadataDTOBuilder
from dinapy.schemas.metadata_schema import MetadataSchema
import traceback

import os
import sys

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():

    # File to be uploaded
    file = "external-resource-import-demo/dataset2.txt"

    try:
        with open(file, 'r') as f:
            uuids = []
            for line in f:
                # Parse through file
                linesplit = line.split("/")
                # Take the last split for the filename
                name = linesplit[-1]

                # Set metadata attributes
                metadata_attributes = MetadataAttributesDTOBuilder(                        
                    ).set_dcType("DATASET").set_acCaption(name).set_acSubtype("SEQUENCE FILE"
                    ).set_dcFormat("application/gzip").set_resourceExternalURL(f"file:/{line}").set_fileExtension(".fastq.gz"
                    ).set_bucket("aafc").set_originalFilename(name).build()
                file_metadata = MetadataDTOBuilder().set_attributes(metadata_attributes).build()

                file_metadata_api = ObjectStoreApi()
                file_metadata_schema = MetadataSchema()

                print(line)
                print(name)

                # Build Metadata JSON object
                metadata_payload = file_metadata_schema.dump(file_metadata)
                print(metadata_payload)
                print()
                # Upload to DINA instance
                response = file_metadata_api.create_entity(metadata_payload, 'metadata')
                print(response)
                uuids.append(response.json()['data']['id'])
                print()

            with open('external-resource-import-demo/external_url_uuids.txt', 'a') as f:
                print(uuids, file=f)
            
    # Check exceptions
    except:
        with open('error_log.txt', 'a') as f:
            print(f'File Not Uploaded: {file}\n{traceback.format_exc()}', file=f)
        if 'Duplicate File Exists' in traceback.format_exc():
            return 'Duplicate File, File not Uploaded'

if __name__ == '__main__':
    main()