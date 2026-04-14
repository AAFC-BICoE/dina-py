"""DINA Search API client.

Wraps the Elasticsearch-backed search endpoint exposed by DINA's search-api
module.  The endpoint accepts a raw ES query body and returns matching
DINA entities from a given index.
"""

import logging
from dinapy.dinaapi import DinaAPI

logger = logging.getLogger(__name__)

# Fields returned for each material-sample hit
_MATERIAL_SAMPLE_SOURCE = {
    "includes": [
        "data.id",
        "data.type",
        "data.relationships",
        "data.attributes.materialSampleName",
        "included.attributes.determination",
        "included.attributes.isTarget",
        "included.id",
        "included.type",
    ]
}


class SearchAPI(DinaAPI):
    """Thin wrapper around the DINA search-api Elasticsearch endpoint."""

    def __init__(self, base_url: str = None) -> None:
        super().__init__(base_url=base_url)
        self.search_base_url = (
            base_url.rstrip("/") + "/search-api"
            if base_url
            else self.base_url.rstrip("/") + "/search-api"
        )

    def _post_search(self, index_name: str, query_body: dict) -> dict:
        """Execute a raw ES query against *index_name*.

        Uses the session already authenticated by the parent DinaAPI so that
        Keycloak tokens are automatically refreshed.

        Args:
            index_name: ES index name (e.g. "dina_material_sample_index").
            query_body:  Dict that will be serialised as the JSON request body.

        Returns:
            Parsed JSON response dict, or an empty dict on HTTP error.
        """
        url = f"{self.search_base_url}/search-ws/search"
        params = {"indexName": index_name}

        response = self.session.post(
            url,
            json=query_body,
            params=params,
            headers={"Content-Type": "application/json"},
        )

        if not response.ok:
            logger.error(
                "Search API request failed: %s %s", response.status_code, response.text
            )
            response.raise_for_status()

        return response.json()

    def search_material_samples_by_attachment(
        self,
        attachment_uuid: str,
        size: int = 25,
        from_: int = 0,
    ) -> dict:
        """Find material samples that reference *attachment_uuid*.

        Queries the ``dina_material_sample_index`` for records whose
        ``data.relationships.attachment.data.id`` matches the given UUID.

        Args:
            attachment_uuid: The object-store metadata UUID of the attachment.
            size:            Maximum number of hits to return (default 25).
            from_:           Pagination offset (default 0).

        Returns:
            Raw ES response dict with ``hits``, ``total``, etc.
            Returns an empty dict if the attachment UUID is falsy.
        """
        if not attachment_uuid:
            return {}

        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "data.relationships.attachment.data.id": attachment_uuid
                            }
                        }
                    ]
                }
            },
            "size": size,
            "from": from_,
            "_source": _MATERIAL_SAMPLE_SOURCE,
        }

        return self._post_search("dina_material_sample_index", query_body)

    def search_object_store_by_filename(
        self,
        filename_stem: str,
        size: int = 25,
    ) -> dict:
        """Find object-store metadata records whose originalFilename contains *filename_stem*.

        Uses a case-insensitive wildcard query so that full filenames like
        ``sample_R1.fastq.gz`` are matched by the stem ``sample``.

        Args:
            filename_stem: Substring to search for (no leading/trailing wildcards needed).
            size:          Maximum number of hits to return (default 25).

        Returns:
            Raw ES response dict with ``hits``, ``total``, etc.
        """
        if not filename_stem:
            return {}

        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "wildcard": {
                                "data.attributes.originalFilename.keyword": {
                                    "value": f"*{filename_stem}*",
                                    "case_insensitive": True,
                                }
                            }
                        }
                    ]
                }
            },
            "size": size,
            "_source": {
                "includes": [
                    "data.id",
                    "data.type",
                    "data.attributes.originalFilename",
                    "data.attributes.bucket",
                ]
            },
        }

        return self._post_search("dina_object_store_index", query_body)
