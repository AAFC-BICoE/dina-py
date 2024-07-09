import argparse
import os
from dinapy.apis.objectstoreapi.uploadfileapi import UploadFileAPI


class DinaApiClient:
    """
    Class for handling making requests to DINA APIs
    """

    def __init__(self) -> None:
        self.uploadfileapi = UploadFileAPI(
            base_url="https://dina-dev2.biodiversity.agr.gc.ca/api/"
        )


def create_parser():
    parser = argparse.ArgumentParser(
        prog="Dina API Client", description="A client to make requests to DINA APIs."
    )
    parser.add_argument(
        "--upload_file",
        metavar="<file_path> : (str, required) = Path to the file to be uploaded.",
        help="Upload a file to Object Store. Argument: file_path",
    )
    parser.add_argument(
        "--upload_dir",
        metavar="<dir_path> : (str, required) = Path to the directory to be uploaded.",
        help="Upload all files in a directory to Object Store",
    )

    return parser


def main():
    os.environ["keycloak_username"] = "dina-admin"
    os.environ["keycloak_password"] = "dina-admin"
    parser = create_parser()
    args = parser.parse_args()
    dina_api_client = DinaApiClient()
    
    if args.upload_file:
        print("upload file")
        dina_api_client.uploadfileapi.upload('aafc', args.upload_file)
    elif args.upload_dir:
        print("upload dir")
        
    else:
        print("incorrect arguments")


if __name__ == "__main__":
    main()
