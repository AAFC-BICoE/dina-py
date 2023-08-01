"""Dina Web Services. Define basic dina module API calls."""

import os
import requests
import yaml
import logging

from keycloak import KeycloakOpenID

KEYCLOACK_CONFIG_PATH = "./keycloak-config.yml"


class DinaAPI:
    """Base class containing basic API calls, to be inherited by other classes."""

    def __init__(self, config_path: str = None) -> None:
        """Creates basic web services based on config path provided.
        Will use a default path if not provided.
        """
        if config_path == None:
            config_path = KEYCLOACK_CONFIG_PATH

        self.configs = None  # contains configuration information
        self.token = None  # keycloak token

        self.set_configs(config_path)
        self.set_token()

        self.req_header = None  # contains request header for accessing DINA
        self.set_req_header()

        # Base web API URL, to be extended in inherited classes
        self.base_url = "https//dina-dev2.biodiversity.agr.gc.ca/api/"

    def set_configs(self, config_path: str) -> None:
        """Loads config from YAML file and saves it to configs variable."""
        try:
            config_file = open(config_path, "r")
            config_yml = yaml.safe_load(config_file)
            config_file.close
        except yaml.YAMLError as exc:
            logging.error("Error in configuration file. Cannot execute.")
            logging.error(exc)

        self.configs = config_yml

    def set_token(self) -> None:
        """Creates a keycloak token based on configs and env variables and
        saves it to token variable."""
        keycloak_openid = KeycloakOpenID(
            server_url=self.configs["url"],
            client_id=self.configs["client_id"],
            realm_name=self.configs["realm_name"],
            verify=self.configs["secure"],
            client_secret_key=None,
        )

        try:
            self.token = keycloak_openid.token(
                os.environ["keycloak_username"], os.environ["keycloak_password"]
            )
        except KeyError as exc:
            logging.error("Could not retrieve credentials from env variables.")
            logging.error(exc)

    def set_req_header(self) -> None:
        """Creates request header based on current token and saves it to
        req_header variable."""
        self.req_header = {
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
            "Authorization": "bearer {}".format(self.token["access_token"]),
        }

    def get_req_dina(self, full_url: str, params: dict = None) -> requests.Response:
        """Base method for a GET request to DINA. The full_url should be
        an extension of the base_url."""
        return requests.get(full_url, headers=self.req_header, params=params)
