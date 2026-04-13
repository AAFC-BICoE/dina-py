"""
Interactive Solara GUI for DINA to ENA submission workflow.

This module provides a user-friendly graphical interface for submitting
sequence data to the European Nucleotide Archive (ENA).

The workflow is **sequence-oriented**: it starts from a directory of local
sequencing files (already uploaded to ENA FTP), verifies their presence on
the server, resolves associated DINA material samples where possible, and
submits the full ENA metadata chain:

    Study → Samples (single or POOL) → Experiments → Runs

Workflow steps:
1. Configuration  – ENA Webin credentials, study mode, defaults
2. Files & Library – Sequence file directory + library parameters
3. Verify & Lookup – FTP check, MD5 computation, DINA sample lookup
4. Review          – Table of planned submissions
5. Submit          – Study → Samples → Experiments → Runs
6. Results         – Per-entry accession table and receipt detail

Scenarios supported:
- New study (from scratch): minimal study is auto-generated.
- Existing study: user provides an existing project accession; study
  submission is skipped.

Sample multiplicity:
- If a sequence entry resolves to exactly 1 DINA material sample, one ENA
  sample is submitted and referenced in the experiment.
- If a sequence entry resolves to N > 1 DINA material samples, all N are
  submitted as a SAMPLE_SET and the experiment references them via a POOL.
- If no DINA material sample is found, a minimal ENA sample is created using
  the configurable default NCBI taxon ID.

Usage:
    >>> from dinapy.ena.workflow_gui import ENAWorkflowGUI
    >>> ENAWorkflowGUI()  # Launch the interactive Solara GUI
"""

import importlib
import re
import time
import traceback
from datetime import date
from pathlib import Path
from typing import List

import solara

from dinapy.ena.models import (
    Attribute,
    DataBlock,
    Design,
    Experiment,
    File as ENAFile,
    LibraryDescriptor,
    LibraryLayout,
    ObjectRef,
    Organism,
    Platform,
    PoolMember,
    Project,
    Run,
    Sample,
)
from dinapy.ena.submission import ENASubmissionWorkflow
from dinapy.ena.upload import ReadUploader


@solara.component
def ENAWorkflowGUI():
    """Sequence-oriented GUI for the DINA → ENA submission workflow."""

    solara.lab.ThemeToggle()

    # ── Navigation ─────────────────────────────────────────────────────────
    current_step = solara.use_reactive(1)

    # ── Step 1 state: credentials & study mode ────────────────────────────
    # Webin credentials are read from os.environ on every render so that
    # loading the .env in a notebook cell takes effect immediately without
    # needing to restart the kernel or the component.
    import os as _os
    def _webin_username() -> str:
        return _os.environ.get("WEBIN_USERNAME", "")
    def _webin_password() -> str:
        return _os.environ.get("WEBIN_PASSWORD", "")
    def _use_test_server() -> bool:
        return _os.environ.get("WEBIN_TEST", "true").lower() not in ("false", "0", "no", "off")

    study_mode = solara.use_reactive("new")           # "new" | "existing"
    existing_study_accession = solara.use_reactive("")
    default_taxon_id = solara.use_reactive(256318)    # metagenome
    hold_date = solara.use_reactive(date.today().isoformat())

    # ── Step 2 state: sequence files & library ───────────────────────────
    sequence_directory = solara.use_reactive("")
    file_pattern = solara.use_reactive("*.fastq.gz")
    library_layout_val = solara.use_reactive("PAIRED")
    r1_suffix = solara.use_reactive("_R1")
    r2_suffix = solara.use_reactive("_R2")
    library_strategy = solara.use_reactive("AMPLICON")
    library_source = solara.use_reactive("METAGENOMIC")
    library_selection = solara.use_reactive("PCR")
    instrument_model = solara.use_reactive("Illumina NovaSeq 6000")
    design_description = solara.use_reactive("")
    nominal_length = solara.use_reactive(300)
    nominal_sdev = solara.use_reactive(50.0)

    # ── Step 3 state: verify & lookup results ───────────────────────────
    # Each entry is a dict:
    #   stem, files: [Path], md5s: [str], on_ftp: [bool],
    #   dina_samples: [dict], attachment_uuids: [str],
    #   ena_sample_accessions: [str],
    #   ena_experiment_alias: str | None, ena_experiment_accession: str | None,
    #   ena_run_alias: str | None,        ena_run_accession: str | None
    sequence_entries = solara.use_reactive([])
    # Pre-mapped ENA sample data (fetched + mapped in precompute step; editable by user).
    # Structure: List[{stem, samples: [{alias, title, taxon_id, attributes: [{tag, value}]}]}]
    mapped_entries_preview = solara.use_reactive([])

    # ── Submit state ───────────────────────────────────────────────────────
    project_accession = solara.use_reactive("")
    project_receipt = solara.use_reactive(None)
    status_messages = solara.use_reactive([])
    is_processing = solara.use_reactive(False)

    # ── Step labels ─────────────────────────────────────────────────────
    STEP_NAMES = [
        "Config",
        "Files & Library",
        "Verify & Lookup",
        "Review",
        "Submit",
        "Results",
    ]

    
    # ══════════════════════════════════════════════════════════════════════════
    # Helper utilities
    # ══════════════════════════════════════════════════════════════════════════

    def add_status(message: str, msg_type: str = "info") -> None:
        ts = time.strftime("%H:%M:%S")
        status_messages.value = status_messages.value + [(ts, msg_type, message)]

    def _ftp_host() -> str:
        return "webin2.ebi.ac.uk" if _use_test_server() else "webin.ebi.ac.uk"

    def _msg_color(msg_type: str) -> str:
        return {"info": "blue", "success": "green", "warning": "orange", "error": "red"}.get(
            msg_type, "grey"
        )

    def _get_objectstore_filename(file_path: Path) -> str:
        """
        Extract the base filename for ObjectStore lookup.
        
        ObjectStore's originalFilename field stores names without file extensions
        and without paired-end suffixes (_R1, _R2, etc.).
        
        Examples:
            sample_R1.fastq.gz → sample
            sample_R2.fq.gz → sample
            data.fasta.gz → data
            file_1.fastq → file
        """
        name = file_path.name
        
        # Strip common sequence file extensions (handles double extensions like .fastq.gz)
        extensions = [
            '.fastq.gz', '.fq.gz', '.fasta.gz', '.fa.gz',
            '.fastq', '.fq', '.fasta', '.fa'
        ]
        for ext in extensions:
            if name.endswith(ext):
                name = name[:-len(ext)]
                break
        
        # Strip paired-end suffixes (_R1, _R2, _1, _2)
        name = re.sub(r'[_\.]R?[12]$', '', name)
        
        return name

    def render_status_log() -> None:
        for ts, msg_type, msg in status_messages.value:
            color = _msg_color(msg_type)
            solara.Markdown(f"<span style='color:{color}'>[{ts}] {msg}</span>")

    def display_receipt_details(receipt, title: str) -> None:
        """Display detailed receipt information"""
        from dinapy.ena.receipt import format_receipt_summary
        
        if not receipt:
            return
        
        with solara.Card(title):
            if receipt.success:
                solara.Success(f"✓ {title} - SUCCESS")
            else:
                solara.Error(f"✗ {title} - FAILURE")
            
            # Show accessions
            if receipt.objects:
                solara.Markdown("**Accessions:**")
                for obj in receipt.objects:
                    if obj.accession:
                        solara.Markdown(f"- {obj.object_type}: `{obj.accession}` (status: {obj.status or 'N/A'})")
            
            # Show errors
            errors = receipt.get_errors()
            if errors:
                solara.Markdown("**Errors:**")
                for err in errors:
                    solara.Error(err)
            
            # Show warnings
            warnings = receipt.get_warnings()
            if warnings:
                solara.Markdown("**Warnings:**")
                for warn in warnings:
                    solara.Warning(warn)
            
            # Show info messages
            infos = receipt.get_info()
            if infos:
                solara.Markdown("**Info:**")
                for info in infos:
                    solara.Info(info)
            
            # Show full formatted summary in expandable section
            with solara.Details("View Full Receipt"):
                summary = format_receipt_summary(receipt)
                solara.Markdown(f"```\n{summary}\n```")

    # ══════════════════════════════════════════════════════════════════════════
    # Step 3 action: Scan → FTP check → MD5 → DINA lookup
    # ══════════════════════════════════════════════════════════════════════════

    def scan_verify_and_lookup() -> None:
        """Scan directory, verify files on FTP, compute MD5s, look up DINA samples."""
        is_processing.value = True
        status_messages.value = []

        try:
            # ── 1. Scan local directory ───────────────────────────────────────
            dir_path = Path(sequence_directory.value)
            if not dir_path.exists():
                add_status(f"Directory not found: {sequence_directory.value}", "error")
                return

            matching_files = sorted(dir_path.glob(file_pattern.value))
            if not matching_files:
                add_status(
                    f"No files matching '{file_pattern.value}' found in {dir_path}", "warning"
                )
                return

            add_status(f"Found {len(matching_files)} file(s) matching pattern", "info")

            # ── 2. Group into sequence entries ────────────────────────────────
            entries: List[dict] = []

            if library_layout_val.value == "PAIRED":
                pairs: dict = {}
                unpaired: list = []
                for f in matching_files:
                    raw = f.name
                    for ext in (".fastq.gz", ".fq.gz", ".fastq", ".fq"):
                        if raw.endswith(ext):
                            raw = raw[: -len(ext)]
                            break
                    if raw.endswith(r1_suffix.value):
                        stem = raw[: -len(r1_suffix.value)]
                        pairs.setdefault(stem, {})["r1"] = f
                    elif raw.endswith(r2_suffix.value):
                        stem = raw[: -len(r2_suffix.value)]
                        pairs.setdefault(stem, {})["r2"] = f
                    else:
                        unpaired.append(f)

                for stem, pair in pairs.items():
                    files = [f for key in ("r1", "r2") if key in pair for f in [pair[key]]]
                    entries.append({"stem": stem, "files": files})

                for f in unpaired:
                    add_status(f"⚠ Could not pair: {f.name} — treating as single", "warning")
                    entries.append({"stem": f.stem, "files": [f]})
            else:
                for f in matching_files:
                    entries.append({"stem": f.stem, "files": [f]})

            add_status(f"Grouped into {len(entries)} sequence entr(ies)", "info")

            # ── 3. FTP check ──────────────────────────────────────────────────
            add_status(
                f"Connecting to ENA FTP ({_ftp_host()}) to verify files are present...", "info"
            )
            uploader = ReadUploader()
            all_entry_files = [f for e in entries for f in e["files"]]
            ftp_status: dict = {}
            try:
                ftp_status = uploader.check_files_on_ftp(
                    file_paths=all_entry_files,
                    host=_ftp_host(),
                    username=_webin_username(),
                    password=_webin_password(),
                )
                found_count = sum(1 for v in ftp_status.values() if v)
                total_files = len(all_entry_files)
                level = "success" if found_count == total_files else "warning"
                add_status(
                    f"FTP check: {found_count}/{total_files} file(s) found on server", level
                )
                for fname, present in ftp_status.items():
                    icon = "✓" if present else "✗"
                    add_status(f"  {icon} {fname}", "success" if present else "warning")
            except Exception as ftp_err:
                add_status(f"FTP check failed: {ftp_err}", "warning")
                add_status("Continuing without FTP verification", "info")

            # ── 4. Local MD5 computation ──────────────────────────────────────
            add_status("Computing local MD5 checksums...", "info")
            for entry in entries:
                entry["md5s"] = []
                entry["on_ftp"] = []
                for f in entry["files"]:
                    md5 = ReadUploader.compute_md5(f)
                    entry["md5s"].append(md5)
                    entry["on_ftp"].append(ftp_status.get(f.name, False))
                    add_status(f"  {f.name}: MD5={md5[:8]}...", "info")

            # ── 5. DINA lookup ────────────────────────────────────────────────
            add_status(
                "Looking up DINA material samples via object-store + search API...", "info"
            )
            # NOTE: ObjectStoreAPI() and SearchAPI() constructors DO attempt a
            # network connection: DinaAPI.__init__ → set_keycloak() →
            # generate_token() → keycloak.token() (HTTP request to Keycloak).
            dina_available = False
            object_store_api = None
            search_api = None
            try:
                from dinapy.apis.objectstoreapi.objectstore_api import ObjectStoreAPI
                from dinapy.apis.searchapi.search_api import SearchAPI
            except Exception as import_err:
                add_status(
                    f"DINA API import failed ({type(import_err).__name__}: {import_err})",
                    "error",
                )
                for line in traceback.format_exc().splitlines():
                    if line.strip():
                        add_status(f"  {line}", "error")

            if object_store_api is None and 'ObjectStoreAPI' in dir():
                try:
                    add_status("Initialising ObjectStoreAPI (connects to Keycloak)...", "info")
                    object_store_api = ObjectStoreAPI()
                    add_status("✓ ObjectStoreAPI initialised", "success")
                except Exception as err:
                    add_status(
                        f"ObjectStoreAPI init failed ({type(err).__name__}: {err})",
                        "error",
                    )
                    for line in traceback.format_exc().splitlines():
                        if line.strip():
                            add_status(f"  {line}", "error")

            if search_api is None and 'SearchAPI' in dir():
                try:
                    add_status("Initialising SearchAPI (connects to Keycloak)...", "info")
                    search_api = SearchAPI()
                    add_status("✓ SearchAPI initialised", "success")
                except Exception as err:
                    add_status(
                        f"SearchAPI init failed ({type(err).__name__}: {err})",
                        "error",
                    )
                    for line in traceback.format_exc().splitlines():
                        if line.strip():
                            add_status(f"  {line}", "error")

            dina_available = object_store_api is not None and search_api is not None
            if not dina_available:
                add_status(
                    "DINA API unavailable — all samples will use minimal ENA records",
                    "warning",
                )

            for entry in entries:
                entry["dina_samples"] = []
                entry["attachment_uuids"] = []
                if not dina_available:
                    continue

                seen_sample_ids: set = set()
                for f in entry["files"]:
                    try:
                        # Step 1: Look up attachment by filename in ObjectStore.
                        # Use a wildcard search via the search API so that full
                        # filenames (e.g. sample_R1.fastq.gz) are matched by the
                        # stripped stem (e.g. sample).
                        filename_no_ext = _get_objectstore_filename(f)  # strips ext + R1/R2
                        add_status(
                            f"  Searching object store for '{filename_no_ext}' (from {f.name})...",
                            "info",
                        )
                        os_resp = search_api.search_object_store_by_filename(filename_no_ext)
                        os_hits = (
                            os_resp.get("hits", {}).get("hits", [])
                            if os_resp
                            else []
                        )
                        if not os_hits:
                            add_status(
                                f"    ✗ No object-store records found for '{filename_no_ext}'",
                                "warning",
                            )
                            continue

                        records = [h.get("_source", {}).get("data", {}) for h in os_hits]
                        add_status(
                            f"    ✓ Found {len(records)} object-store record(s) matching stem",
                            "success",
                        )

                        attachment_uuid = records[0].get("id")
                        if not attachment_uuid:
                            add_status(f"    ✗ No attachment UUID in metadata for '{filename_no_ext}'", "warning")
                            continue
                        entry["attachment_uuids"].append(attachment_uuid)
                        add_status(
                            f"    ✓ Found attachment {attachment_uuid[:8]}... ({len(records)} record(s))", "success"
                        )

                        # Step 2: Search for material samples linked to this attachment
                        add_status(f"  Searching for material samples linked to attachment...", "info")
                        search_resp = search_api.search_material_samples_by_attachment(
                            attachment_uuid
                        )
                        hits = (
                            search_resp.get("hits", {}).get("hits", [])
                            if search_resp
                            else []
                        )
                        
                        if not hits:
                            total = search_resp.get("hits", {}).get("total", {})
                            total_value = total.get("value", 0) if isinstance(total, dict) else total
                            add_status(f"    ✗ No material samples found for attachment (total={total_value})", "warning")
                        else:
                            add_status(f"    ✓ Found {len(hits)} material sample hit(s)", "success")
                        
                        for hit in hits:
                            src = hit.get("_source", {})
                            data_field = src.get("data", {})
                            sample_docs = (
                                data_field
                                if isinstance(data_field, list)
                                else [data_field]
                            )
                            for sample_doc in sample_docs:
                                sid = sample_doc.get("id")
                                if sid and sid not in seen_sample_ids:
                                    seen_sample_ids.add(sid)
                                    entry["dina_samples"].append(sample_doc)

                    except Exception as lookup_err:
                        add_status(f"  ✗ Lookup error for {f.name}: {lookup_err}", "warning")

                if entry["dina_samples"]:
                    names = [
                        s.get("attributes", {}).get(
                            "materialSampleName", s.get("id", "?")
                        )
                        for s in entry["dina_samples"]
                    ]
                    add_status(
                        f"  {entry['stem']}: {len(entry['dina_samples'])} DINA sample(s) → "
                        + ", ".join(names),
                        "success",
                    )
                else:
                    add_status(
                        f"  {entry['stem']}: no DINA samples found — minimal sample will be created",
                        "info",
                    )

            # ── 6. Initialise per-entry submit fields ─────────────────────────
            for entry in entries:
                entry.setdefault("ena_sample_accessions", [])
                entry.setdefault("ena_experiment_alias", None)
                entry.setdefault("ena_experiment_accession", None)
                entry.setdefault("ena_run_alias", None)
                entry.setdefault("ena_run_accession", None)

            sequence_entries.value = entries
            add_status(f"✓ Scan complete — {len(entries)} entr(ies) ready for review", "success")
            current_step.value = 4

        except Exception as e:
            add_status(f"Fatal scan error: {e}", "error")
            for line in traceback.format_exc().split("\n")[-6:-1]:
                if line.strip():
                    add_status(f"  {line}", "error")
        finally:
            is_processing.value = False

    # ══════════════════════════════════════════════════════════════════════════
    # Step 5 action: Submit Study → Samples → Experiments → Runs
    # ══════════════════════════════════════════════════════════════════════════

    def submit_to_ena() -> None:
        is_processing.value = True
        status_messages.value = []
        entries = [dict(e) for e in sequence_entries.value]

        try:
            workflow = ENASubmissionWorkflow(
                username=_webin_username(),
                password=_webin_password(),
                test=_use_test_server(),
            )
            timestamp = str(int(time.time()))

            # ── [1/4] Study ───────────────────────────────────────────────────
            if study_mode.value == "existing":
                project_accession.value = existing_study_accession.value
                add_status(
                    f"[1/4] Using existing study: {project_accession.value}", "info"
                )
            else:
                add_status("[1/4] Submitting minimal study...", "info")
                ena_project = Project(
                    alias=f"study_{timestamp}",
                    title=f"Sequencing study ({timestamp})",
                    description=(
                        f"Sequencing study created from {len(entries)} sequence entr(ies)"
                    ),
                )
                receipt = workflow.submit_project_xml(
                    ena_project, action="ADD", hold_until_date=hold_date.value
                )
                project_receipt.value = receipt
                if receipt.success:
                    project_accession.value = receipt.get_accession(
                        "PROJECT"
                    ) or receipt.get_accession("STUDY")
                    add_status(f"✓ Study submitted: {project_accession.value}", "success")
                    for warn in receipt.get_warnings():
                        add_status(f"  Study warning: {warn}", "warning")
                else:
                    for err in receipt.get_errors():
                        add_status(f"Study error: {err}", "error")
                    raise Exception("Study submission failed")

            # ── Pre-flight: FTP presence check across ALL entries ─────────────
            add_status("\n─── FTP pre-flight check ───", "info")
            all_present = True
            for entry in entries:
                on_ftp_list = entry.get("on_ftp", [])
                # Treat entries with no FTP data as unconfirmed
                if not on_ftp_list:
                    add_status(
                        f"  ✗ {entry['stem']}: FTP status unknown (re-run scan to verify)",
                        "error",
                    )
                    all_present = False
                    continue
                for f, on_ftp in zip(entry["files"], on_ftp_list):
                    status_icon = "✓" if on_ftp else "✗"
                    status_level = "success" if on_ftp else "error"
                    add_status(
                        f"  {status_icon} {entry['stem']} / {f.name}",
                        status_level,
                    )
                    if not on_ftp:
                        all_present = False

            if not all_present:
                add_status(
                    "\n✗ One or more sequence files are missing from the FTP server. "
                    "Please upload all files before submitting. Submission aborted.",
                    "error",
                )
                return

            add_status("✓ All files confirmed on FTP — proceeding with submission.\n", "success")

            # ── [2-4] Per entry: Samples → Experiment → Run ───────────────────
            total = len(entries)
            for idx, entry in enumerate(entries, 1):
                stem = entry["stem"]
                add_status(f"\n─── Entry {idx}/{total}: {stem} ───", "info")

                # ── [2] Samples ───────────────────────────────────────────────
                sample_accessions: List[str] = []
                dina_samples = entry.get("dina_samples", [])

                if dina_samples:
                    add_status(
                        f"[2/4] Mapping {len(dina_samples)} DINA sample(s) for {stem}...",
                        "info",
                    )
                    from dinapy.apis.collectionapi.ena_helpers import (
                        prepare_sample_for_ena_mapping,
                    )
                    from dinapy.apis.collectionapi.materialsampleapi import MaterialSampleAPI
                    from dinapy.ena.mappers.dina_to_ena import mappers_dto as _mappers_mod

                    importlib.reload(_mappers_mod)
                    from dinapy.ena.mappers.dina_to_ena.mappers_dto import (
                        material_sample_to_ena,
                    )

                    ms_api = MaterialSampleAPI()

                    ena_samples: List[Sample] = []
                    for dina_s in dina_samples:
                        sample_id = dina_s.get("id", "?")
                        try:
                            add_status(
                                f"  Fetching full DINA record for sample {sample_id[:8]}...",
                                "info",
                            )
                            full_resp = ms_api.get_req_dina(
                                f"{ms_api.base_url}/{sample_id}",
                                {"include": "collectingEvent,organism"},
                            )
                            full_json = full_resp.json() if hasattr(full_resp, "json") else full_resp
                            full_sample_data = full_json.get("data")
                            full_included = full_json.get("included", [])

                            if not full_sample_data:
                                raise ValueError(
                                    f"DINA API returned no data for sample id={sample_id}"
                                )
                            ms_dto, ce_dto, org_data = prepare_sample_for_ena_mapping(
                                full_sample_data, full_included
                            )
                            ena_s = material_sample_to_ena(
                                material_sample=ms_dto,
                                collecting_event=ce_dto,
                                organism_data=org_data,
                                email="your.email@example.com",
                                include_unmapped=True,
                            )
                            ena_s.alias = f"{ena_s.alias}_{timestamp}"
                            ena_samples.append(ena_s)
                        except Exception as map_err:
                            add_status(
                                f"  Mapping error for DINA sample {sample_id[:8]}: {map_err} — using minimal",
                                "warning",
                            )
                            sname = dina_s.get("attributes", {}).get(
                                "materialSampleName", stem
                            )
                            ena_samples.append(
                                Sample(
                                    alias=f"{sname}_{timestamp}",
                                    title=sname,
                                    organism=Organism(taxon_id=default_taxon_id.value),
                                    attributes=[
                                        Attribute(tag="collection date", value="not provided"),
                                        Attribute(tag="geographic location (country and/or sea)", value="not provided"),
                                    ],
                                )
                            )
                else:
                    add_status(f"[2/4] Creating minimal sample for {stem}...", "info")
                    ena_samples = [
                        Sample(
                            alias=f"{stem}_{timestamp}",
                            title=stem,
                            organism=Organism(taxon_id=default_taxon_id.value),
                            attributes=[
                                Attribute(tag="collection date", value="not provided"),
                                Attribute(tag="geographic location (country and/or sea)", value="not provided"),
                            ],
                        )
                    ]

                if len(ena_samples) == 1:
                    receipt = workflow.submit_sample_xml(
                        ena_samples[0],
                        action="ADD",
                        hold_until_date=hold_date.value,
                    )
                    if receipt.success:
                        acc = receipt.get_accession("SAMPLE")
                        sample_accessions.append(acc)
                        add_status(f"✓ Sample submitted: {acc}", "success")
                    else:
                        for err in receipt.get_errors():
                            add_status(f"Sample error: {err}", "error")
                        raise Exception(f"Sample submission failed for {stem}")
                else:
                    receipt = workflow.submit_samples_xml(
                        ena_samples,
                        action="ADD",
                        hold_until_date=hold_date.value,
                    )
                    if receipt.success:
                        for obj in receipt.objects:
                            if obj.accession:
                                sample_accessions.append(obj.accession)
                        add_status(
                            f"✓ {len(sample_accessions)} samples submitted as SAMPLE_SET",
                            "success",
                        )
                    else:
                        for err in receipt.get_errors():
                            add_status(f"Sample set error: {err}", "error")
                        raise Exception(f"Sample set submission failed for {stem}")

                entry["ena_sample_accessions"] = sample_accessions

                # ── [3] Experiment ─────────────────────────────────────────────
                add_status(f"[3/4] Submitting experiment for {stem}...", "info")
                exp_alias = f"exp_{stem}_{timestamp}"

                lib_layout = LibraryLayout(
                    layout_type=library_layout_val.value,
                    nominal_length=(
                        nominal_length.value
                        if library_layout_val.value == "PAIRED"
                        else None
                    ),
                    nominal_sdev=(
                        nominal_sdev.value
                        if library_layout_val.value == "PAIRED"
                        else None
                    ),
                )
                lib_desc = LibraryDescriptor(
                    library_strategy=library_strategy.value,
                    library_source=library_source.value,
                    library_selection=library_selection.value,
                    library_layout=lib_layout,
                )
                desc_text = (
                    design_description.value
                    or f"{library_strategy.value} sequencing"
                )

                if len(sample_accessions) > 1:
                    design = Design(
                        design_description=desc_text,
                        sample_pool=[
                            PoolMember(
                                accession=acc,
                                member_name=f"member_{i + 1}",
                            )
                            for i, acc in enumerate(sample_accessions)
                        ],
                        library_descriptor=lib_desc,
                    )
                else:
                    design = Design(
                        design_description=desc_text,
                        sample_descriptor=ObjectRef(accession=sample_accessions[0]),
                        library_descriptor=lib_desc,
                    )

                ena_experiment = Experiment(
                    alias=exp_alias,
                    title=f"Sequencing experiment for {stem}",
                    study_ref=ObjectRef(accession=project_accession.value),
                    design=design,
                    platform=Platform(instrument_model=instrument_model.value),
                )
                receipt = workflow.submit_experiment(ena_experiment, action="ADD")
                if receipt.success:
                    exp_acc = receipt.get_accession("EXPERIMENT")
                    entry["ena_experiment_alias"] = exp_alias
                    entry["ena_experiment_accession"] = exp_acc
                    add_status(f"✓ Experiment submitted: {exp_acc}", "success")
                else:
                    for err in receipt.get_errors():
                        add_status(f"Experiment error: {err}", "error")
                    raise Exception(f"Experiment submission failed for {stem}")

                # ── [4] Run ────────────────────────────────────────────────────
                add_status(f"[4/4] Submitting run for {stem}...", "info")
                run_alias = f"run_{stem}_{timestamp}"
                run_files = [
                    ENAFile(
                        filename=f.name,
                        filetype="fastq",
                        checksum_method="MD5",
                        checksum=md5,
                    )
                    for f, md5 in zip(entry["files"], entry["md5s"])
                ]
                ena_run = Run(
                    alias=run_alias,
                    title=f"Run for {stem}",
                    experiment_ref=ObjectRef(refname=exp_alias),
                    data_blocks=[DataBlock(files=run_files)],
                )
                receipt = workflow.submit_run(ena_run, action="ADD")
                if receipt.success:
                    run_acc = receipt.get_accession("RUN")
                    entry["ena_run_alias"] = run_alias
                    entry["ena_run_accession"] = run_acc
                    add_status(f"✓ Run submitted: {run_acc}", "success")
                else:
                    for err in receipt.get_errors():
                        add_status(f"Run error: {err}", "error")
                    add_status(
                        "Run submission failed — experiment and samples are registered",
                        "warning",
                    )

            sequence_entries.value = entries
            add_status(
                f"\n✓ Submission workflow complete for {total} entr(ies)", "success"
            )
            current_step.value = 6

        except Exception as e:
            add_status(f"Fatal submission error: {e}", "error")
            for line in traceback.format_exc().split("\n")[-6:-1]:
                if line.strip():
                    add_status(f"  {line}", "error")
        finally:
            is_processing.value = False


    
    # ══════════════════════════════════════════════════════════════════════════
    # Main layout
    # ══════════════════════════════════════════════════════════════════════════

    with solara.Card(title="ENA Submission Workflow", elevation=2):
        solara.Markdown(f"### Step {current_step.value} of 6")
        solara.ProgressLinear(value=(current_step.value / 6) * 100)

        with solara.Row():
            for i, name in enumerate(STEP_NAMES, 1):
                color = (
                    "primary"
                    if i == current_step.value
                    else ("success" if i < current_step.value else "default")
                )
                solara.Button(
                    f"{i}. {name}",
                    color=color,
                    disabled=True,
                    style={"margin": "5px"},
                )

        solara.HTML(tag="hr")

        # ── Step 1: Configuration ─────────────────────────────────────────────
        if current_step.value == 1:
            solara.Markdown("## Step 1: Configuration")

            with solara.Card("ENA Webin Credentials"):
                if _webin_username():
                    solara.Success(f"✓ Webin credentials loaded from environment")
                    solara.Markdown(f"**Username:** `{_webin_username()}`")
                    solara.Markdown(f"**Server:** {'Test (webin2.ebi.ac.uk)' if _use_test_server() else 'Production (webin.ebi.ac.uk)'}")
                    solara.Markdown("*To change credentials, update `WEBIN_USERNAME`, `WEBIN_PASSWORD`, and `WEBIN_TEST` in your `.env` file and re-run this cell.*")
                else:
                    solara.Warning("⚠ No Webin credentials found in environment. Add `WEBIN_USERNAME`, `WEBIN_PASSWORD`, and `WEBIN_TEST` to your `.env` file.")

            with solara.Card("Study"):
                solara.Select(
                    label="Study Mode",
                    value=study_mode,
                    values=["new", "existing"],
                )
                if study_mode.value == "existing":
                    solara.InputText(
                        label="Existing Study Accession (e.g. PRJEB123456)",
                        value=existing_study_accession,
                        continuous_update=False,
                    )
                else:
                    solara.Info("A minimal study will be created automatically at submission time.")

            with solara.Card("Defaults"):
                solara.InputInt(
                    label="Default NCBI Taxon ID for minimal samples",
                    value=default_taxon_id,
                )
                solara.Markdown(
                    "*256318 = metagenome. Used when no DINA sample is found for a sequence.*"
                )
                solara.InputText(
                    label="Hold Until Date (YYYY-MM-DD)",
                    value=hold_date,
                    continuous_update=False,
                )

            with solara.Row():
                can_advance = bool(_webin_username()) and bool(_webin_password()) and (
                    study_mode.value == "new" or bool(existing_study_accession.value)
                )
                solara.Button(
                    "Next: Sequence Files →",
                    on_click=lambda: setattr(current_step, "value", 2),
                    color="primary",
                    disabled=not can_advance,
                )

        # ── Step 2: Sequence Files & Library ──────────────────────────────────
        elif current_step.value == 2:
            solara.Markdown("## Step 2: Sequence Files & Library Parameters")

            with solara.Card("Sequence Files"):
                solara.InputText(
                    label="Directory Path (local path containing sequence files)",
                    value=sequence_directory,
                    continuous_update=False,
                )
                solara.InputText(
                    label="File Pattern",
                    value=file_pattern,
                    continuous_update=False,
                )
                solara.Select(
                    label="Library Layout",
                    value=library_layout_val,
                    values=["PAIRED", "SINGLE"],
                )
                if library_layout_val.value == "PAIRED":
                    solara.InputText(
                        label="R1 Suffix (e.g. _R1, _R1_001)",
                        value=r1_suffix,
                        continuous_update=False,
                    )
                    solara.InputText(
                        label="R2 Suffix (e.g. _R2, _R2_001)",
                        value=r2_suffix,
                        continuous_update=False,
                    )

            with solara.Card("Library Parameters"):
                solara.Select(
                    label="Library Strategy",
                    value=library_strategy,
                    values=[
                        "AMPLICON", "WGS", "WGA", "WXS", "RNA-Seq", "ssRNA-seq",
                        "ChIP-Seq", "ATAC-seq", "GBS", "Ribo-Seq", "OTHER",
                    ],
                )
                solara.Select(
                    label="Library Source",
                    value=library_source,
                    values=[
                        "METAGENOMIC", "GENOMIC", "GENOMIC SINGLE CELL",
                        "TRANSCRIPTOMIC", "TRANSCRIPTOMIC SINGLE CELL",
                        "METATRANSCRIPTOMIC", "SYNTHETIC", "VIRAL RNA", "OTHER",
                    ],
                )
                solara.Select(
                    label="Library Selection",
                    value=library_selection,
                    values=[
                        "PCR", "RANDOM", "RANDOM PCR", "RT-PCR", "HMPR", "MF",
                        "cDNA", "PolyA", "MNase", "DNase",
                        "Hybrid Selection", "Reduced Representation",
                        "other", "unspecified",
                    ],
                )
                solara.Select(
                    label="Instrument Model",
                    value=instrument_model,
                    values=[
                        "Illumina NovaSeq 6000", "Illumina NovaSeq X",
                        "Illumina MiSeq", "Illumina HiSeq 2500",
                        "NextSeq 500", "NextSeq 2000",
                        "PacBio RS II", "Sequel", "Sequel II", "Sequel IIe", "Revio",
                        "MinION", "GridION", "PromethION",
                        "DNBSEQ-G400", "DNBSEQ-T7",
                        "Ion Torrent PGM", "Ion Torrent S5",
                        "unspecified",
                    ],
                )
                solara.InputText(
                    label="Design Description (optional)",
                    value=design_description,
                    continuous_update=False,
                )
                if library_layout_val.value == "PAIRED":
                    solara.InputInt(label="Nominal Insert Length (bp)", value=nominal_length)
                    solara.InputFloat(label="Nominal Standard Deviation", value=nominal_sdev)

            with solara.Row():
                solara.Button("← Back", on_click=lambda: setattr(current_step, "value", 1))
                solara.Button(
                    "Next: Verify & Lookup →",
                    on_click=lambda: setattr(current_step, "value", 3),
                    color="primary",
                    disabled=not sequence_directory.value,
                )

        # ── Step 3: Verify & Lookup ────────────────────────────────────────────
        elif current_step.value == 3:
            solara.Markdown("## Step 3: Verify & Lookup")
            solara.Markdown(
                "Click **Run Scan & Verify** to:\n"
                "1. Scan the local directory and group files into sequence entries\n"
                "2. Connect to ENA FTP and confirm each file is present on the server\n"
                "3. Compute local MD5 checksums (required for Run submission)\n"
                "4. Look up DINA material samples linked to each file via "
                "object-store + search API"
            )

            if sequence_entries.value:
                with solara.Card("Scan Results"):
                    for entry in sequence_entries.value:
                        ftp_ok = all(entry.get("on_ftp", [False]))
                        ftp_icon = "✓" if ftp_ok else "⚠"
                        dina_n = len(entry.get("dina_samples", []))
                        dina_label = (
                            f"{dina_n} DINA sample(s)"
                            if dina_n
                            else "no DINA — minimal sample"
                        )
                        file_names = ", ".join(f.name for f in entry["files"])
                        solara.Markdown(
                            f"**{entry['stem']}** | {file_names} | FTP: {ftp_icon} | {dina_label}"
                        )

            if status_messages.value:
                with solara.Card("Lookup Log"):
                    render_status_log()

            with solara.Row():
                solara.Button("← Back", on_click=lambda: setattr(current_step, "value", 2))
                solara.Button(
                    "Run Scan & Verify",
                    on_click=scan_verify_and_lookup,
                    color="primary",
                    disabled=is_processing.value,
                )

        # ── Step 4: Review ─────────────────────────────────────────────────────
        elif current_step.value == 4:
            solara.Markdown("## Step 4: Review")
            solara.Markdown("Review the planned submissions before proceeding to submit.")

            entries = sequence_entries.value
            if not entries:
                solara.Warning("No entries found — go back and run the scan first.")
            else:
                all_ftp = all(v for e in entries for v in e.get("on_ftp", [False]))
                if not all_ftp:
                    solara.Warning(
                        "⚠ Some files were not confirmed on ENA FTP. "
                        "Run submission may fail. Verify files are uploaded before proceeding."
                    )
                else:
                    solara.Success("✓ All files confirmed present on ENA FTP")

                study_label = (
                    f"Existing study: **{existing_study_accession.value}**"
                    if study_mode.value == "existing"
                    else "A new minimal study will be created"
                )
                solara.Info(f"Study: {study_label}")
                solara.Info(f"Hold date: {hold_date.value}")

                with solara.Card("Sequence Entries"):
                    for i, entry in enumerate(entries, 1):
                        files_str = ", ".join(f.name for f in entry["files"])
                        ftp_str = (
                            "✓ on FTP"
                            if all(entry.get("on_ftp", []))
                            else "⚠ not confirmed"
                        )
                        dina_n = len(entry.get("dina_samples", []))
                        if dina_n > 1:
                            sample_plan = (
                                f"{dina_n} DINA samples → submitted as SAMPLE_SET, "
                                "referenced via POOL in experiment"
                            )
                        elif dina_n == 1:
                            sample_plan = "1 DINA sample → mapped ENA sample"
                        else:
                            sample_plan = f"Minimal sample (taxon ID: {default_taxon_id.value})"
                        solara.Markdown(
                            f"**{i}. {entry['stem']}**  \n"
                            f"Files: {files_str}  \n"
                            f"FTP: {ftp_str}  \n"
                            f"Samples: {sample_plan}"
                        )

            with solara.Row():
                solara.Button(
                    "← Back (re-run scan)", on_click=lambda: setattr(current_step, "value", 3)
                )
                solara.Button(
                    "Next: Submit →",
                    on_click=lambda: setattr(current_step, "value", 5),
                    color="primary",
                    disabled=not entries or not all_ftp,
                )
            if not all_ftp:
                solara.Error(
                    "Cannot proceed: one or more files are not confirmed on ENA FTP. "
                    "Upload the missing files and re-run the scan."
                )

        # ── Step 5: Submit ─────────────────────────────────────────────────────
        elif current_step.value == 5:
            solara.Markdown("## Step 5: Submit to ENA")
            solara.Warning("⚠ This will submit data to ENA. Verify all configuration first.")

            entries = sequence_entries.value
            with solara.Card("Submission Plan"):
                solara.Markdown(
                    "1. **Study** — "
                    + (
                        f"Use existing: {existing_study_accession.value}"
                        if study_mode.value == "existing"
                        else "Create new minimal study"
                    )
                    + "\n2. **Samples** — One ENA sample (or SAMPLE_SET pool) per entry"
                    "\n3. **Experiments** — One per entry, referencing study + sample(s)"
                    "\n4. **Runs** — One per entry, referencing experiment + uploaded files"
                )
                solara.Info(f"{len(entries)} sequence entr(ies) to process")

            if status_messages.value:
                with solara.Card("Submission Progress"):
                    render_status_log()

            with solara.Row():
                solara.Button("← Back", on_click=lambda: setattr(current_step, "value", 4))
                solara.Button(
                    "Submit to ENA",
                    on_click=submit_to_ena,
                    color="primary",
                    disabled=(
                        is_processing.value
                        or not _webin_username()
                        or not entries
                    ),
                )

        # ── Step 6: Results ────────────────────────────────────────────────────
        elif current_step.value == 6:
            solara.Markdown("## Step 6: Submission Results")

            if project_accession.value:
                solara.Success(f"**Study:** {project_accession.value}")
            if project_receipt.value:
                display_receipt_details(project_receipt.value, "Study Submission Receipt")

            entries = sequence_entries.value
            if entries:
                with solara.Card("Per-Entry Accessions"):
                    for entry in entries:
                        solara.Markdown(f"**{entry['stem']}**")
                        for acc in entry.get("ena_sample_accessions", []):
                            solara.Success(f"  Sample: {acc}")
                        if entry.get("ena_experiment_accession"):
                            solara.Success(
                                f"  Experiment: {entry['ena_experiment_accession']}"
                            )
                        if entry.get("ena_run_accession"):
                            solara.Success(f"  Run: {entry['ena_run_accession']}")
                        elif entry.get("ena_experiment_accession"):
                            solara.Warning("  Run: not submitted")

            if status_messages.value:
                with solara.Card("Submission Log"):
                    render_status_log()

            def reset_workflow() -> None:
                current_step.value = 1
                status_messages.value = []
                sequence_entries.value = []
                project_accession.value = ""
                project_receipt.value = None

            with solara.Row():
                solara.Button("← Start New Submission", on_click=reset_workflow)

