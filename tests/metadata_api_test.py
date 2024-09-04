import sys
import os
from pathlib import Path
import yaml

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.client.dina_api_client import DinaApiClient, create_metadatas

os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

DINA_API_CONFIG_TEST_PATH = "./tests/resources/dina-api-config-test.yml"
OBJECT_UPLOAD_PATH = "./tests/resources/object-upload-test"

def main():
    dina_api_client = DinaApiClient()
    pathlist = Path(OBJECT_UPLOAD_PATH).rglob("*.*")
    with open(DINA_API_CONFIG_TEST_PATH, "r", encoding="utf-8") as dina_api_config_file:
        dina_api_config: dict = yaml.safe_load(dina_api_config_file)
        group = dina_api_config["group"]
        create_metadatas(dina_api_client, pathlist, dina_api_config, group)

if __name__ == "__main__":
    main()
