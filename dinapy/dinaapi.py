# This file contains the base class to inherit from when adding functionality for Dina entities.
# Handles authentication and token generation, as well as generating a requests session.
# Creates basic request methods that should be used by inherited classes.

import os
import requests
import yaml
import logging
import json

from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError

KEYCLOAK_CONFIG_PATH = "./keycloak-config.yml"
BASE_URL = "https://dina.local/api/"
BULK_POST_ENDPOINT_URL = "/bulk"

class DinaAPI:
    """Base class containing basic DINA module API calls.

    This class provides the basic functionality for making API calls to the DINA web services.
    It handles token authentication using Keycloak and sets necessary headers for API requests.

    Parameters:
            config_path (str): Path to the YAML configuration file containing Keycloak settings.

    Attributes:
            configs (dict): Configuration information loaded from the YAML file.
            token (dict): Keycloak token obtained during authentication.
            session (requests.Session): Requests session object for making HTTP requests.
            base_url (str): Base URL for the DINA web API.

    """

    # Class-level field. class level are shared across all instances of the class. This means they belong to the class itself, not to any individual instance
    token = None

    def __init__(self, config_path: str = None, base_url: str = None):
        """Creates basic web services based on the provided config path or a default path.

        If the config_path is not provided, the default KEYCLOAK_CONFIG_PATH will be used.

        Parameters:
                config_path (str, optional): Path to the YAML configuration file (default: None).
                base_url (str, optional): URL to the URL to perform the API requests against. If not
                        provided then local deployment URL is used. Should end with a forward slash.
        """
        if config_path is None:
            config_path = KEYCLOAK_CONFIG_PATH
        if base_url is None:
            self.base_url = BASE_URL

        logging.basicConfig(level=logging.INFO)
        logging.captureWarnings(True)

        self.configs = None

        self.keycloak = None

        self.session = requests.Session()

        self.set_configs(config_path)
        self.set_keycloak()

    def set_configs(self, config_path: str):
        """Loads config from YAML file and saves it to the 'configs' variable.

        Parameters:
                config_path (str): Path to the YAML configuration file.

        Raises:
                FileNotFoundError: If the config_path does not point to an existing file.
                yaml.YAMLError: If there is an error in reading or parsing the YAML file.

        """
        try:
            with open(config_path, "r", encoding="utf-8") as config_file:
                self.configs = yaml.safe_load(config_file)
                if (
                    self.configs["keycloak_username"]
                    and self.configs["keycloak_password"]
                ):
                    # Set keycloak user
                    os.environ["keycloak_username"] = self.configs["keycloak_username"]
                    os.environ["keycloak_password"] = self.configs["keycloak_password"]
                if self.configs["url"]:
                    self.base_url = f'{self.configs["url"]}/api/'
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {config_path}")
            raise
        except yaml.YAMLError as exc:
            logging.error("Error in configuration file. Cannot execute.")
            logging.error(exc)
            raise
        
    def set_keycloak(self):
        """
        Creates a Keycloak token based on configurations and environment variables.
        """
        self.keycloak = KeycloakOpenID(
            server_url=f'{self.configs["url"]}/auth/',
            client_id=self.configs["client_id"],
            realm_name=self.configs["realm_name"],
            client_secret_key=None,
            verify=self.configs["secure"],
        )
        if not DinaAPI.token:
            print(f'User: {os.environ.get("keycloak_username")}')
            self.generate_token()
    
    def generate_token(self):
        try:
            DinaAPI.token = self.keycloak.token(
                os.environ.get("keycloak_username"),
                os.environ.get("keycloak_password"),
            )

            # Set the bearer token in the header.
            self.set_req_header()
        except Exception as exc:
            logging.error(exc)
            raise

    def refresh_token(self):
        """
        Check if the token still valid or if it needs to be regenerated.
        """
        try:
            # Set the bearer token in the header.
            self.set_req_header()
            self.keycloak.userinfo(DinaAPI.token["access_token"])
        except KeycloakAuthenticationError as e:
            self.generate_token()

    def set_req_header(self):
        """Sets the header for the session.

        The header includes the 'Accept', 'Content-Type', and 'Authorization' fields.
        Token must be set beforehand.

        """
        self.session.headers.update(
            {
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/vnd.api+json",
                "Authorization": f"bearer {DinaAPI.token['access_token']}",
            }
        )

    def get_req_dina(self, full_url: str, params: dict = None, stream = bool) -> requests.Response:
        """Base method for a GET request to DINA.

        Args:
                full_url (str): The full URL for the API request (extension of the base_url).
                params (dict, optional): Query parameters for the request (default: None).

        Returns:
                requests.Response: The response object containing the API response.

        Raises:
                requests.exceptions.RequestException: If there is an error during the HTTP request.

        """
        self.refresh_token()
        try:
            response = self.session.get(
                full_url, params=params, verify=self.configs["secure"], stream=stream
            )
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        except requests.exceptions.RequestException as exc:
            # Handle the exception here, e.g., log the error or raise a custom exception
            logging.error(f"Failed to fetch data from {full_url}: {exc}")
            raise  # Re-raise the exception

        return response

    # TODO: everything below is untested

    def post_req_dina(self, full_url: str, json_data: dict, params: dict = None):
        """
        Base method for a POST request to DINA.

        Args:
                full_url (str): The full URL for the API request (extension of the base_url).
                json_data (dict): JSON data to be sent in the request body.
                params (dict, optional): Query parameters for the request (default: None).

        Returns:
                requests.Response: The response object containing the API response.

        """
        self.refresh_token()
        try:
            response = self.session.post(
                full_url,
                json=json_data,
                headers=self.session.headers,
                verify=self.configs["secure"],
            )
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        except requests.exceptions.RequestException as exc:
            # Handle the exception here, e.g., log the error or raise a custom exception
            logging.error(f"Failed to fetch data from {full_url}: {exc}")
            raise  # Re-raise the exception

        return response

    def post_file_dina(self, full_url: str, file_path: str, params: dict = None):
        """
        Base method for a POST request to DINA.

        Args:
                full_url (str): The full URL for the API request (extension of the base_url).
                file_path (str): The location of the file to be uploaded including file itself and
                        extension.
                params (dict, optional): Query parameters for the request (default: None).

        Returns:
                requests.Response: The response object containing the API response.

        Raises:
                requests.exceptions.RequestException: If there is an error during the HTTP request.
        """
        self.refresh_token()

        try:
            file = {"file": open(file_path, "rb")}
        except FileNotFoundError:
            logging.error(
                f"\t\tError: Unable to locate file -> {file_path}.\n\t\t\tEnsure the filepath is correct."
            )
            return None

        try:
            # For uploading the Accept and Content-Type are not included.
            response = self.session.post(
                full_url,
                files=file,
                params=params,
                headers={"Accept": None, "Content-Type": None},
                verify=self.configs["secure"],
            )
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        except requests.exceptions.RequestException as exc:
            # Handle the exception here, e.g., log the error or raise a custom exception
            logging.error(f"Failed to post file to {full_url}: {exc}")
            raise  # Re-raise the exception

        return response

    def patch_req_dina(self, full_url: str, json_data: dict, params: dict = None):
        """Base method for a PATCH request to DINA.

        Args:
                full_url (str): The full URL for the API request (extension of the base_url).
                json_data (dict): JSON data to be sent in the request body.
                params (dict, optional): Query parameters for the request (default: None).

        Returns:
                requests.Response: The response object containing the API response.

        Raises:
                requests.exceptions.RequestException: If there is an error during the HTTP request.

        """
        self.refresh_token()
        try:
            response = self.session.patch(full_url, json=json_data, params=params)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        except requests.exceptions.RequestException as exc:
            # Handle the exception here, e.g., log the error or raise a custom exception
            logging.error(f"Failed to perform PATCH request to {full_url}: {exc}")
            raise  # Re-raise the exception

        return response

    def bulk_update_req_dina(self, full_url:str, json_data: dict):
        """Base method for a Bulk update PATCH request to DINA.

        Args:
                full_url (str): The full URL for the API request (extension of the base_url).
                json_data (dict): JSON data to be sent in the request body.

        Returns:
                requests.Response: The response object containing the API response.

        Raises:
                requests.exceptions.RequestException: If there is an error during the HTTP request.

        """
        self.refresh_token()
        self.session.headers.update(
        {
            "Accept": "application/vnd.api+json; ext=bulk",
            "Content-Type": "application/vnd.api+json; ext=bulk",
            "Authorization": f"bearer {DinaAPI.token['access_token']}",
        }
        )
        try:
            response = self.session.patch(full_url + BULK_POST_ENDPOINT_URL, json=json_data,
                headers=self.session.headers,
                verify=self.configs["secure"],)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        except requests.exceptions.RequestException as exc:
            # Handle the exception here, e.g., log the error or raise a custom exception
            logging.error(f"Failed to perform PATCH request to {full_url}: {exc}")
            raise  # Re-raise the exception

        return response
    def delete_req_dina(self, full_url: str, params: dict = None):
        """Base method for a DELETE request to DINA.

        Args:
                full_url (str): The full URL for the API request (extension of the base_url).
                params (dict, optional): Query parameters for the request (default: None).

        Returns:
                requests.Response: The response object containing the API response.

        Raises:
                requests.exceptions.RequestException: If there is an error during the HTTP request.

        """
        self.refresh_token()
        try:
            response = self.session.delete(full_url, params=params)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        except requests.exceptions.RequestException as exc:
            # Handle the exception here, e.g., log the error or raise a custom exception
            logging.error(f"Failed to delete data from {full_url}: {exc}")
            raise  # Re-raise the exception

        return response