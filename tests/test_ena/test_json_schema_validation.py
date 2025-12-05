# tests/test_ena/test_json_schema_fast.py
import json
from pathlib import Path
from wsgiref.validate import validator
import pytest
from jsonschema import Draft202012Validator
import logging
log = logging.getLogger(__name__)

try:
    from fastjsonschema import compile as fj_compile, JsonSchemaException
except Exception:
    fj_compile = None
    JsonSchemaException = Exception  # fallback for typing in pytest.raises

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "dinapy" / "ena" / "schemas"
WEBIN_SCHEMA_PATH = SCHEMA_DIR / "schema_webin_v2_payload.json"

def _load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def webin_validator():
    schema = _load_schema(WEBIN_SCHEMA_PATH)

    # Try fastjsonschema first (returns a callable validator)
    if fj_compile is not None:
        try:
            validate = fj_compile(schema)           # callable
            exc = JsonSchemaException               # fastjsonschema exception class
            globals()['JsonSchemaException'] = exc
            return validate
        except Exception:
            # fall back to jsonschema if compile fails
            pass

    # Fallback to jsonschema Draft202012Validator: return its .validate method (callable)
    validator = Draft202012Validator(schema)
    log.info("Using Draft202012Validator for validation fallback")
    validate = validator.validate
    from jsonschema import ValidationError as JsonSchemaValidationError
    globals()['JsonSchemaException'] = JsonSchemaValidationError
    return validate

def test_valid_webin_payload_passes(webin_validator):
    payload = {
        "submission": {
            "alias": "submissionAliasName",
            "actions": [
                {"type": "ADD"},
                {"type": "HOLD", "holdUntilDate": "2025-12-04"}
            ],
        },
        "projects": [
            {
                "alias": "comparative-analysis",
                "title": "Exploration of the diversity human gastric microbiota",
                "description": "The genome sequences of gut microbes were obtained using...",
                "sequencingProject": {}
            }
        ],
        "samples": [
            {
                "alias": "stomach_microbiota",
                "title": "human gastric microbiota, mucosal",
                "organism": {"taxonId": 1284369},
                "attributes": [
                    {"tag": "investigation type", "value": "mimarks-survey"},
                    {"tag": "ena-checklist", "value": "ERC000014"},
                    {"tag": "broad-scale environmental context", "value": "test"},
                    {"tag": "local environmental context", "value": "test"},
                    {"tag": "environmental medium", "value": "test"}
                ]
            }
        ]
    }

    # Should not raise
    webin_validator(payload)

def test_invalid_hold_date_fails(webin_validator):
    payload = {
        "submission": {
            "alias": "bad_date",
            "actions": [
                {"type": "HOLD", "holdUntilDate": "2025-12-004"}  # invalid: day has 3 digits
            ]
        }
    }
    with pytest.raises(JsonSchemaException):
        webin_validator(payload)

def test_sample_missing_taxon_fails(webin_validator):
    payload = {
        "submission": {
            "alias": "s_missing_taxon",
            "actions": [{"type": "ADD"}]
        },
        "samples": [
            {
                "alias": "s_no_taxon",
                "title": "No taxon sample",
                "organism": {},  # missing taxonId
                "attributes": [{"tag": "foo", "value": "bar"}]
            }
        ]
    }
    with pytest.raises(JsonSchemaException):
        webin_validator(payload)