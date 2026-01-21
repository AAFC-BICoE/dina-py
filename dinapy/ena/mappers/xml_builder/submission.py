from typing import Optional
from lxml import etree

def build_submission_xml_from_model(submission_alias: str, center_name: Optional[str] = None,
                         action: str = "ADD") -> str:
    """
    Build a minimal SUBMISSION_SET XML for actions like ADD, MODIFY, VALIDATE, etc.

    action: "ADD", "MODIFY", "RELEASE", "VALIDATE", ...
    """
    sub_set = etree.Element("SUBMISSION_SET")
    attrs = {"alias": submission_alias}
    if center_name:
        attrs["center_name"] = center_name
    sub_el = etree.SubElement(sub_set, "SUBMISSION", **attrs)

    actions_el = etree.SubElement(sub_el, "ACTIONS")
    action_el = etree.SubElement(actions_el, "ACTION")
    etree.SubElement(action_el, action.upper())

    return etree.tostring(
        sub_set,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True
    ).decode("utf-8")