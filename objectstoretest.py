import os
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

# output directory for the generated files to go temporaly.
output_directory = "./temp"

# File name to generate
file_name = "randomFile.bin"

file_size = 1024 * 1024 * 100  # 100 MB

generated_file_path = generate_random_file(output_directory, file_name, file_size)

print("File generated. Attempt to upload this to the object store.")

object_store_api.upload("aafc", generated_file_path)
