from lxml import etree
from dinapy.ena.models import Project

def build_project_xml_from_model(project_model: Project) -> str:
    """
    Build ENA PROJECT_SET XML from a Project Pydantic model.

    Maps:
      - Project.alias   -> <PROJECT alias="...">
      - Project.title   -> <TITLE>
      - Project.description -> <DESCRIPTION>
      - Project.name    -> <NAME> (if present)
      - Project.submission_project.organism.* -> <SUBMISSION_PROJECT>/<ORGANISM>...
      - Project.project_links -> <PROJECT_LINKS>/<PROJECT_LINK>/<XREF_LINK> or <URL_LINK>
      - Project.project_attributes -> <PROJECT_ATTRIBUTES>/<PROJECT_ATTRIBUTE>
    """
    proj = project_model.model_dump(by_alias=True)

    NSMAP = {
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "com": "SRA.common",
    }

    proj_set = etree.Element("PROJECT_SET", nsmap=NSMAP)

    attrs = {"alias": proj["alias"]}
    proj_el = etree.SubElement(proj_set, "PROJECT", **attrs)

    # Optional NAME (short name)
    if proj.get("name"):
        name_el = etree.SubElement(proj_el, "NAME")
        name_el.text = proj["name"]

    # TITLE (required in ENA schema)
    title_el = etree.SubElement(proj_el, "TITLE")
    title_el.text = proj["title"]

    # DESCRIPTION (optional)
    if proj.get("description"):
        desc_el = etree.SubElement(proj_el, "DESCRIPTION")
        desc_el.text = proj["description"]

    # SUBMISSION_PROJECT / SEQUENCING_PROJECT / ORGANISM
    sub_proj = proj.get("submissionProject") or {}
    if sub_proj:
        sub_proj_el = etree.SubElement(proj_el, "SUBMISSION_PROJECT")

        # SEQUENCING_PROJECT (if locus_tag_prefix or other details present)
        seq_proj = sub_proj.get("sequencingProject") or {}
        if seq_proj and seq_proj.get("locusTagPrefix"):
            seq_el = etree.SubElement(sub_proj_el, "SEQUENCING_PROJECT")
            for prefix in seq_proj["locusTagPrefix"]:
                lp_el = etree.SubElement(seq_el, "LOCUS_TAG_PREFIX")
                lp_el.text = prefix
        else:
            # ENA examples often have an empty <SEQUENCING_PROJECT/>; optional
            etree.SubElement(sub_proj_el, "SEQUENCING_PROJECT")

        # ORGANISM (taxon info)
        org = sub_proj.get("organism") or {}
        if org:
            org_el = etree.SubElement(sub_proj_el, "ORGANISM")
            # TAXON_ID
            if org.get("taxonId") is not None:
                tax_el = etree.SubElement(org_el, "TAXON_ID")
                tax_el.text = str(org["taxonId"])
            # SCIENTIFIC_NAME
            if org.get("scientificName"):
                sci_el = etree.SubElement(org_el, "SCIENTIFIC_NAME")
                sci_el.text = org["scientificName"]
            # COMMON_NAME
            if org.get("commonName"):
                com_el = etree.SubElement(org_el, "COMMON_NAME")
                com_el.text = org["commonName"]
            # ENA usually puts these either in ORGANISM or as PROJECT_ATTRIBUTEs;

    # PROJECT_LINKS
    links = proj.get("projectLinks") or []
    if links:
        pls_el = etree.SubElement(proj_el, "PROJECT_LINKS")
        for link in links:
            pl_el = etree.SubElement(pls_el, "PROJECT_LINK")
            if link.get("xrefLink"):
                # XREF_LINK
                xref = link["xrefLink"]
                xl_el = etree.SubElement(pl_el, "XREF_LINK")
                db_el = etree.SubElement(xl_el, "DB")
                db_el.text = xref["db"]
                id_el = etree.SubElement(xl_el, "ID")
                id_el.text = xref["id"]
            elif link.get("url"):
                # URL_LINK
                url_el = etree.SubElement(pl_el, "URL_LINK")
                loc_el = etree.SubElement(url_el, "URL")
                loc_el.text = link["url"]

    # PROJECT_ATTRIBUTES
    attrs_list = proj.get("projectAttributes") or []
    if attrs_list:
        pats_el = etree.SubElement(proj_el, "PROJECT_ATTRIBUTES")
        for a in attrs_list:
            pa_el = etree.SubElement(pats_el, "PROJECT_ATTRIBUTE")
            tag_el = etree.SubElement(pa_el, "TAG")
            tag_el.text = a["tag"]
            val_el = etree.SubElement(pa_el, "VALUE")
            val_el.text = a["value"]
            if a.get("unit"):
                unit_el = etree.SubElement(pa_el, "UNITS")
                unit_el.text = a["unit"]

    return etree.tostring(
        proj_set,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True
    ).decode("utf-8")