from lxml import etree
from dinapy.ena.models import Experiment

def build_experiment_xml_from_model(exp_model: Experiment) -> str:
    exp = exp_model.model_dump(by_alias=True)  # use aliases like studyRef, sampleDescriptor, etc.

    NSMAP = {
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'com': "SRA.common",
    }

    exp_set = etree.Element("EXPERIMENT_SET", nsmap=NSMAP)

    exp_el = etree.SubElement(
        exp_set,
        "EXPERIMENT",
        alias=exp["alias"],
    )

    # TITLE
    if exp.get("title"):
        title_el = etree.SubElement(exp_el, "TITLE")
        title_el.text = exp["title"]

    # STUDY_REF
    study_ref = exp["studyRef"]
    study_ref_attrs = {k: v for k, v in study_ref.items() if v is not None}
    etree.SubElement(exp_el, "STUDY_REF", **study_ref_attrs)

    # DESIGN
    design = exp["design"]
    design_el = etree.SubElement(exp_el, "DESIGN")

    dd_el = etree.SubElement(design_el, "DESIGN_DESCRIPTION")
    dd_el.text = design["designDescription"]

    # SAMPLE_DESCRIPTOR — single sample OR pooled multi-sample
    sample_pool = design.get("samplePool")
    if sample_pool:
        # Multiplexed pool: <SAMPLE_DESCRIPTOR><POOL><MEMBER .../></POOL></SAMPLE_DESCRIPTOR>
        sd_el = etree.SubElement(design_el, "SAMPLE_DESCRIPTOR")
        pool_el = etree.SubElement(sd_el, "POOL")
        for member in sample_pool:
            member_attrs = {}
            if member.get("accession"):
                member_attrs["accession"] = member["accession"]
            if member.get("refname"):
                member_attrs["refname"] = member["refname"]
            if member.get("memberName"):
                member_attrs["member_name"] = member["memberName"]
            if member.get("proportion") is not None:
                member_attrs["proportion"] = str(member["proportion"])
            etree.SubElement(pool_el, "MEMBER", **member_attrs)
    else:
        # Single sample: <SAMPLE_DESCRIPTOR accession="SAMEA..."/>
        sample_ref = design.get("sampleDescriptor") or {}
        sample_attrs = {k: v for k, v in sample_ref.items() if v is not None}
        etree.SubElement(design_el, "SAMPLE_DESCRIPTOR", **sample_attrs)

    # LIBRARY_DESCRIPTOR
    lib = design["libraryDescriptor"]
    lib_desc_el = etree.SubElement(design_el, "LIBRARY_DESCRIPTOR")

    if lib.get("libraryName"):
        lib_name_el = etree.SubElement(lib_desc_el, "LIBRARY_NAME")
        lib_name_el.text = lib["libraryName"]

    etree.SubElement(lib_desc_el, "LIBRARY_STRATEGY").text = lib["libraryStrategy"]
    etree.SubElement(lib_desc_el, "LIBRARY_SOURCE").text = lib["librarySource"]
    etree.SubElement(lib_desc_el, "LIBRARY_SELECTION").text = lib["librarySelection"]

    layout_el = etree.SubElement(lib_desc_el, "LIBRARY_LAYOUT")
    layout_type = lib["libraryLayout"]["layoutType"]
    if layout_type == "SINGLE":
        etree.SubElement(layout_el, "SINGLE")
    else:
        paired_el = etree.SubElement(layout_el, "PAIRED")
        # Optional: nominal_length etc. are not attributes in SRA XSD, 
        # so they’d go elsewhere; for now we ignore them in XML.

    if lib.get("libraryConstructionProtocol"):
        prot_el = etree.SubElement(lib_desc_el, "LIBRARY_CONSTRUCTION_PROTOCOL")
        prot_el.text = lib["libraryConstructionProtocol"]

    # PLATFORM
    plat = exp["platform"]
    platform_el = etree.SubElement(exp_el, "PLATFORM")

    # We only have instrumentModel as a flat string; need to infer the correct platform element.
    inst = plat["instrumentModel"]
    if "Illumina" in inst or "HiSeq" in inst or "NextSeq" in inst or "NovaSeq" in inst or "MiSeq" in inst or "MiniSeq" in inst:
        plat_type_el = etree.SubElement(platform_el, "ILLUMINA")
    elif "PacBio" in inst or "Sequel" in inst or "Revio" in inst:
        plat_type_el = etree.SubElement(platform_el, "PACBIO_SMRT")
    elif inst in ("MinION", "GridION", "PromethION", "Flongle"):
        plat_type_el = etree.SubElement(platform_el, "OXFORD_NANOPORE")
    elif "BGI" in inst or "DNBSEQ" in inst or "MGISEQ" in inst:
        plat_type_el = etree.SubElement(platform_el, "DNBSEQ")
    elif "Ion Torrent" in inst:
        plat_type_el = etree.SubElement(platform_el, "ION_TORRENT")
    elif "454 GS" in inst:
        plat_type_el = etree.SubElement(platform_el, "LS454")
    else:
        plat_type_el = etree.SubElement(platform_el, "ILLUMINA")  # fallback

    model_el = etree.SubElement(plat_type_el, "INSTRUMENT_MODEL")
    model_el.text = inst

    return etree.tostring(
        exp_set, xml_declaration=True, encoding="UTF-8", pretty_print=True
    ).decode("utf-8")