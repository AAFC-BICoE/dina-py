from lxml import etree
from dinapy.ena.models import Sample

def build_sample_xml_from_model(sample_model: Sample) -> str:
    """
    Build ENA SAMPLE_SET XML from a Sample Pydantic model.

    Maps:
      - Sample.alias   -> <SAMPLE alias="...">
      - Sample.title   -> <TITLE>
      - Sample.organism.* -> <SAMPLE_NAME> children
      - Sample.description -> (optional) added as a SAMPLE_ATTRIBUTE
      - Sample.attributes -> <SAMPLE_ATTRIBUTES>/<SAMPLE_ATTRIBUTE>
    """
    sm = sample_model.model_dump(by_alias=True)

    NSMAP = {
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "com": "SRA.common",
    }

    sample_set = etree.Element("SAMPLE_SET", nsmap=NSMAP)

    attrs = {"alias": sm["alias"]}
    # You could also add center_name if you know it; omitted by default.
    sample_el = etree.SubElement(sample_set, "SAMPLE", **attrs)

    # TITLE
    if sm.get("title"):
        title_el = etree.SubElement(sample_el, "TITLE")
        title_el.text = sm["title"]

    # SAMPLE_NAME (from organism field)
    organism = sm["organism"]
    sn_el = etree.SubElement(sample_el, "SAMPLE_NAME")

    tax_el = etree.SubElement(sn_el, "TAXON_ID")
    tax_el.text = str(organism["taxonId"])

    if organism.get("scientificName"):
        sci_el = etree.SubElement(sn_el, "SCIENTIFIC_NAME")
        sci_el.text = organism["scientificName"]

    if organism.get("commonName"):
        com_el = etree.SubElement(sn_el, "COMMON_NAME")
        com_el.text = organism["commonName"]

    # SAMPLE_ATTRIBUTES
    attrs_list = sm.get("attributes") or []

    # If you want description to appear as a SAMPLE_ATTRIBUTE:
    if sm.get("description"):
        attrs_list = attrs_list.copy()
        attrs_list.insert(0, {
            "tag": "description",
            "value": sm["description"],
            "unit": None,
        })

    if attrs_list:
        sats_el = etree.SubElement(sample_el, "SAMPLE_ATTRIBUTES")
        for a in attrs_list:
            sa_el = etree.SubElement(sats_el, "SAMPLE_ATTRIBUTE")
            tag_el = etree.SubElement(sa_el, "TAG")
            tag_el.text = a["tag"]
            val_el = etree.SubElement(sa_el, "VALUE")
            val_el.text = a["value"]
            if a.get("unit"):
                unit_el = etree.SubElement(sa_el, "UNITS")
                unit_el.text = a["unit"]

    return etree.tostring(
        sample_set,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True
    ).decode("utf-8")