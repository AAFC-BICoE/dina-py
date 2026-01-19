
from pathlib import Path
from lxml import etree
import warnings

from dinapy.ena.xml import validate_xml, validate_xml_with_children, _schema_from, XSD_DIR
from dinapy.ena.models import Project, Sample, Organism, Attribute
from dinapy.ena.mappers.xml_builder.project import build_project_xml_from_model
from dinapy.ena.mappers.xml_builder.sample import build_sample_xml_from_model
from dinapy.ena.mappers.xml_builder.submission import build_submission_xml_from_model

# Suppress deprecation warnings in tests
warnings.filterwarnings("ignore", category=DeprecationWarning)

def test_xsd_imports_resolve():
    # Ensure the resolver can parse the main project schema with its imports
    schema = _schema_from(XSD_DIR / "ENA.project.xsd")
    assert isinstance(schema, etree.XMLSchema)

def test_project_xml_xsd_valid():
    """Test that Project Pydantic model generates valid XML."""
    project = Project(
        alias="p1",
        title="Test Project",
        description="Test project description"
    )
    xml = build_project_xml_from_model(project)
    ok, msg = validate_xml(xml, XSD_DIR / "ENA.project.xsd")
    assert ok, msg

def test_submission_xml_xsd_valid():
    submission = {
        "submission": {
        "alias": "submissionAliasName",
        "accession": "",
        "actions": [
            {
                    "type": "ADD"
            },
            {
                    "type": "HOLD",
                    "holdUntilDate": "2025-12-4"
                }
            ],
            "attributes": [
                {
                    "tag": "test_tag",
                    "value": "test_val"
                },
                {
                    "tag": "test_tag_1",
                    "value": "test_val_1"
                }
            ]
        },
        "projects": [
            {
                "alias": "comparative-analysis",
                "name": "Human Gut Microbiota Study",
                "title": "Exploration of the diversity human gastric microbiota",
                "description": "The genome sequences of gut microbes were obtained using...",
                "sequencingProject": {},
                "attributes": [
                    {
                        "tag": "testTag",
                        "value": "testValue"
                    }
                ],
                "project_links": [
                    {
                        "xrefLink": {
                            "db": "PUBMED",
                            "id": "25035323"
                        }
                    }
                ]
            }
        ],
        "samples": [
            {
                "alias": "stomach_microbiota",
                "title": "human gastric microbiota, mucosal",
                "organism": {
                    "taxonId": "1284369"
                },
                "attributes": [
                    {
                        "tag": "investigation type",
                        "value": "mimarks-survey"
                    },
                    {
                        "tag": "sequencing method",
                        "value": "pyrosequencing"
                    },
                    {
                        "tag": "broad-scale environmental context",
                        "value": "test"
                    },
                    {
                        "tag": "local environmental context",
                        "value": "test"
                    },
                    {
                        "tag": "environmental medium",
                        "value": "test"
                    },
                    {
                        "tag": "host body site",
                        "value": "Mucosa of stomach"
                    },
                    {
                        "tag": "human-associated environmental package",
                        "value": "human-associated"
                    },
                    {
                        "tag": "geographic location (latitude)",
                        "value": "1.81",
                        "unit": "DD"
                    },
                    {
                        "tag": "geographic location (longitude)",
                        "value": "-78.76",
                        "unit": "DD"
                    },
                    {
                        "tag": "geographic location (country and/or sea)",
                        "value": "Colombia"
                    },
                    {
                        "tag": "geographic location (region and locality)",
                        "value": "Tumaco"
                    },
                    {
                        "tag": "environment (biome)",
                        "value": "coast"
                    },
                    {
                    "tag": "environment (feature)",
                    "value": "human-associated habitat"
                    },
                    {
                        "tag": "project name",
                        "value": "Human microbiota"
                    },
                    {
                        "tag": "environment (material)",
                        "value": "gastric biopsy"
                    },
                    {
                        "tag": "ena-checklist",
                        "value": "ERC000014"
                    }
                ]
            }
        ]
    }
    
    # Build XML using xml_builder functions
    submission_xml = build_submission_xml_from_model(
        submission_alias="submissionAliasName",
        center_name=None,
        action="ADD"
    )
    project = Project(
        alias="comparative-analysis",
        title="Exploration of the diversity human gastric microbiota",
        description="The genome sequences of gut microbes were obtained using..."
    )
    project_xml = build_project_xml_from_model(project)
    
    sample = Sample(
        alias="stomach_microbiota",
        title="human gastric microbiota, mucosal",
        organism=Organism(taxonId=1284369, scientificName="stomach metagenome"),
        attributes=[
            Attribute(tag="investigation type", value="mimarks-survey"),
            Attribute(tag="ena-checklist", value="ERC000014")
        ]
    )
    sample_xml = build_sample_xml_from_model(sample)
    
    # Validate individual components
    ok, msg = validate_xml(submission_xml, XSD_DIR / "SRA.submission.xsd")
    assert ok, f"Submission XML validation failed: {msg}"
    
    ok, msg = validate_xml(project_xml, XSD_DIR / "ENA.project.xsd")
    assert ok, f"Project XML validation failed: {msg}"
    
    ok, msg = validate_xml(sample_xml, XSD_DIR / "SRA.sample.xsd")
    assert ok, f"Sample XML validation failed: {msg}"
