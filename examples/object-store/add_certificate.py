import os
from pdb import main
import subprocess
import certifi
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path

def main():
    # Load .env file from the same directory as the notebook

    load_dotenv()

    # Ensure KEYCLOAK_URL is set
    keycloak_url = os.environ.get("KEYCLOAK_URL")
    print(f"KEYCLOAK_URL: {keycloak_url}")
    if not keycloak_url:
        raise ValueError("KEYCLOAK_URL environment variable is not set.")

    # Extract hostname from URL
    parsed_url = urlparse(keycloak_url)
    hostname = parsed_url.hostname

    if not hostname:
        raise ValueError("Invalid KEYCLOAK_URL format.")

    # Define file paths
    certs_txt = "certs.txt"
    combined_cert = "combined-cert.crt"
    certifi_path = certifi.where()

    # Run openssl to get the certificate and extract it using awk
    subprocess.run(f"openssl s_client -connect {hostname}:443 -showcerts < /dev/null > {certs_txt}", shell=True, check=True)
    subprocess.run(f"awk '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/' {certs_txt} > {combined_cert}", shell=True, check=True)

    # Append the certificate to certifi's CA bundle
    with open(certifi_path, "ab") as ca_bundle, open(combined_cert, "rb") as new_cert:
        ca_bundle.write(b"\n")
        ca_bundle.write(new_cert.read())

    print(f"✅ Certificate from {hostname} added to certifi store at {certifi_path}.")
if __name__ == "__main__":
    main()
