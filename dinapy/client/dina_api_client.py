import argparse
from dinapy.apis.objectstoreapi.uploadfileapi import UploadFileAPI
from pathlib import Path
import json


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
    # Initialize argparse
    parser = create_parser()
    args = parser.parse_args()

    dina_api_client = DinaApiClient()
    if args.upload_file:
        # Use Path object instead of just str to handle Windows paths and Posix (Unix) paths
        path = Path(args.upload_file)
        upload_file(args, dina_api_client, path)
    elif args.upload_dir:
        # .rglob recognizes file patterns
        pathlist = Path(args.upload_dir).rglob("*.*")
        for path in pathlist:
            upload_file(args, dina_api_client, path)
    else:
        raise Exception("Incorrect arguments.")


def upload_file(args: argparse.Namespace, dina_api_client: DinaApiClient, path: Path):
    response_json: dict = dina_api_client.uploadfileapi.upload(args.group, path.as_posix())
    log_response: dict = {
        "originalFilename": response_json.get("originalFilename"),
        "uuid": response_json.get("uuid"),
        "warnings": response_json.get("meta").get("warnings")
    }
    print(log_response)

    if args.verbose:
        print(response_json)


if __name__ == "__main__":
    main()
