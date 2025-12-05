
# dinapy/ena/xml.py
from __future__ import annotations
from pathlib import Path
from typing import Tuple
from jinja2 import Environment, FileSystemLoader, select_autoescape
from lxml import etree

TEMPLATES_DIR = Path(__file__).parent / "xml_templates"
XSD_DIR = Path(__file__).parent / "xsd"

# ---------- Jinja2 renderers ----------
_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["xml"])
)
def render_sample_xml(sample: dict) -> str:
    """
    Render a SAMPLE (wrapped in SAMPLE_SET) from a sample-like dict using the
    Jinja2 template `xml_templates/sample.xml.j2`.
    """
    tpl = _env.get_template("sample.xml.j2")
    return tpl.render(sample=sample)

def render_project_xml(project: dict) -> str:
    tpl = _env.get_template("project.xml.j2")
    return tpl.render(project=project)

def render_submission_xml(submission: dict) -> str:
    tpl = _env.get_template("submission.xml.j2")
    return tpl.render(submission=submission)

# ---------- lxml XSD import resolver ----------
class LocalXsdResolver(etree.Resolver):
    """Resolve imported XSDs (e.g., SRA.common.xsd) from our local xsd dir."""
    def resolve(self, url, pubid, context):
        # Try filename in local xsd directory
        candidate = XSD_DIR / Path(url).name
        if candidate.exists():
            return self.resolve_filename(str(candidate), context)
        # Try exact relative path under xsd dir
        candidate2 = (XSD_DIR / url)
        if candidate2.exists():
            return self.resolve_filename(str(candidate2), context)
        return None

def _schema_from(xsd_path: Path) -> etree.XMLSchema:
    parser = etree.XMLParser()
    parser.resolvers.add(LocalXsdResolver())
    # parse the schema with resolver; base_url helps for relative imports
    schema_doc = etree.parse(str(xsd_path), parser)
    return etree.XMLSchema(schema_doc)

def validate_xml(xml_text: str, xsd_path: Path) -> Tuple[bool, str]:
    xml_doc = etree.XML(xml_text.encode("utf-8"))
    try:
        schema = _schema_from(xsd_path)
        schema.assertValid(xml_doc)
        return True, "ok"
    except etree.DocumentInvalid as e:
        return False, str(e)
    except etree.XMLSchemaParseError as e:
        return False, f"XSD parse error: {e}"

def validate_xml_with_children(xml_text: str,
                               main_xsd_path: Path,
                               child_xsd_map: Dict[str, Path]) -> Tuple[bool, str]:
    """
    Validate `xml_text` against `main_xsd_path`, then validate each child element
    named in `child_xsd_map` against its respective XSD.

    - child_xsd_map: mapping of element local-name -> Path to XSD.
      Example: {'SAMPLE': XSD_DIR / 'SRA.sample.xsd'}
    """
    try:
        xml_doc = etree.XML(xml_text.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        return False, f"XML parse error: {e}"

    # Validate root submission against main schema
    try:
        main_schema = _schema_from(main_xsd_path)
        main_schema.assertValid(xml_doc)
    except etree.DocumentInvalid as e:
        return False, f"Submission invalid: {e}"
    except etree.XMLSchemaParseError as e:
        return False, f"Main XSD parse error: {e}"

    # Validate each child element type against its XSD
    for elem_local_name, child_xsd_path in child_xsd_map.items():
        try:
            child_schema = _schema_from(child_xsd_path)
        except etree.XMLSchemaParseError as e:
            return False, f"Child XSD parse error for {child_xsd_path}: {e}"

        # Use local-name() in XPath to be robust against namespaces
        nodes = xml_doc.xpath(f"//*[local-name() = '{elem_local_name}']")

        for i, node in enumerate(nodes, start=1):
            # wrap node in an ElementTree to give it a document root for validation
            node_tree = etree.ElementTree(node)
            try:
                child_schema.assertValid(node_tree)
            except etree.DocumentInvalid as e:
                # Include context: which element failed
                return False, f"Child element validation failed for {elem_local_name}[{i}]: {e}"

    return True, "ok"
