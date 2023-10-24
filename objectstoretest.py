import os
import random
import secrets
from dinaapi.apis.objectstoreapi.uploadfileapi import UploadFileAPI

def generate_random_file(directory, file_name, file_size_bytes):
    file_path = os.path.join(directory, file_name)
    
    with open(file_path, 'wb') as file:
        while file_size_bytes > 0:
            # Generate a chunk of random data
            chunk_size = min(file_size_bytes, 1024 * 1024)  # Generate in 1 MB chunks (adjust as needed)
            random_data = secrets.token_bytes(chunk_size)
            
            # Write the random data to the file
            file.write(random_data)
            
            file_size_bytes -= chunk_size

    return file_path

# Configure keycloak username and password.
os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

# Configure path to keycloak configuration
object_store_api = UploadFileAPI("./keycloak-config.yml")

print("ObjectStore API is configured correctly")

# output directory for the generated files to go temporary.
output_directory = "./temp"

for i in range(1000000):
    # File name to generate
    file_name = f"randomFile_{i}.bin"

    # Random size to generate in MB:
    file_size = 1024 * 1024 * random.randint(1, 100)

    generated_file_path = generate_random_file(output_directory, file_name, file_size)

    print(f"File generated: {file_name} (Size: {file_size / 1024 / 1024}MB) - Attempting to upload this to the object store.")

    response = object_store_api.upload("aafc", generated_file_path)
    print(f"File uploaded. File identifier: {response['fileIdentifier']}")

    print(f"Verifying file exists...")
    file_info_response = object_store_api.get_file_info("aafc", response['fileIdentifier'] + response['evaluatedFileExtension'])
    print(f"File info: {file_info_response}")

    if ("length" not in file_info_response):
        print(f"Missing file found! File identifier: {response['fileIdentifier']} - File uploaded: {file_name}")
        break
    
    # Delete the generated file after it has been verified it exists:
    os.remove(os.path.join(output_directory, file_name))
    print("------------------------------------------------------------------------------------------------")