
from pathlib import Path
from lxml import etree
from dinapy.ena.xml import render_project_xml, render_submission_xml, validate_xml, validate_xml_with_children, _schema_from, XSD_DIR

def test_xsd_imports_resolve():
    # Ensure the resolver can parse the main project schema with its imports
    schema = _schema_from(XSD_DIR / "ENA.project.xsd")
    assert isinstance(schema, etree.XMLSchema)

def test_project_xml_xsd_valid():
    project = {
        "alias": "p1",
        "title": "t",
        "description": "d",
        "project_links": []
    }
    xml = render_project_xml(project)
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
    xml = render_submission_xml(submission)
    # If you’ve vendored ENA.submission.xsd, swap the path below appropriately.
    ok, msg = validate_xml_with_children(xml, XSD_DIR / "SRA.submission.xsd", {'PROJECT': XSD_DIR / "ENA.project.xsd", 'SAMPLE':  XSD_DIR / "SRA.sample.xsd"})  # schema for demo purposes
    assert ok, msg
