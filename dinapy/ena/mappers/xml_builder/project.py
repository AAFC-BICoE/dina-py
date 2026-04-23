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
      - Project.collaborators -> <COLLABORATORS>/<COLLABORATOR>
      - Project.umbrella_project.organism.* -> <UMBRELLA_PROJECT>/<ORGANISM>...
      - Project.sequencing_project.* -> <SUBMISSION_PROJECT>/<SEQUENCING_PROJECT>...
      - Project.related_projects -> <RELATED_PROJECTS>/<RELATED_PROJECT>
      - Project.project_links -> <PROJECT_LINKS>/<PROJECT_LINK>/<XREF_LINK> or <URL_LINK>
      - Project.attributes -> <PROJECT_ATTRIBUTES>/<PROJECT_ATTRIBUTE>
      
    Note: UMBRELLA_PROJECT and SUBMISSION_PROJECT are mutually exclusive.
    If umbrella_project is set, it takes precedence.
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

    # COLLABORATORS (XML-only)
    collaborators = proj.get("collaborators") or []
    if collaborators:
        collabs_el = etree.SubElement(proj_el, "COLLABORATORS")
        for collab_name in collaborators:
            collab_el = etree.SubElement(collabs_el, "COLLABORATOR")
            collab_el.text = collab_name

    # UMBRELLA_PROJECT or SUBMISSION_PROJECT (mutually exclusive)
    umbrella = proj.get("umbrellaProject")
    if umbrella:
        # UMBRELLA_PROJECT mode - for grouping other projects
        umb_el = etree.SubElement(proj_el, "UMBRELLA_PROJECT")
        
        # ORGANISM (optional in umbrella)
        org = umbrella.get("organism")
        if org:
            org_el = etree.SubElement(umb_el, "ORGANISM")
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
            # Optional organism fields
            for field in ["strain", "breed", "cultivar", "isolate"]:
                if org.get(field):
                    field_el = etree.SubElement(org_el, field.upper())
                    field_el.text = org[field]
    else:
        # SUBMISSION_PROJECT mode - standard project
        sub_proj_el = etree.SubElement(proj_el, "SUBMISSION_PROJECT")
        
        # SEQUENCING_PROJECT (inside SUBMISSION_PROJECT)
        seq_proj = proj.get("sequencingProject") or {}
        if seq_proj and seq_proj.get("locusTagPrefix"):
            seq_el = etree.SubElement(sub_proj_el, "SEQUENCING_PROJECT")
            for prefix in seq_proj["locusTagPrefix"]:
                lp_el = etree.SubElement(seq_el, "LOCUS_TAG_PREFIX")
                lp_el.text = prefix
        else:
            # Empty SEQUENCING_PROJECT element
            etree.SubElement(sub_proj_el, "SEQUENCING_PROJECT")

        # ORGANISM (optional, inside SUBMISSION_PROJECT)
        # Check if organism is in submissionProject (old structure)
        sub_proj_data = proj.get("submissionProject") or {}
        org = sub_proj_data.get("organism")
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

    # RELATED_PROJECTS (XML-only)
    related_projects = proj.get("relatedProjects") or []
    if related_projects:
        rel_projs_el = etree.SubElement(proj_el, "RELATED_PROJECTS")
        for rel_proj in related_projects:
            rel_proj_el = etree.SubElement(rel_projs_el, "RELATED_PROJECT")
            
            # Relationship type element with accession attribute
            # Structure: <PARENT_PROJECT accession="..."/>
            rel_type = rel_proj.get("relationshipType")
            accession = rel_proj.get("accession")
            if rel_type and accession:
                etree.SubElement(rel_proj_el, rel_type, accession=accession)

    # PROJECT_LINKS (field name is now project_links in our model)
    links = proj.get("project_links") or []
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

    # PROJECT_ATTRIBUTES (field name is now attributes in our model)
    attrs_list = proj.get("attributes") or []
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