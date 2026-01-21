from lxml import etree
from dinapy.ena.models import Run

def build_run_xml_from_model(run_model: Run) -> str:
    run = run_model.model_dump(by_alias=True)

    NSMAP = {
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'com': "SRA.common",
    }

    run_set = etree.Element("RUN_SET", nsmap=NSMAP)

    attrs = {"alias": run["alias"]}
    if run.get("runDate"):
        attrs["run_date"] = run["runDate"]
    if run.get("runCenter"):
        attrs["run_center"] = run["runCenter"]

    run_el = etree.SubElement(run_set, "RUN", **attrs)

    if run.get("title"):
        title_el = etree.SubElement(run_el, "TITLE")
        title_el.text = run["title"]

    exp_ref = run["experimentRef"]
    exp_ref_attrs = {k: v for k, v in exp_ref.items() if v is not None}
    etree.SubElement(run_el, "EXPERIMENT_REF", **exp_ref_attrs)

    # We flatten dataBlocks[] to DATA_BLOCK/FILES/FILE, because the XSD has a single DATA_BLOCK element.
    data_block_el = etree.SubElement(run_el, "DATA_BLOCK")
    files_el = etree.SubElement(data_block_el, "FILES")

    for block in run.get("dataBlocks", []):
        for f in block["files"]:
            file_attrs = {
                "filename": f["filename"],
                "filetype": f["filetype"],
                "checksum_method": f["checksumMethod"],
                "checksum": f["checksum"],
            }
            if f.get("unencryptedChecksum"):
                file_attrs["unencrypted_checksum"] = f["unencryptedChecksum"]

            file_el = etree.SubElement(files_el, "FILE", **file_attrs)

            # Optionally add READ_LABEL children or READ_TYPEs if you want; for now we skip.

    return etree.tostring(
        run_set, xml_declaration=True, encoding="UTF-8", pretty_print=True
    ).decode("utf-8")