
# webin_api.py
# ENA Webin v2 base client (Basic Auth) – drop-in replacement for your DINA API base class.

import os
import logging
import json
from typing import Any, Dict, Optional, Union

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Import receipt parsing utilities
from dinapy.ena.receipt import parse_receipt_xml, format_receipt_summary, ENAReceipt

# ---- Defaults ----
# Use test=True for the nightly-reset dev environment (wwwdev), production otherwise.
# Base URL points at Webin v2; some classic programmatic XML submissions use the drop-box "submit" endpoint.
WEBIN_V2_BASE_PROD = "https://www.ebi.ac.uk/ena/submit/webin-v2"
WEBIN_V2_BASE_TEST = "https://wwwdev.ebi.ac.uk/ena/submit/webin-v2"
DROPBOX_SUBMIT_PROD = "https://www.ebi.ac.uk/ena/submit/drop-box/submit/"
DROPBOX_SUBMIT_TEST = "https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/"

class WebinAPI:
    """
    ENA Webin REST v2 base client using HTTP Basic Auth.

    Environment variables (optional):
      WEBIN_USERNAME, WEBIN_PASSWORD, WEBIN_TEST (true/false),
      WEBIN_BASE_URL (override), SECURE (true/false)
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: Optional[str] = None,
        test: Optional[bool] = None,
        verify_tls: Optional[bool] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        timeout: int = 60,
    ):
        # Load .env if present (works in notebooks and scripts)
        load_dotenv()

        # Logging similar to your original
        logging.basicConfig(level=logging.INFO)
        logging.captureWarnings(True)

        # Resolve config from params or env
        self.username = username or os.getenv("WEBIN_USERNAME")
        self.password = password or os.getenv("WEBIN_PASSWORD")

        if self.username is None or self.password is None:
            raise ValueError(
                "WEBIN_USERNAME and WEBIN_PASSWORD are required. "
                "Please provide them as arguments or set them in environment variables/.env file."
            )

        if test is None:
            test_env = os.getenv("WEBIN_TEST", "").strip().lower()
            test = test_env in ("1", "true", "yes", "on")

        if base_url:
            self.base_url = base_url.rstrip("/")
        else:
            self.base_url = WEBIN_V2_BASE_TEST if test else WEBIN_V2_BASE_PROD

        if verify_tls is None:
            verify_tls_env = os.getenv("SECURE", "").strip().lower()
            verify_tls = verify_tls_env in ("", "1", "true", "yes", "on")  # default True

        self.verify_tls = verify_tls
        self.timeout = timeout

        # Prepare session with Basic Auth
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(self.username, self.password)

        # Set default JSON headers (override per request as needed)
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "webin-api-client/1.0 (+https://www.ebi.ac.uk/ena/submit/webin-v2/swagger-ui/index.html)"
        })
        if extra_headers:
            self.session.headers.update(extra_headers)

        logging.info("WebinAPI initialized (base_url=%s, test=%s, verify_tls=%s)",
                     self.base_url, test, self.verify_tls)

    # ---------------------- Internal helpers ----------------------

    def _url(self, path: str) -> str:
        """Join base_url with relative path, keeping trailing slashes if provided."""
        if not path:
            raise ValueError("path must be non-empty.")
        # Allow callers to pass absolute URLs (e.g., drop-box submit)
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _handle(self, resp: requests.Response) -> requests.Response:
        """Raise for 4xx/5xx and log details."""
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            content_preview = None
            try:
                content_preview = resp.text[:1024]
            except Exception:
                content_preview = "<unavailable>"
            logging.error("HTTP %s for %s: %s", resp.status_code, resp.url, content_preview)
            raise
        return resp

    # ---------------------- Generic verbs ----------------------

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, stream: bool = False) -> requests.Response:
        resp = self.session.get(self._url(path), params=params, timeout=self.timeout,
                                verify=self.verify_tls, stream=stream)
        return self._handle(resp)

    def delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        resp = self.session.delete(self._url(path), params=params, timeout=self.timeout,
                                   verify=self.verify_tls)
        return self._handle(resp)

    def post_json(self, path: str, payload: Union[Dict[str, Any], list]) -> requests.Response:
        # Ensure JSON header for this call
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        resp = self.session.post(self._url(path), headers=headers, json=payload,
                                 timeout=self.timeout, verify=self.verify_tls)
        return self._handle(resp)

    def put_json(self, path: str, payload: Union[Dict[str, Any], list]) -> requests.Response:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        resp = self.session.put(self._url(path), headers=headers, json=payload,
                                 timeout=self.timeout, verify=self.verify_tls)
        return self._handle(resp)

    def patch_json(self, path: str, payload: Union[Dict[str, Any], list]) -> requests.Response:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        resp = self.session.patch(self._url(path), headers=headers, json=payload,
                                  timeout=self.timeout, verify=self.verify_tls)
        return self._handle(resp)

    def post_xml(self, path_or_full_url: str, xml_string: str) -> requests.Response:
        # Some programmatic submissions still use XML (e.g., drop-box submit)
        headers = {"Accept": "application/xml", "Content-Type": "application/xml"}
        resp = self.session.post(self._url(path_or_full_url), headers=headers, data=xml_string,
                                 timeout=self.timeout, verify=self.verify_tls)
        return self._handle(resp)

    def post_multipart(self, path: str, files: Dict[str, Any], data: Optional[Dict[str, Any]] = None) -> requests.Response:
        # Rarely used in ENA; actual read file uploads are via FTP/Aspera.
        # Use with caution; check Swagger for the exact endpoint requirements.
        headers = {"Accept": "application/json"}  # let requests set Content-Type boundary
        resp = self.session.post(self._url(path), headers=headers, files=files, data=data or {},
                                 timeout=self.timeout, verify=self.verify_tls)
        return self._handle(resp)

    # ---------------------- Convenience helpers ----------------------

    def call(self, method: str, path: str, **kwargs) -> requests.Response:
        """Single entry point if you prefer dynamic calls: method in {'GET','POST','PUT','PATCH','DELETE'}."""
        method = method.upper().strip()
        if method == "GET":
            return self.get(path, params=kwargs.get("params"), stream=kwargs.get("stream", False))
        elif method == "POST":
            if "json" in kwargs:
                return self.post_json(path, kwargs["json"])
            elif "xml" in kwargs:
                return self.post_xml(path, kwargs["xml"])
            else:
                return self.post_multipart(path, kwargs.get("files", {}), kwargs.get("data"))
        elif method == "PUT":
            return self.put_json(path, kwargs["json"])
        elif method == "PATCH":
            return self.patch_json(path, kwargs["json"])
        elif method == "DELETE":
            return self.delete(path, params=kwargs.get("params"))
        else:
            raise ValueError(f"Unsupported method: {method}")

    def submit_xml(
            self,
            submission_xml: str,
            experiment_xml: Optional[str] = None,
            run_xml: Optional[str] = None,
            test: Optional[bool] = None,
        ) -> requests.Response:
            """
            Submit SUBMISSION + EXPERIMENT and/or RUN XML to the drop-box endpoint
            using multipart/form-data, equivalent to:

            curl -u user:pass \\
                -F "SUBMISSION=@submission.xml" \\
                [-F "EXPERIMENT=@experiment.xml"] \\
                [-F "RUN=@run.xml"] \\
                https://www[dev].ebi.ac.uk/ena/submit/drop-box/submit/

            You must provide at least one of experiment_xml or run_xml.
            """
            if experiment_xml is None and run_xml is None:
                raise ValueError("You must provide at least experiment_xml or run_xml.")

            if test is None:
                test_env = os.getenv("WEBIN_TEST", "").strip().lower()
                test = test_env in ("1", "true", "yes", "on")

            submit_url = DROPBOX_SUBMIT_TEST if test else DROPBOX_SUBMIT_PROD

            files = {
                "SUBMISSION": ("submission.xml", submission_xml, "application/xml"),
            }
            if experiment_xml is not None:
                files["EXPERIMENT"] = ("experiment.xml", experiment_xml, "application/xml")
            if run_xml is not None:
                files["RUN"] = ("run.xml", run_xml, "application/xml")

            headers = {"Accept": "application/xml"}  # let requests set multipart boundary

            resp = self.session.post(
                submit_url,
                headers=headers,
                files=files,
                timeout=self.timeout,
                verify=self.verify_tls,
            )
            return self._handle(resp)

    def submit_webin_xml(
            self,
            submission_xml: str,
            project_xml: Optional[str] = None,
            sample_xml: Optional[str] = None,
            experiment_xml: Optional[str] = None,
            run_xml: Optional[str] = None,
            extra_sections: Optional[str] = None,
            path: str = "/metadata",
        ) -> requests.Response:
            """
            Submit a single Webin v2 XML document of the form:

            <WEBIN>
                <SUBMISSION>...</SUBMISSION>
                [<PROJECT_SET>...</PROJECT_SET>]
                [<SAMPLE_SET>...</SAMPLE_SET>]
                [<EXPERIMENT_SET>...</EXPERIMENT_SET>]
                [<RUN_SET>...</RUN_SET>]
                ...
            </WEBIN>

            to the Webin v2 XML endpoint (relative `path` under base_url).
            """
            # Build inner XML sections
            parts = [submission_xml]
            if project_xml:
                parts.append(project_xml)
            if sample_xml:
                parts.append(sample_xml)
            if experiment_xml:
                parts.append(experiment_xml)
            if run_xml:
                parts.append(run_xml)
            if extra_sections:
                parts.append(extra_sections)

            # Strip XML declarations from inner fragments if present
            def strip_decl(x: str) -> str:
                x = x.lstrip()
                if x.startswith("<?xml"):
                    return x.split("?>", 1)[1].lstrip()
                return x

            inner = "\n".join(strip_decl(p) for p in parts if p)

            webin_xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<WEBIN>\n{inner}\n</WEBIN>\n'

            # Now send as a single XML body to Webin v2
            return self.post_xml(self._url(path), webin_xml)

    # ---------------------- Receipt parsing helpers ----------------------
    
    def parse_receipt(self, response: requests.Response) -> ENAReceipt:
        """
        Parse an ENA receipt XML response into a structured ENAReceipt object.
        
        Args:
            response: requests.Response object containing XML receipt
            
        Returns:
            ENAReceipt object with parsed accessions, messages, etc.
            
        Example:
            >>> resp = client.submit_xml(submission_xml, experiment_xml=exp_xml)
            >>> receipt = client.parse_receipt(resp)
            >>> if receipt.success:
            ...     print(f"Experiment accession: {receipt.get_accession('EXPERIMENT')}")
            >>> else:
            ...     print(f"Errors: {receipt.get_errors()}")
        """
        receipt = parse_receipt_xml(response.text)
        receipt.raw_text = response.text
        return receipt
    
    def get_receipt_summary(self, response: requests.Response) -> str:
        """
        Get a human-readable summary of an ENA receipt response.
        
        Args:
            response: requests.Response object containing XML receipt
            
        Returns:
            Formatted string summary
            
        Example:
            >>> resp = client.submit_xml(submission_xml, run_xml=run_xml)
            >>> print(client.get_receipt_summary(resp))
        """
        receipt = self.parse_receipt(response)
        return format_receipt_summary(receipt)