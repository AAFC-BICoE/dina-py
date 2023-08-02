import os
import requests
import yaml
import logging

from keycloak import KeycloakOpenID

KEYCLOACK_CONFIG_PATH = "./keycloak-config.yml"
BASE_URL = "https://dina-dev2.biodiversity.agr.gc.ca/api/v1/"


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

    def __init__(self, config_path: str = None):
        """Creates basic web services based on the provided config path or a default path.

        If the config_path is not provided, the default KEYCLOACK_CONFIG_PATH will be used.

        Parameters:
            config_path (str, optional): Path to the YAML configuration file (default: None).

        """
        if config_path is None:
            config_path = KEYCLOACK_CONFIG_PATH

        self.configs = None
        self.token = None

        self.set_configs(config_path)
        self.set_token()

        self.session = requests.Session()
        self.set_req_header()

        # Base web API URL, to be extended in inherited classes
        self.base_url = BASE_URL

    def set_configs(self, config_path: str):
        """Loads config from YAML file and saves it to the 'configs' variable.

        Parameters:
            config_path (str): Path to the YAML configuration file.

        Raises:
            FileNotFoundError: If the config_path does not point to an existing file.
            yaml.YAMLError: If there is an error in reading or parsing the YAML file.

        """
        try:
            with open(config_path, "r") as config_file:
                self.configs = yaml.safe_load(config_file)
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {config_path}")
            raise
        except yaml.YAMLError as exc:
            logging.error("Error in configuration file. Cannot execute.")
            logging.error(exc)
            raise

    def set_token(self):
        """Creates a Keycloak token based on configurations and environment variables.

        The Keycloak token is retrieved and saved to the 'token' attribute.

        Raises:
            requests.exceptions.RequestException: If there is an error during the token retrieval.

        """
        keycloak_openid = KeycloakOpenID(
            server_url=self.configs["url"],
            client_id=self.configs["client_id"],
            realm_name=self.configs["realm_name"],
            verify=self.configs["secure"],
            client_secret_key=None,
        )

        try:
            self.token = keycloak_openid.token(
                os.environ.get("keycloak_username"),
                os.environ.get("keycloak_password"),
            )
        except KeyError as exc:
            logging.error("Could not retrieve credentials from env variables.")
            logging.error(exc)
            raise

    def set_req_header(self):
        """Sets the header for the session.

        The header includes the 'Accept', 'Content-Type', and 'Authorization' fields.
        Token must be set beforehand.

        """
        self.session.headers.update(
            {
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/vnd.api+json",
                "Authorization": f"bearer {self.token['access_token']}",
            }
        )

    def get_req_dina(self, full_url: str, params: dict = None) -> requests.Response:
        """Base method for a GET request to DINA.

        Args:
            full_url (str): The full URL for the API request (extension of the base_url).
            params (dict, optional): Query parameters for the request (default: None).

        Returns:
            requests.Response: The response object containing the API response.

        Raises:
            requests.exceptions.RequestException: If there is an error during the HTTP request.

        """
        try:
            response = self.session.get(full_url, params=params)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        except requests.exceptions.RequestException as exc:
            # Handle the exception here, e.g., log the error or raise a custom exception
            logging.error(f"Failed to fetch data from {full_url}: {exc}")
            raise  # Re-raise the exception

        return response.json()
