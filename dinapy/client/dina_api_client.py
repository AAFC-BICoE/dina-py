import argparse
import os
from dinapy.apis.objectstoreapi.uploadfileapi import UploadFileAPI
from pathlib import Path, PurePath


class DinaApiClient:
    """
    Class for handling making requests to DINA APIs
    """

    def __init__(self) -> None:
        self.uploadfileapi = UploadFileAPI(
            None, "https://dina-dev2.biodiversity.agr.gc.ca/api/"
        )


def create_parser():
    """
    Create command line parser.
    """
    parser = argparse.ArgumentParser(
        prog="Dina API Client", description="A client to make requests to DINA APIs."
    )
    parser.add_argument(
        "-upload_file",
        metavar="<file_path> : (str) = Path to the file to be uploaded.",
        help="Upload a file to Object Store. Argument: file_path",
    )
    parser.add_argument(
        "-upload_dir",
        metavar="<dir_path> : (str) = Path to the directory to be uploaded.",
        help="Upload all files in a directory to Object Store",
    )
    parser.add_argument(
        "-group",
        metavar="<group> : (str, required)",
        help="DINA group to be attached to resources.",
        required=True,
    )
    parser.add_argument(
        "-verbose",
        help="Verbosity of logs. Primarily for debugging.",
        action="store_true",
    )
    return parser


def main():
    # Set keycloak user
    os.environ["keycloak_username"] = "dina-admin"
    os.environ["keycloak_password"] = "dina-admin"
    
    # Initialize argparse
    parser = create_parser()
    args = parser.parse_args()
    
    dina_api_client = DinaApiClient()
    
    if args.upload_file:
        # Use Path object instead of just str to handle Windows paths and Posix (Unix) paths
        path = Path(args.upload_file)
        response_json = dina_api_client.uploadfileapi.upload(
            args.group, path.as_posix()
        )
        if args.verbose:
            print(response_json)
    elif args.upload_dir:
        # .rglob recognizes file patterns
        pathlist = Path(args.upload_dir).rglob("*.*")
        for path in pathlist:
            response_json = dina_api_client.uploadfileapi.upload(
                args.group, path.as_posix()
            )
            if args.verbose:
                print(response_json)

    else:
        raise Exception("Incorrect arguments.")


if __name__ == "__main__":
    main()
