# ENA Submission Tests

This directory contains comprehensive tests for the ENA (European Nucleotide Archive) submission functionality.

## Test Files

### `test_sample_models.py`
**17 tests** covering ENA Pydantic models:

#### Organism Model Tests (3 tests)
- Basic organism creation
- Full organism with all fields
- JSON serialization with camelCase aliases

#### Attribute Model Tests (4 tests)
- Basic attribute creation
- Attributes with units (e.g., geographic coordinates)
- JSON serialization
- Unit preservation in serialization

#### Sample Model Tests (5 tests)
- Minimal sample creation
- Complete sample with all fields
- JSON format validation
- ENA API format compliance
- Full submission payload structure

#### Validation Tests (5 tests)
- Required field validation (alias, organism, attributes)
- Organism taxon_id requirement
- Attribute tag and value requirements

### `test_submission_workflow.py`
**12 tests** covering the submission workflow:

#### Workflow Initialization (2 tests)
- Basic initialization with credentials
- Environment variable configuration

#### Project Submission (2 tests)
- Successful project submission
- Custom submission alias

#### Sample Submission (2 tests)
- Successful sample submission
- JSON format verification (organism/attributes structure)

#### Experiment Submission (1 test)
- XML API usage verification

#### Run Submission (1 test)
- XML API usage with file references

#### Combined Submission (1 test)
- Project + Sample + Experiment together

#### File Upload (1 test)
- Read file FTP upload

#### Response Parsing (2 tests)
- JSON response parsing
- Error handling

### `test_models.py`
**3 tests** for XML generation and validation:
- XSD import resolution
- Project XML validation
- Submission XML validation

### `test_invalid_payloads.py`
**1 test** for validation:
- Pydantic model validation (invalid cases prevented at model creation)

## Running Tests

### Run all ENA tests:
```bash
pytest tests/test_ena/ -v
```

### Run specific test files:
```bash
# Sample models
pytest tests/test_ena/test_sample_models.py -v

# Submission workflow
pytest tests/test_ena/test_submission_workflow.py -v

# XML validation
pytest tests/test_ena/test_models.py -v
```

### Run with coverage:
```bash
pytest tests/test_ena/ --cov=dinapy.ena --cov-report=html
```

## Test Coverage Summary

✅ **29 tests** for new ENA submission functionality:
- Organism, Attribute, and Sample models
- JSON serialization and format validation
- Submission workflow with mocked API calls
- Project, Sample, Experiment, and Run submissions
- Combined submissions
- File upload functionality
- Response parsing

## Key Testing Features

1. **Pydantic Model Validation**: Tests verify that models enforce required fields and data types
2. **JSON Format Compliance**: Ensures output matches ENA Webin API v2 expected format
3. **Mocked API Calls**: Workflow tests use mocks to avoid real network calls
4. **XML Validation**: Verifies generated XML against ENA XSD schemas
5. **Comprehensive Coverage**: Tests both success and failure scenarios

## Example Test Usage

```python
from dinapy.ena.models import Sample, Organism, Attribute

# Models are validated at creation time
sample = Sample(
    alias="test_sample",
    organism=Organism(taxon_id=9606),
    attributes=[
        Attribute(tag="collection date", value="2024-01-01")
    ]
)

# Serializes to correct JSON format
data = sample.model_dump(by_alias=True, exclude_none=True)
# Output: {"alias": "test_sample", "organism": {"taxonId": 9606}, "attributes": [...]}
```
