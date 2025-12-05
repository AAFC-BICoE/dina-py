# tests/test_ena/test_invalid_payloads_json.py
from pathlib import Path
from lxml import etree
from dinapy.ena.xml import render_submission_xml, render_project_xml, _schema_from,render_sample_xml, XSD_DIR

def _validate_string(xml_text: str, xsd_path: Path):
    try:
        doc = etree.XML(xml_text.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        return False, f"XML parse error: {e}"
    try:
        schema = _schema_from(xsd_path)
        schema.assertValid(doc)
        return True, "ok"
    except Exception as e:
        return False, str(e)

def test_invalid_submission_and_sample_jsons_are_caught():
    cases = []

    # Base-ish submission example (simplified) — will mutate per case
    base_submission = {
        "submission": {
            "alias": "submissionAliasName",
            "accession": "",
            # actions list will be replaced per-case
        }
    }

    # Case A: HOLD with three-digit day (typo) -> invalid xs:date lexical format
    s_a = dict(base_submission)
    s_a["submission"] = dict(base_submission["submission"])
    s_a["submission"]["actions"] = [{"type": "HOLD", "holdUntilDate": "2025-12-004"}]
    xml_a = render_submission_xml(s_a)
    cases.append(("submission: HOLD three-digit day (bad lexical date)", xml_a, XSD_DIR / "SRA.submission.xsd"))

    # Case B: HOLD with non-existent Feb 29 on non-leap year -> invalid date
    s_b = dict(base_submission)
    s_b["submission"] = dict(base_submission["submission"])
    s_b["submission"]["actions"] = [{"type": "HOLD", "holdUntilDate": "2025-02-29"}]
    xml_b = render_submission_xml(s_b)
    cases.append(("submission: HOLD non-leap Feb 29 (invalid date)", xml_b, XSD_DIR / "SRA.submission.xsd"))

    # Case C: Unknown action type -> produces <ACTION></ACTION> (no required child)
    s_c = dict(base_submission)
    s_c["submission"] = dict(base_submission["submission"])
    s_c["submission"]["actions"] = [{"type": "FOO"}]
    xml_c = render_submission_xml(s_c)
    cases.append(("submission: ACTION with no child (unknown type)", xml_c, XSD_DIR / "SRA.submission.xsd"))

    # Sample-level invalid cases (use helper to produce SAMPLE_SET XML)
    # Case D: SAMPLE missing TAXON_ID
    sample_d = {"alias": "s_no_taxon", "organism": {}}
    xml_d = render_sample_xml(sample_d)
    cases.append(("sample: missing TAXON_ID", xml_d, XSD_DIR / "SRA.sample.xsd"))

    # Case E: SAMPLE TAXON_ID not integer
    sample_e = {"alias": "s_taxon_str", "sample_name": {"taxonId": "abc", "scientific_name": "Test species"}}
    xml_e = render_sample_xml(sample_e)
    cases.append(("sample: TAXON_ID not integer", xml_e, XSD_DIR / "SRA.sample.xsd"))

    # Case F: SAMPLE_ATTRIBUTES present but empty (minOccurs=1 for SAMPLE_ATTRIBUTE)
    sample_f = {"alias": "s_empty_attrs", "sample_name": {"taxonId": 9606}, "attributes": []}
    xml_f = render_sample_xml(sample_f)
    cases.append(("sample: SAMPLE_ATTRIBUTES present but empty", xml_f, XSD_DIR / "SRA.sample.xsd"))

    # Run validations: each case is expected to FAIL
    passed_unexpected = []
    for name, xml_text, xsd_path in cases:
        ok, msg = _validate_string(xml_text, xsd_path)
        if ok:
            passed_unexpected.append((name, "unexpectedly passed"))
        else:
            # good: test harness prints the validator message for debugging
            print(f"Case '{name}' correctly failed validation: {msg}")

    assert not passed_unexpected, f"The following invalid JSON cases unexpectedly passed: {passed_unexpected}"