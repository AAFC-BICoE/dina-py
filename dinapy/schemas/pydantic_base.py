"""
Base Pydantic models for JSON API serialization/deserialization.

The JSON API wire format looks like:
  {
    "data": {
      "id": "...",
      "type": "collecting-event",
      "attributes": { ... },
      "relationships": { ... }
    }
  }

These generics handle that envelope so each resource only needs to define
its own attributes model.
"""
from __future__ import annotations
from typing import Generic, TypeVar, Any
from pydantic import BaseModel, ConfigDict


class RelationshipLinkage(BaseModel):
    """Single resource linkage: {"type": "person", "id": "..."}"""
    type: str
    id: str


class RelationshipData(BaseModel):
    """A relationship block containing either a single or list linkage."""
    data: RelationshipLinkage | list[RelationshipLinkage] | None = None


AttributesT = TypeVar("AttributesT")


class JsonApiData(BaseModel, Generic[AttributesT]):
    id: str | None = None
    type: str
    attributes: AttributesT
    relationships: dict[str, RelationshipData] | None = None


class JsonApiDocument(BaseModel, Generic[AttributesT]):
    data: JsonApiData[AttributesT]

    @classmethod
    def deserialize(cls, response: dict) -> "JsonApiDocument[AttributesT]":
        """Deserialize a raw API response dict.

        - Null attribute values are stripped before model construction so they
          are never counted as "set" in model_fields_set.  This prevents an
          accidental round-trip from NULLing fields in a PATCH request.
        - Relationships with no data (links-only) are dropped for the same
          reason — they carry no actionable data for a client library.

        To intentionally clear a field on PATCH, pass the field as an explicit
        keyword argument (e.g. ``usageType=None``) when constructing the
        attributes model directly — that marks it as set in model_fields_set
        and serialize() will include it as null.
        """
        raw = dict(response)
        if "data" in raw:
            raw["data"] = dict(raw["data"])
            # Strip null attribute values so they are never in model_fields_set.
            if isinstance(raw["data"].get("attributes"), dict):
                raw["data"]["attributes"] = {
                    k: v for k, v in raw["data"]["attributes"].items()
                    if v is not None
                }
            # Strip links-only relationships.
            if isinstance(raw["data"].get("relationships"), dict):
                raw["data"]["relationships"] = {
                    k: v for k, v in raw["data"]["relationships"].items()
                    if v.get("data") is not None
                } or None
        return cls.model_validate(raw)

    def serialize(self) -> dict:
        """
        Serialize to a JSON API request payload.
        Uses exclude_unset=True so only explicitly set attributes are included
        """
        data = self.data.model_dump(exclude_unset=True, mode="json")
        # Always include type
        data["type"] = self.data.type
        # Strip relationships with no data (links-only from GET response) and
        # null relationships — only relationships with explicit data belong in a request
        if "relationships" in data:
            if data["relationships"] is None:
                del data["relationships"]
            else:
                data["relationships"] = {
                    k: v for k, v in data["relationships"].items()
                    if v.get("data") is not None
                }
                if not data["relationships"]:
                    del data["relationships"]
        return {"data": data}
