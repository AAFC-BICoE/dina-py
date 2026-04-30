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

import csv
import hashlib
import importlib
import io
import json
import os
import re
import tempfile
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
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
from dinapy.ena.receipt import format_receipt_summary
from dinapy.ena.submission import ENASubmissionWorkflow
from dinapy.ena.upload import ReadUploader


# ── Status display ────────────────────────────────────────────────────────────

def _msg_color(msg_type: str) -> str:
    """Map a status message type to a display colour."""
    return {"info": "blue", "success": "green", "warning": "orange", "error": "red"}.get(
        msg_type, "grey"
    )


# ── MD5 cache helpers ──────────────────────────────────────────────────────────

def _md5_cache_path(directory: Path) -> Path:
    """Return a per-directory MD5 cache file in the system temp dir."""
    dir_hash = hashlib.md5(str(directory.resolve()).encode()).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / f"dina_md5_cache_{dir_hash}.json"


def _load_md5_cache(cache_path: Path) -> dict:
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_md5_cache(cache_path: Path, cache: dict) -> None:
    try:
        cache_path.write_text(json.dumps(cache), encoding="utf-8")
    except Exception:
        pass  # cache write failures are non-fatal


def _md5_cache_key(path: Path) -> str:
    """Cache key: absolute path + size + mtime — invalidates if file changes."""
    stat = path.stat()
    return f"{path.resolve()}:{stat.st_size}:{stat.st_mtime}"


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
    def _webin_username() -> str:
        return os.environ.get("WEBIN_USERNAME", "")
    def _webin_password() -> str:
        return os.environ.get("WEBIN_PASSWORD", "")
    def _use_test_server() -> bool:
        return os.environ.get("WEBIN_TEST", "true").lower() not in ("false", "0", "no", "off")

    study_mode = solara.use_reactive("new")           # "new" | "existing"
    existing_study_accession = solara.use_reactive("")
    new_study_name = solara.use_reactive("")
    new_study_title = solara.use_reactive("")
    new_study_description = solara.use_reactive("")
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
    # Phase-1 results: entries after directory scan + FTP check (before MD5 / DINA lookup)
    ftp_scanned_entries = solara.use_reactive([])
    # Stems the user has selected to proceed with MD5 + DINA lookup
    selected_stems = solara.use_reactive([])
    # Snapshot of status_messages captured at the end of run_md5_and_lookup;
    # preserved so Step 4 can show the scan/lookup log for inspection.
    scan_log_messages = solara.use_reactive([])
    # Step 3 list pagination / filtering
    step3_page = solara.use_reactive(0)
    step3_filter = solara.use_reactive("all")  # "all" | "ftp_ok" | "ftp_missing"
    step3_search = solara.use_reactive("")

    # ── Submit state ───────────────────────────────────────────────────────
    project_accession = solara.use_reactive("")
    project_receipt = solara.use_reactive(None)
    status_messages = solara.use_reactive([])
    is_processing = solara.use_reactive(False)
    cancel_event = solara.use_ref(threading.Event())

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
        lines = "".join(
            f"<div style='color:{_msg_color(msg_type)};white-space:pre-wrap;word-break:break-all'>"
            f"[{ts}] {msg}</div>"
            for ts, msg_type, msg in status_messages.value
        )
        solara.HTML(
            tag="div",
            unsafe_innerHTML=lines,
            style=(
                "max-height:320px;"
                "overflow-y:auto;"
                "font-family:monospace;"
                "font-size:0.82em;"
                "line-height:1.4;"
                "padding:6px 8px;"
                "background:rgba(0,0,0,0.04);"
                "border-radius:4px;"
                "border:1px solid rgba(0,0,0,0.1);"
            ),
        )

    def display_receipt_details(receipt, title: str) -> None:
        """Display detailed receipt information"""
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
    # Step 3 helpers: entry selection
    # ══════════════════════════════════════════════════════════════════════════

    def _select_all_entries() -> None:
        selected_stems.value = [e["stem"] for e in ftp_scanned_entries.value]

    def _clear_all_entries() -> None:
        selected_stems.value = []

    def _toggle_entry(stem: str, checked: bool) -> None:
        current = list(selected_stems.value)
        if checked and stem not in current:
            selected_stems.value = current + [stem]
        elif not checked and stem in current:
            selected_stems.value = [s for s in current if s != stem]

    # ══════════════════════════════════════════════════════════════════════════
    # Step 3 action — Phase 1: Scan directory + FTP check
    # ══════════════════════════════════════════════════════════════════════════

    def scan_and_check_ftp() -> None:
        """Phase 1: Scan directory, group entries, check FTP presence."""
        cancel_event.current.clear()
        is_processing.value = True
        status_messages.value = []
        ftp_scanned_entries.value = []
        selected_stems.value = []

        def _run():
            try:
                # ── 1. Scan local directory ───────────────────────────────────
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

                # ── 2. Group into sequence entries ────────────────────────────
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

                # ── 3. FTP check ──────────────────────────────────────────────
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
                except Exception as ftp_err:
                    add_status(f"FTP check failed: {ftp_err}", "warning")
                    add_status("Continuing without FTP verification", "info")

                # Populate on_ftp and stub remaining fields
                for entry in entries:
                    entry["on_ftp"] = [ftp_status.get(f.name, False) for f in entry["files"]]
                    entry["md5s"] = [None] * len(entry["files"])
                    entry["dina_samples"] = []
                    entry["attachment_uuids"] = []
                    entry.setdefault("ena_sample_accessions", [])
                    entry.setdefault("ena_experiment_alias", None)
                    entry.setdefault("ena_experiment_accession", None)
                    entry.setdefault("ena_run_alias", None)
                    entry.setdefault("ena_run_accession", None)

                ftp_scanned_entries.value = entries
                # Pre-select all entries so the user can just click Proceed if they want all
                selected_stems.value = [e["stem"] for e in entries]
                add_status(
                    f"✓ FTP check complete — {len(entries)} entr(ies) found. "
                    "Select which ones to process and click Proceed.",
                    "success",
                )

            except Exception as e:
                add_status(f"Fatal scan error: {e}", "error")
                for line in traceback.format_exc().split("\n")[-6:-1]:
                    if line.strip():
                        add_status(f"  {line}", "error")
            finally:
                is_processing.value = False

        threading.Thread(target=_run, daemon=True).start()

    # ══════════════════════════════════════════════════════════════════════════
    # Step 3 action — Phase 2: MD5 + DINA lookup for selected entries only
    # ══════════════════════════════════════════════════════════════════════════

    def run_md5_and_lookup() -> None:
        """Phase 2: Compute MD5s and look up DINA samples for selected entries."""
        cancel_event.current.clear()
        is_processing.value = True
        status_messages.value = []

        def _run():
            try:
                chosen_stems = set(selected_stems.value)
                # Deep-copy entries so we don't mutate ftp_scanned_entries
                entries = [
                    {k: list(v) if isinstance(v, list) else v for k, v in e.items()}
                    for e in ftp_scanned_entries.value
                    if e["stem"] in chosen_stems
                ]

                if not entries:
                    add_status("No entries selected — please select at least one.", "warning")
                    return

                add_status(f"Processing {len(entries)} selected entr(ies)...", "info")

                # ── MD5 computation (cache-aware, throttled status updates) ──
                _first_file = next(
                    (f for e in entries for f in e["files"]), None
                )
                _cache_path = _md5_cache_path(_first_file.parent) if _first_file else None
                _md5_cache = _load_md5_cache(_cache_path) if _cache_path else {}
                _total_md5_files = sum(
                    1 for e in entries for i, f in enumerate(e["files"]) if e["on_ftp"][i]
                )
                add_status(
                    f"Computing MD5 for {_total_md5_files} file(s) "
                    f"— cache: {_cache_path} "
                    f"({len(_md5_cache)} entr(ies) already cached)",
                    "info",
                )
                _MD5_LOG_INTERVAL = 100  # emit a progress line every N files
                md5_count = 0
                _cached_count = 0
                _computed_count = 0
                for entry in entries:
                    for i, f in enumerate(entry["files"]):
                        if not entry["on_ftp"][i]:
                            continue
                        if cancel_event.current.is_set():
                            add_status("✗ Cancelled by user.", "warning")
                            return
                        _key = _md5_cache_key(f)
                        if _key in _md5_cache:
                            entry["md5s"][i] = _md5_cache[_key]
                            _cached_count += 1
                        else:
                            try:
                                md5 = ReadUploader.compute_md5(
                                    f, cancel_event=cancel_event.current
                                )
                            except InterruptedError:
                                add_status("✗ Cancelled during MD5.", "warning")
                                return
                            entry["md5s"][i] = md5
                            _md5_cache[_key] = md5
                            if _cache_path:
                                _save_md5_cache(_cache_path, _md5_cache)
                            _computed_count += 1
                        md5_count += 1
                        if md5_count % _MD5_LOG_INTERVAL == 0 or md5_count == _total_md5_files:
                            add_status(
                                f"  MD5 progress: {md5_count}/{_total_md5_files} "
                                f"({_cached_count} cached, {_computed_count} computed)",
                                "info",
                            )
                add_status(
                    f"MD5 complete: {md5_count} file(s) "
                    f"({_cached_count} from cache, {_computed_count} newly computed)",
                    "info",
                )

                # Drop entries with files missing from FTP
                entries_before = len(entries)
                entries = [e for e in entries if all(e.get("on_ftp", []))]
                skipped = entries_before - len(entries)
                if skipped:
                    add_status(
                        f"⚠ {skipped} entr(ies) excluded — file(s) not found on FTP. "
                        f"{len(entries)} entr(ies) will proceed.",
                        "warning",
                    )
                if not entries:
                    add_status("No entries have all files confirmed on FTP — nothing to submit.", "warning")
                    return

                # ── DINA lookup ───────────────────────────────────────────────
                add_status(
                    "Looking up DINA material samples via object-store + search API...", "info"
                )
                try:
                    from dinapy.apis.objectstoreapi.objectstore_api import ObjectStoreAPI
                    from dinapy.apis.searchapi.search_api import SearchAPI
                    add_status("Initialising DINA APIs (connecting to Keycloak)...", "info")
                    object_store_api = ObjectStoreAPI()
                    search_api = SearchAPI()
                    add_status("✓ DINA APIs initialised", "success")
                    dina_available = True
                except Exception as err:
                    add_status(
                        f"DINA API unavailable ({type(err).__name__}: {err}) — "
                        "entries without DINA samples will be excluded",
                        "warning",
                    )
                    object_store_api = None
                    search_api = None
                    dina_available = False

                _LOOKUP_LOG_INTERVAL = 100
                _lookup_ok = 0        # entries with ≥1 DINA sample found
                _lookup_none = 0      # entries with no DINA sample found
                _lookup_errors = 0    # entries that hit an exception
                _n_lookup = len(entries)

                for _lookup_idx, entry in enumerate(entries, 1):
                    if cancel_event.current.is_set():
                        add_status(
                            f"✗ Cancelled by user after {_lookup_idx - 1}/{_n_lookup} entr(ies).",
                            "warning",
                        )
                        return

                    entry["dina_samples"] = []
                    entry["attachment_uuids"] = []
                    if not dina_available:
                        continue

                    seen_sample_ids: set = set()
                    _entry_ok = False
                    for f in entry["files"]:
                        try:
                            filename_no_ext = _get_objectstore_filename(f)
                            os_resp = search_api.search_object_store_by_filename(filename_no_ext)
                            os_hits = (
                                os_resp.get("hits", {}).get("hits", [])
                                if os_resp
                                else []
                            )
                            if not os_hits:
                                add_status(
                                    f"  ✗ [{entry['stem']}] No object-store record for '{filename_no_ext}'",
                                    "warning",
                                )
                                continue

                            records = [h.get("_source", {}).get("data", {}) for h in os_hits]
                            attachment_uuid = records[0].get("id")
                            if not attachment_uuid:
                                add_status(
                                    f"  ✗ [{entry['stem']}] No attachment UUID for '{filename_no_ext}'",
                                    "warning",
                                )
                                continue
                            entry["attachment_uuids"].append(attachment_uuid)

                            search_resp = search_api.search_material_samples_by_attachment(
                                attachment_uuid
                            )
                            hits = (
                                search_resp.get("hits", {}).get("hits", [])
                                if search_resp
                                else []
                            )
                            if not hits:
                                add_status(
                                    f"  ✗ [{entry['stem']}] No material samples for attachment {attachment_uuid[:8]}...",
                                    "warning",
                                )
                            else:
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
                                _entry_ok = True

                        except Exception as lookup_err:
                            add_status(
                                f"  ✗ [{entry['stem']}] Lookup error for {f.name}: {lookup_err}",
                                "warning",
                            )
                            _lookup_errors += 1

                        if _entry_ok:
                            break  # sample found from first file — skip remaining files

                    if entry["dina_samples"]:
                        _lookup_ok += 1
                    else:
                        _lookup_none += 1

                    if _lookup_idx % _LOOKUP_LOG_INTERVAL == 0 or _lookup_idx == _n_lookup:
                        add_status(
                            f"  Lookup progress: {_lookup_idx}/{_n_lookup} "
                            f"({_lookup_ok} matched, {_lookup_none} unmatched"
                            + (f", {_lookup_errors} errors" if _lookup_errors else "")
                            + ")",
                            "info",
                        )

                add_status(
                    f"DINA lookup complete — {_lookup_ok} matched, {_lookup_none} unmatched"
                    + (f", {_lookup_errors} errors" if _lookup_errors else ""),
                    "info" if _lookup_none == 0 else "warning",
                )

                # Drop entries with no DINA samples
                entries_before = len(entries)
                entries = [e for e in entries if e.get("dina_samples")]
                excluded = entries_before - len(entries)
                if excluded:
                    add_status(
                        f"⚠ {excluded} entr(ies) excluded — no DINA samples found. "
                        f"{len(entries)} entr(ies) will proceed.",
                        "warning",
                    )

                if not entries:
                    add_status("No entries have associated DINA samples — nothing to submit.", "warning")
                    return

                sequence_entries.value = entries
                add_status(f"✓ Processing complete — {len(entries)} entr(ies) ready for review", "success")
                scan_log_messages.value = list(status_messages.value)
                current_step.value = 4

            except Exception as e:
                add_status(f"Fatal error: {e}", "error")
                for line in traceback.format_exc().split("\n")[-6:-1]:
                    if line.strip():
                        add_status(f"  {line}", "error")
            finally:
                is_processing.value = False

        threading.Thread(target=_run, daemon=True).start()

    # ══════════════════════════════════════════════════════════════════════════
    # Step 5 action: Submit Study → Samples → Experiments → Runs
    # ══════════════════════════════════════════════════════════════════════════

    def submit_to_ena() -> None:
        if is_processing.value:
            return
        is_processing.value = True
        status_messages.value = []
        entries = [dict(e) for e in sequence_entries.value]

        def _run():
            import requests as _requests

            def _submit_with_retry(fn, *args, retries: int = 3, delay: float = 5.0, label: str = "", **kwargs):
                """Call fn(*args, **kwargs) up to `retries` times on ConnectionError."""
                for attempt in range(1, retries + 1):
                    try:
                        return fn(*args, **kwargs)
                    except _requests.exceptions.ConnectionError as exc:
                        if attempt == retries:
                            raise
                        add_status(
                            f"  ⚠ Connection reset{' (' + label + ')' if label else ''} "
                            f"— retry {attempt}/{retries - 1} in {delay:.0f}s…",
                            "warning",
                        )
                        time.sleep(delay)

            try:
                workflow = ENASubmissionWorkflow(
                    username=_webin_username(),
                    password=_webin_password(),
                    test=_use_test_server(),
                )
                timestamp = str(int(time.time()))
                _hold_date = hold_date.value

                # ── [1/4] Study ───────────────────────────────────────────────────
                if study_mode.value == "existing":
                    project_accession.value = existing_study_accession.value
                    add_status(
                        f"[1/4] Using existing study: {project_accession.value}", "info"
                    )
                else:
                    add_status("[1/4] Submitting study...", "info")
                    _name = new_study_name.value.strip()
                    _alias = _name.replace(" ", "_") + f"_{timestamp}"
                    _title = new_study_title.value.strip() or _name
                    _description = new_study_description.value.strip() or f"Sequencing study created from {len(entries)} sequence entr(ies)"
                    ena_project = Project(
                        alias=_alias,
                        name=_name,
                        title=_title,
                        description=_description,
                    )
                    receipt = _submit_with_retry(
                        workflow.submit_project_xml,
                        ena_project, action="ADD", hold_until_date=_hold_date,
                        label="study",
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

                # ── [2-4] Per entry: Samples → Experiment → Run ───────────────────
                # ── Imports loaded once, outside the loop ─────────────────────────
                from dinapy.apis.collectionapi.ena_helpers import prepare_sample_for_ena_mapping
                from dinapy.apis.collectionapi.materialsampleapi import MaterialSampleAPI
                import dinapy.ena.mappers.dina_to_ena.mappers_dto as _mappers_mod
                importlib.reload(_mappers_mod)
                from dinapy.ena.mappers.dina_to_ena.mappers_dto import material_sample_to_ena
                ms_api = MaterialSampleAPI()

                # ── Cache reactive values (avoid repeated lock reads in hot loop) ──
                _library_layout = library_layout_val.value
                _nominal_length = nominal_length.value
                _nominal_sdev = nominal_sdev.value
                _library_strategy = library_strategy.value
                _library_source = library_source.value
                _library_selection = library_selection.value
                _desc_text = design_description.value or f"{library_strategy.value} sequencing"
                _instrument_model = instrument_model.value
                _project_acc = project_accession.value

                # ── Parallel pre-fetch of all DINA sample records ─────────────────
                _all_sample_ids = {
                    dina_s.get("id")
                    for entry in entries
                    for dina_s in entry.get("dina_samples", [])
                    if dina_s.get("id")
                }
                _dina_fetch_cache: dict = {}
                if _all_sample_ids:
                    def _fetch_one_sample(sid: str):
                        try:
                            r = ms_api.get_req_dina(
                                f"{ms_api.base_url}/{sid}",
                                {"include": "collectingEvent,organism"},
                            )
                            j = r.json() if hasattr(r, "json") else r
                            return sid, j.get("data"), j.get("included", []), None
                        except Exception as _err:
                            return sid, None, None, _err

                    add_status(
                        f"Pre-fetching {len(_all_sample_ids)} DINA sample record(s) in parallel...",
                        "info",
                    )
                    _n_fetched = 0
                    _n_fetch_errors = 0
                    with ThreadPoolExecutor(max_workers=8) as _pool:
                        _futures = {
                            _pool.submit(_fetch_one_sample, sid): sid
                            for sid in _all_sample_ids
                        }
                        for fut in as_completed(_futures):
                            sid, data, included, err = fut.result()
                            _n_fetched += 1
                            if data is not None:
                                _dina_fetch_cache[sid] = (data, included)
                            else:
                                _n_fetch_errors += 1
                                add_status(
                                    f"  Pre-fetch failed for sample {sid[:8]}: {err}", "error"
                                )
                            if _n_fetched % 100 == 0 or _n_fetched == len(_all_sample_ids):
                                add_status(
                                    f"  Pre-fetching: {_n_fetched}/{len(_all_sample_ids)}"
                                    + (f" ({_n_fetch_errors} errors)" if _n_fetch_errors else ""),
                                    "info",
                                )
                    add_status(
                        f"✓ Pre-fetch complete — {len(_dina_fetch_cache)}/{len(_all_sample_ids)} cached"
                        + (f", {_n_fetch_errors} failed" if _n_fetch_errors else ""),
                        "success" if not _n_fetch_errors else "warning",
                    )

                def _valid_sample_acc(acc: str | None) -> str | None:
                    """Return acc only if it is a real sample accession (ERS/SAMEA), not an ERA wrapper."""
                    return acc if acc and not acc.startswith("ERA") else None

                _SUBMIT_LOG_INTERVAL = 100
                total = len(entries)
                _ok_samples = 0
                _ok_experiments = 0
                _ok_runs = 0
                _skipped = 0
                _already_complete = 0
                add_status(f"Submitting {total} entr(ies)...", "info")
                for idx, entry in enumerate(entries, 1):
                    stem = entry["stem"]
                    if idx == 1 or idx % _SUBMIT_LOG_INTERVAL == 0 or idx == total:
                        add_status(f"  Progress: {idx}/{total} entries processed...", "info")

                    # ── Skip entries that were fully submitted in a prior run ──
                    if entry.get("ena_run_accession"):
                        _already_complete += 1
                        continue

                    # ── [2] Samples ───────────────────────────────────────────
                    # Each entry in sample_refs is (accession_or_None, alias).
                    # When ENA "already exists" returns an ERA submission accession
                    # instead of a real ERS/SAMEA accession, we store None and fall
                    # back to refname (the stable DINA UUID alias) in the design.
                    sample_refs: List[tuple] = []  # list of (accession|None, alias)
                    dina_samples = entry.get("dina_samples", [])

                    if dina_samples:
                        ena_samples: List[Sample] = []
                        for dina_s in dina_samples:
                            sample_id = dina_s.get("id", "?")
                            try:
                                cached = _dina_fetch_cache.get(sample_id)
                                if not cached:
                                    raise ValueError(
                                        f"DINA API returned no data for sample id={sample_id}"
                                    )
                                full_sample_data, full_included = cached
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
                                # Keep the DINA UUID as the alias — stable across re-runs,
                                # so ENA can detect already-registered samples by alias.
                                ena_samples.append(ena_s)
                            except Exception as map_err:
                                add_status(
                                    f"  Mapping error for DINA sample {sample_id[:8]}: {map_err} — skipping entry",
                                    "error",
                                )
                                raise Exception(
                                    f"Could not map DINA sample {sample_id[:8]} for {stem}: {map_err}"
                                )
                    else:
                        _skipped += 1
                        continue

                    if len(ena_samples) == 1:
                        receipt = _submit_with_retry(
                            workflow.submit_sample_xml,
                            ena_samples[0],
                            action="ADD",
                            hold_until_date=_hold_date,
                            label=f"sample {stem}",
                        )
                        if receipt.success:
                            acc = receipt.get_accession("SAMPLE")
                            sample_refs.append((_valid_sample_acc(acc), ena_samples[0].alias))
                            _ok_samples += 1
                        else:
                            errs = receipt.get_errors()
                            # ENA "already exists" error returns the ERA submission accession,
                            # not the real ERS/SAMEA accession — use alias (refname) instead.
                            if any("already exists" in e for e in errs):
                                sample_refs.append((None, ena_samples[0].alias))
                                entry["ena_samples_linked"] = True
                                _ok_samples += 1
                            else:
                                for err in errs:
                                    add_status(f"Sample error ({stem}): {err}", "error")
                                raise Exception(f"Sample submission failed for {stem}")
                    else:
                        receipt = _submit_with_retry(
                            workflow.submit_samples_xml,
                            ena_samples,
                            action="ADD",
                            hold_until_date=_hold_date,
                            label=f"sample set {stem}",
                        )
                        if receipt.success:
                            # Match returned accessions to aliases by alias field
                            alias_to_acc = {
                                obj.alias: obj.accession
                                for obj in receipt.objects
                                if obj.accession and obj.alias
                            }
                            for ena_s in ena_samples:
                                raw_acc = alias_to_acc.get(ena_s.alias)
                                sample_refs.append((_valid_sample_acc(raw_acc), ena_s.alias))
                            _ok_samples += len(ena_samples)
                        else:
                            errs = receipt.get_errors()
                            if any("already exists" in e for e in errs):
                                # All samples already registered — use aliases as refnames
                                for ena_s in ena_samples:
                                    sample_refs.append((None, ena_s.alias))
                                entry["ena_samples_linked"] = True
                                _ok_samples += len(ena_samples)
                            else:
                                for err in errs:
                                    add_status(f"Sample set error ({stem}): {err}", "error")
                                raise Exception(f"Sample set submission failed for {stem}")

                    entry["ena_sample_accessions"] = [
                        acc for acc, _ in sample_refs if acc
                    ] or [alias for _, alias in sample_refs]

                    # ── [3] Experiment ─────────────────────────────────────────
                    exp_alias = f"exp_{stem}"

                    lib_layout = LibraryLayout(
                        layout_type=_library_layout,
                        nominal_length=_nominal_length if _library_layout == "PAIRED" else None,
                        nominal_sdev=_nominal_sdev if _library_layout == "PAIRED" else None,
                    )
                    lib_desc = LibraryDescriptor(
                        library_strategy=_library_strategy,
                        library_source=_library_source,
                        library_selection=_library_selection,
                        library_layout=lib_layout,
                    )

                    if len(sample_refs) > 1:
                        design = Design(
                            design_description=_desc_text,
                            sample_pool=[
                                PoolMember(
                                    accession=acc if acc else None,
                                    refname=alias if not acc else None,
                                    member_name=f"member_{i + 1}",
                                )
                                for i, (acc, alias) in enumerate(sample_refs)
                            ],
                            library_descriptor=lib_desc,
                        )
                    else:
                        acc, alias = sample_refs[0]
                        design = Design(
                            design_description=_desc_text,
                            sample_descriptor=(
                                ObjectRef(accession=acc)
                                if acc
                                else ObjectRef(refname=alias)
                            ),
                            library_descriptor=lib_desc,
                        )

                    ena_experiment = Experiment(
                        alias=exp_alias,
                        title=f"Sequencing experiment for {stem}",
                        study_ref=ObjectRef(accession=_project_acc),
                        design=design,
                        platform=Platform(instrument_model=_instrument_model),
                    )
                    receipt = _submit_with_retry(
                        workflow.submit_experiment,
                        ena_experiment, action="ADD",
                        label=f"experiment {stem}",
                    )
                    if receipt.success:
                        exp_acc = receipt.get_accession("EXPERIMENT")
                        entry["ena_experiment_alias"] = exp_alias
                        entry["ena_experiment_accession"] = exp_acc
                        _ok_experiments += 1
                    else:
                        errs = receipt.get_errors()
                        # ENA "already exists" error for experiments reports the
                        # submission (ERA...) accession, not the experiment (ERX...)
                        # accession.  Detect the already-exists condition and fall
                        # back to alias-based resolution in the run step instead.
                        _already_exists = any("already exists" in e for e in errs)
                        if _already_exists:
                            entry["ena_experiment_alias"] = exp_alias
                            entry["ena_experiment_accession"] = None  # use refname below
                            _ok_experiments += 1
                        else:
                            for err in errs:
                                add_status(f"Experiment error ({stem}): {err}", "error")
                            raise Exception(f"Experiment submission failed for {stem}")

                    # ── [4] Run ────────────────────────────────────────────────
                    run_alias = f"run_{stem}"
                    run_files = [
                        ENAFile(
                            filename=f.name,
                            filetype="fastq",
                            checksum_method="MD5",
                            checksum=md5,
                        )
                        for f, md5 in zip(entry["files"], entry["md5s"])
                    ]
                    # Prefer accession (ERX...) when available; fall back to stable alias
                    # when the experiment already existed and ENA only returned an ERA
                    # (submission-level) accession rather than the ERX accession.
                    _exp_acc = entry.get("ena_experiment_accession")
                    _exp_ref = (
                        ObjectRef(accession=_exp_acc)
                        if _exp_acc and not _exp_acc.startswith("ERA")
                        else ObjectRef(refname=entry["ena_experiment_alias"])
                    )
                    ena_run = Run(
                        alias=run_alias,
                        title=f"Run for {stem}",
                        experiment_ref=_exp_ref,
                        data_blocks=[DataBlock(files=run_files)],
                    )
                    receipt = _submit_with_retry(
                        workflow.submit_run,
                        ena_run, action="ADD",
                        label=f"run {stem}",
                    )
                    if receipt.success:
                        run_acc = receipt.get_accession("RUN")
                        entry["ena_run_alias"] = run_alias
                        entry["ena_run_accession"] = run_acc
                        _ok_runs += 1
                        # Checkpoint: flush accessions periodically so progress isn't lost on failure
                        if idx % _SUBMIT_LOG_INTERVAL == 0:
                            sequence_entries.value = list(entries)
                    else:
                        errs = receipt.get_errors()
                        # Pattern 1: ENA reports the existing run accession directly
                        #   e.g. "The run files have been submitted in ERR1234567"
                        _existing_run = next(
                            (m.group(1) for e in errs
                             for m in [re.search(r'submitted in (ERR[0-9]+)', e)] if m),
                            None,
                        )
                        # Pattern 2: ENA reports the submission wrapper accession (ERA)
                        #   e.g. "already exists in the submission account with accession: "ERA36099119""
                        # ERA is the submission-level accession, not the ERR — we can't
                        # recover the actual run accession from this, so we store the alias
                        # only and mark the entry as already registered.
                        _already_registered = not _existing_run and any(
                            "already exists in the submission account" in e for e in errs
                        )
                        if _existing_run:
                            entry["ena_run_alias"] = run_alias
                            entry["ena_run_accession"] = _existing_run
                            _ok_runs += 1
                            if idx % _SUBMIT_LOG_INTERVAL == 0:
                                sequence_entries.value = list(entries)
                        elif _already_registered:
                            entry["ena_run_alias"] = run_alias
                            # ERR not recoverable from ERA — leave accession blank so the
                            # results page shows it as "already registered, ERR unknown"
                            entry.setdefault("ena_run_accession", None)
                            _ok_runs += 1
                            add_status(
                                f"  Run for {stem} already registered in ENA (ERR accession not returned)",
                                "info",
                            )
                        else:
                            for err in errs:
                                add_status(f"Run error ({stem}): {err}", "error")
                            add_status(
                                f"Run submission failed for {stem} — experiment and samples are registered",
                                "warning",
                            )

                sequence_entries.value = entries
                skip_str = f", {_skipped} skipped (no DINA samples)" if _skipped else ""
                complete_str = f", {_already_complete} already complete (skipped)" if _already_complete else ""
                add_status(
                    f"✓ Submission complete — {_ok_runs} runs, {_ok_experiments} experiments, "
                    f"{_ok_samples} samples submitted{skip_str}{complete_str}",
                    "success",
                )
                current_step.value = 6

            except Exception as e:
                add_status(f"Fatal submission error: {e}", "error")
                for line in traceback.format_exc().split("\n")[-6:-1]:
                    if line.strip():
                        add_status(f"  {line}", "error")
            finally:
                is_processing.value = False

        threading.Thread(target=_run, daemon=True).start()


    # ══════════════════════════════════════════════════════════════════════════
    # Main layout
    # ══════════════════════════════════════════════════════════════════════════
    # min-height keeps the cell output a consistent size between steps so the
    # notebook doesn't jump/scroll when the GUI re-renders.
    with solara.Card(title="ENA Submission Workflow", elevation=2,
                     style="min-height: 900px;"):
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
                    solara.InputText(
                        label="Study Name (required)",
                        value=new_study_name,
                        continuous_update=False,
                    )
                    solara.InputText(
                        label="Study Title",
                        value=new_study_title,
                        continuous_update=False,
                    )
                    solara.InputText(
                        label="Study Description",
                        value=new_study_description,
                        continuous_update=False,
                    )
                    if new_study_name.value:
                        _preview_alias = new_study_name.value.strip().replace(" ", "_") + "_<timestamp>"
                        solara.Info(f"Alias will be: `{_preview_alias}`")
                    else:
                        solara.Warning("A study name is required to proceed.")

            with solara.Card("Defaults"):
                solara.InputText(
                    label="Hold Until Date (YYYY-MM-DD)",
                    value=hold_date,
                    continuous_update=False,
                )

            with solara.Row():
                can_advance = bool(_webin_username()) and bool(_webin_password()) and (
                    (study_mode.value == "new" and bool(new_study_name.value))
                    or (study_mode.value == "existing" and bool(existing_study_accession.value))
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

            has_scan_results = bool(ftp_scanned_entries.value)

            if has_scan_results and not is_processing.value:
                # ── Selection UI (phase 1 done, awaiting user choice) ─────────
                _all_entries = ftp_scanned_entries.value
                _n_total = len(_all_entries)
                _n_ftp_ok = sum(1 for e in _all_entries if all(e.get("on_ftp", [False])))
                _n_ftp_missing = _n_total - _n_ftp_ok
                _n_selected = len(selected_stems.value)

                solara.Markdown(
                    f"FTP check complete — **{_n_total}** entr(ies) found: "
                    f"✓ {_n_ftp_ok} on FTP, ⚠ {_n_ftp_missing} missing. "
                    f"**{_n_selected} selected.** "
                    f"Select entries to process (MD5 + DINA lookup)."
                )

                _PAGE_SIZE = 100

                # ── Apply search filter ───────────────────────────────────────
                _search_q = step3_search.value.strip().lower()
                _filt = step3_filter.value
                _visible = [
                    e for e in _all_entries
                    if (_filt == "all"
                        or (_filt == "ftp_ok" and all(e.get("on_ftp", [False])))
                        or (_filt == "ftp_missing" and not all(e.get("on_ftp", [False]))))
                    and (_search_q == "" or _search_q in e["stem"].lower())
                ]
                _n_visible = len(_visible)
                _n_pages = max(1, (_n_visible + _PAGE_SIZE - 1) // _PAGE_SIZE)
                _page = min(step3_page.value, _n_pages - 1)
                _page_entries = _visible[_page * _PAGE_SIZE: (_page + 1) * _PAGE_SIZE]

                with solara.Card("Sequence Entries"):
                    # ── Toolbar row ───────────────────────────────────────────
                    with solara.Row():
                        solara.Button("Select All", on_click=_select_all_entries)
                        solara.Button("Clear All", on_click=_clear_all_entries)
                        def _select_page():
                            cur = set(selected_stems.value)
                            cur.update(e["stem"] for e in _page_entries)
                            selected_stems.value = list(cur)
                        def _deselect_page():
                            page_stems = {e["stem"] for e in _page_entries}
                            selected_stems.value = [s for s in selected_stems.value if s not in page_stems]
                        solara.Button("Select Page", on_click=_select_page)
                        solara.Button("Deselect Page", on_click=_deselect_page)

                    # ── Filter + search row ───────────────────────────────────
                    with solara.Row():
                        solara.InputText(
                            label="Search stem",
                            value=step3_search,
                            continuous_update=True,
                            style="max-width:280px;",
                            on_value=lambda _: setattr(step3_page, "value", 0),
                        )
                        for _label, _key in [("All", "all"), ("FTP ✓", "ftp_ok"), ("FTP ⚠", "ftp_missing")]:
                            _is_active = step3_filter.value == _key
                            def _set_filt(k=_key):
                                step3_filter.value = k
                                step3_page.value = 0
                            solara.Button(
                                _label,
                                on_click=_set_filt,
                                color="primary" if _is_active else "default",
                                style="min-width:80px;",
                            )

                    solara.HTML(tag="hr")

                    # ── Entry rows for current page only ──────────────────────
                    solara.Markdown(
                        f"Showing **{len(_page_entries)}** of **{_n_visible}** "
                        f"(page {_page + 1} / {_n_pages})"
                    )
                    for entry in _page_entries:
                        _stem = entry["stem"]
                        ftp_ok = all(entry.get("on_ftp", [False]))
                        ftp_icon = "✓" if ftp_ok else "⚠"
                        file_names = ", ".join(f.name for f in entry["files"])
                        is_checked = _stem in selected_stems.value

                        def _toggle(val, s=_stem):
                            _toggle_entry(s, val)

                        with solara.Row():
                            solara.Checkbox(value=is_checked, on_value=_toggle, label="")
                            solara.Markdown(
                                f"**{_stem}** — {file_names} &nbsp;&nbsp; FTP: {ftp_icon}"
                            )

                    # ── Pagination controls ───────────────────────────────────
                    if _n_pages > 1:
                        solara.HTML(tag="hr")
                        with solara.Row():
                            solara.Button(
                                "◀ Prev",
                                on_click=lambda: setattr(step3_page, "value", max(0, _page - 1)),
                                disabled=_page == 0,
                            )
                            solara.Markdown(f"Page **{_page + 1}** / {_n_pages}")
                            solara.Button(
                                "Next ▶",
                                on_click=lambda: setattr(step3_page, "value", min(_n_pages - 1, _page + 1)),
                                disabled=_page >= _n_pages - 1,
                            )

                if status_messages.value:
                    with solara.Card("Scan Log"):
                        render_status_log()

                with solara.Row():
                    solara.Button("← Back", on_click=lambda: setattr(current_step, "value", 2))
                    solara.Button(
                        "Re-scan",
                        on_click=scan_and_check_ftp,
                        disabled=is_processing.value,
                    )
                    solara.Button(
                        f"Proceed with {_n_selected} Selected →",
                        on_click=run_md5_and_lookup,
                        color="primary",
                        disabled=_n_selected == 0 or is_processing.value,
                    )
                    if is_processing.value:
                        solara.Button(
                            "Cancel",
                            on_click=lambda: cancel_event.current.set(),
                            color="error",
                        )

            else:
                # ── Initial state or phase 1/2 in progress ────────────────────
                if not is_processing.value:
                    solara.Markdown(
                        "Click **Scan & Check FTP** to:\n"
                        "1. Scan the local directory and group files into sequence entries\n"
                        "2. Connect to ENA FTP and confirm which files are present\n\n"
                        "You will then select which entries to process."
                    )

                if status_messages.value:
                    with solara.Card("Log"):
                        render_status_log()

                with solara.Row():
                    solara.Button("← Back", on_click=lambda: setattr(current_step, "value", 2))
                    solara.Button(
                        "Scan & Check FTP",
                        on_click=scan_and_check_ftp,
                        color="primary",
                        disabled=is_processing.value,
                    )
                    if is_processing.value:
                        solara.Button(
                            "Cancel",
                            on_click=lambda: cancel_event.current.set(),
                            color="error",
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
                    else (
                        f"New study: **{new_study_name.value}**"
                        + (f" — title: *{new_study_title.value}*" if new_study_title.value else "")
                    )
                )
                solara.Info(f"Study: {study_label}")
                solara.Info(f"Hold date: {hold_date.value}")

                # ── Summary card ──────────────────────────────────────────────
                _n_entries = len(entries)
                _n_single = sum(1 for e in entries if len(e.get("dina_samples", [])) == 1)
                _n_pool   = sum(1 for e in entries if len(e.get("dina_samples", [])) > 1)
                _n_no_dina = sum(1 for e in entries if not e.get("dina_samples"))
                _total_samples = sum(len(e.get("dina_samples", [])) for e in entries)
                _n_ftp_missing = sum(
                    1 for e in entries if not all(e.get("on_ftp", [False]))
                )

                with solara.Card("Submission Summary"):
                    solara.Markdown(
                        f"| | |\n"
                        f"|---|---|\n"
                        f"| Sequence entries | **{_n_entries}** |\n"
                        f"| DINA samples mapped | **{_total_samples}** |\n"
                        f"| Single-sample entries | **{_n_single}** |\n"
                        f"| Multi-sample (POOL) entries | **{_n_pool}** |\n"
                        + (f"| ⚠ Entries with FTP issues | **{_n_ftp_missing}** |\n" if _n_ftp_missing else "")
                        + (f"| ⚠ Entries with no DINA samples | **{_n_no_dina}** |\n" if _n_no_dina else "")
                    )

                # ── Collapsible per-entry detail ─────────────────────────────
                _issues = [
                    e for e in entries
                    if not e.get("dina_samples") or not all(e.get("on_ftp", [False]))
                ]
                if _issues:
                    with solara.Details(summary=f"⚠ {len(_issues)} entr(ies) with issues"):
                        with solara.Card():
                            for entry in _issues:
                                ftp_ok = all(entry.get("on_ftp", [False]))
                                dina_n = len(entry.get("dina_samples", []))
                                flags = []
                                if not ftp_ok:
                                    flags.append("files not on FTP")
                                if dina_n == 0:
                                    flags.append("no DINA samples")
                                solara.Markdown(
                                    f"- **{entry['stem']}** — {', '.join(flags)}"
                                )

            if scan_log_messages.value:
                with solara.Details(summary="Step 3 Scan / Lookup Log"):
                    with solara.Card():
                        lines = "".join(
                            f"<div style='color:{_msg_color(msg_type)};white-space:pre-wrap;word-break:break-all'>"
                            f"[{ts}] {msg}</div>"
                            for ts, msg_type, msg in scan_log_messages.value
                        )
                        solara.HTML(
                            tag="div",
                            unsafe_innerHTML=lines,
                            style=(
                                "max-height:320px;"
                                "overflow-y:auto;"
                                "font-family:monospace;"
                                "font-size:0.82em;"
                                "line-height:1.4;"
                                "padding:6px 8px;"
                            ),
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
                _submitted = [
                    e for e in entries if e.get("ena_experiment_accession")
                ]
                # Pre-existing: run already in ENA but experiment not tracked
                # (all three objects were already registered in a prior session)
                _pre_existing = [
                    e for e in entries
                    if e.get("ena_run_accession") and not e.get("ena_experiment_accession")
                ]
                _failed = [
                    e for e in entries
                    if not e.get("ena_experiment_accession") and not e.get("ena_run_accession")
                ]
                _total_samples = sum(
                    len(e.get("ena_sample_accessions", [])) for e in _submitted
                )
                _linked_samples = sum(
                    1 for e in _submitted if e.get("ena_samples_linked")
                )

                with solara.Card("Results Summary"):
                    solara.Markdown(
                        f"| | |\n"
                        f"|---|---|\n"
                        f"| Entries submitted | **{len(_submitted)}** / {len(entries)} |\n"
                        f"| ENA samples submitted | **{_total_samples}** |\n"
                        + (f"| Samples linked (already in ENA) | **{_linked_samples}** |\n" if _linked_samples else "")
                        + f"| Study accession | **{project_accession.value or 'N/A'}** |\n"
                        + (f"| Already in ENA (skipped) | **{len(_pre_existing)}** |\n" if _pre_existing else "")
                        + (f"| ⚠ Entries not submitted | **{len(_failed)}** |\n" if _failed else "")
                    )

                # ── CSV generation + download ─────────────────────────────────
                def _make_csv() -> bytes:
                    buf = io.StringIO()
                    writer = csv.writer(buf)
                    writer.writerow([
                        "stem",
                        "dina_sample_uuids",
                        "project_accession",
                        "ena_sample_accessions",
                        "ena_experiment_accession",
                        "ena_run_accession",
                    ])
                    for e in entries:
                        dina_ids = "|".join(
                            s.get("id", "") for s in e.get("dina_samples", [])
                        )
                        writer.writerow([
                            e["stem"],
                            dina_ids,
                            project_accession.value or "",
                            "|".join(e.get("ena_sample_accessions", [])),
                            e.get("ena_experiment_accession") or "",
                            e.get("ena_run_accession") or "",
                        ])
                    return buf.getvalue().encode("utf-8")

                solara.FileDownload(
                    _make_csv,
                    filename="ena_accessions.csv",
                    label="⬇ Download accessions CSV",
                )

                if _pre_existing:
                    with solara.Details(summary=f"ℹ {len(_pre_existing)} entr(ies) already in ENA"):
                        with solara.Card():
                            solara.Markdown(
                                "These entries were already fully registered in ENA "
                                "(run already existed). Nothing new was submitted."
                            )
                            for e in _pre_existing:
                                solara.Markdown(f"- **{e['stem']}** — Run: `{e['ena_run_accession']}`")

                if _failed:
                    with solara.Details(summary=f"⚠ {len(_failed)} entr(ies) not submitted"):
                        with solara.Card():
                            for e in _failed:
                                solara.Markdown(f"- **{e['stem']}**")

                def _is_dina_uuid(s: str) -> bool:
                    """True when s looks like a DINA UUID (fallback alias, not a real ENA accession)."""
                    return bool(re.match(
                        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
                        s, re.IGNORECASE,
                    ))

                with solara.Details(summary=f"All {len(entries)} accessions (click to expand)"):
                    with solara.Card():
                        for entry in entries:
                            run_acc = entry.get("ena_run_accession")
                            exp_acc = entry.get("ena_experiment_accession")
                            if run_acc and not exp_acc:
                                # Pre-existing — no new objects registered this session
                                solara.Markdown(
                                    f"**{entry['stem']}** *(already in ENA)* &nbsp; "
                                    f"Run: `{run_acc}`"
                                )
                            else:
                                raw_accs = entry.get("ena_sample_accessions", [])
                                real_accs = [a for a in raw_accs if not _is_dina_uuid(a)]
                                if real_accs:
                                    samples_str = ", ".join(real_accs)
                                elif entry.get("ena_samples_linked"):
                                    samples_str = "*linked (existing)*"
                                else:
                                    samples_str = "—"
                                exp_str = exp_acc or "—"
                                run_str = run_acc or "—"
                                solara.Markdown(
                                    f"**{entry['stem']}**  "
                                    f"Sample(s): `{samples_str}` &nbsp; "
                                    f"Exp: `{exp_str}` &nbsp; "
                                    f"Run: `{run_str}`"
                                )

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


@solara.component
def StudyActionPanel():
    """
    Standalone panel for applying lifecycle actions to an existing ENA study.

    Supported actions (based on ActionType in models):
    - HOLD    – Update the hold/embargo date for a study.
    - RELEASE – Immediately release held data (make it publicly available).
    - CANCEL  – Cancel a previously submitted study.
    - VALIDATE – Validate the action without persisting changes to ENA.

    Credentials are read from the WEBIN_USERNAME, WEBIN_PASSWORD, and
    WEBIN_TEST environment variables (same as ENAWorkflowGUI).

    Usage::

        >>> from dinapy.ena.workflow_gui import StudyActionPanel
        >>> StudyActionPanel()
    """

    def _webin_username() -> str:
        return os.environ.get("WEBIN_USERNAME", "")

    def _webin_password() -> str:
        return os.environ.get("WEBIN_PASSWORD", "")

    def _env_test_server() -> bool:
        return os.environ.get("WEBIN_TEST", "true").lower() not in (
            "false", "0", "no", "off"
        )

    # ── Component state ───────────────────────────────────────────────────
    study_accession = solara.use_reactive("")
    selected_action = solara.use_reactive("RELEASE")
    new_hold_date = solara.use_reactive(date.today().isoformat())
    is_processing = solara.use_reactive(False)
    status_messages = solara.use_reactive([])
    result_receipt = solara.use_reactive(None)

    AVAILABLE_ACTIONS = ["HOLD", "RELEASE", "CANCEL", "VALIDATE"]
    ACTION_DESCRIPTIONS = {
        "HOLD":     "Update the hold/embargo date for this study.",
        "RELEASE":  "Release held data immediately (make it publicly available).",
        "CANCEL":   "Cancel this previously submitted study.",
        "VALIDATE": "Validate the action without persisting any changes to ENA.",
    }

    # ── Helpers ───────────────────────────────────────────────────────────
    def add_status(message: str, msg_type: str = "info") -> None:
        ts = time.strftime("%H:%M:%S")
        status_messages.value = status_messages.value + [(ts, msg_type, message)]

    def render_status_log() -> None:
        lines = "".join(
            f"<div style='color:{_msg_color(t)};white-space:pre-wrap;word-break:break-all'>"
            f"[{ts}] {msg}</div>"
            for ts, t, msg in status_messages.value
        )
        solara.HTML(
            tag="div",
            unsafe_innerHTML=lines,
            style=(
                "max-height:240px;overflow-y:auto;font-family:monospace;"
                "font-size:0.82em;line-height:1.4;padding:6px 8px;"
                "background:rgba(0,0,0,0.04);border-radius:4px;"
                "border:1px solid rgba(0,0,0,0.1);"
            ),
        )

    # ── Action handler ────────────────────────────────────────────────────
    def apply_action() -> None:
        is_processing.value = True
        status_messages.value = []
        result_receipt.value = None

        acc = study_accession.value.strip()
        action = selected_action.value
        hold_date = new_hold_date.value.strip() if action == "HOLD" else None

        try:
            if not acc:
                add_status("Study accession is required.", "error")
                return
            if not _webin_username() or not _webin_password():
                add_status(
                    "Webin credentials not found. "
                    "Set WEBIN_USERNAME and WEBIN_PASSWORD environment variables.",
                    "error",
                )
                return
            if action == "HOLD" and not hold_date:
                add_status("A hold date is required for the HOLD action.", "error")
                return

            server_label = "test (wwwdev)" if _env_test_server() else "production"
            add_status(
                f"Applying {action} to study {acc} on {server_label} server...", "info"
            )

            workflow = ENASubmissionWorkflow(
                username=_webin_username(),
                password=_webin_password(),
                test=_env_test_server(),
            )

            receipt = workflow.update_study_action(
                accession=acc,
                action=action,
                hold_until_date=hold_date,
            )

            result_receipt.value = receipt

            if receipt.success:
                add_status(
                    f"✓ Action {action} applied successfully to {acc}.", "success"
                )
                for info in receipt.get_info():
                    add_status(f"  {info}", "info")
                for warn in receipt.get_warnings():
                    add_status(f"  Warning: {warn}", "warning")
            else:
                add_status(f"✗ Action {action} failed.", "error")
                for err in receipt.get_errors():
                    add_status(f"  ENA: {err}", "error")
                # Show submission XML sent to ENA (attached by update_study_action)
                sub_xml = getattr(receipt, "_submission_xml", None)
                if sub_xml:
                    add_status("── Submission XML sent ──", "info")
                    for line in sub_xml.strip().splitlines():
                        add_status(line, "info")
                # Show raw ENA response so full error text is always visible
                raw_text = getattr(receipt, "raw_text", "")
                if raw_text:
                    add_status("── Raw ENA response ──", "warning")
                    for line in raw_text.strip().splitlines():
                        add_status(line, "warning")

        except ValueError as ve:
            add_status(f"Validation error: {ve}", "error")
        except Exception as e:
            import requests as _requests
            # requests.HTTPError carries the raw server response — show it
            http_resp = getattr(e, "response", None)
            if http_resp is not None:
                add_status(
                    f"HTTP {http_resp.status_code} error from ENA.", "error"
                )
                add_status("── Raw ENA response ──", "warning")
                for line in http_resp.text.strip().splitlines():
                    add_status(line, "warning")
                # Also show what was sent
                sub_xml = getattr(e, "_submission_xml", None)
                if sub_xml:
                    add_status("── Submission XML sent ──", "info")
                    for line in sub_xml.strip().splitlines():
                        add_status(line, "info")
            else:
                add_status(f"Error: {e}", "error")
                for line in traceback.format_exc().split("\n")[-6:-1]:
                    if line.strip():
                        add_status(f"  {line}", "error")
        finally:
            is_processing.value = False

    # ── Layout ────────────────────────────────────────────────────────────
    with solara.Card(title="Study / Project Action", elevation=2):
        solara.Markdown(
            "Apply a lifecycle action (HOLD, RELEASE, CANCEL, VALIDATE) "
            "to an **existing** ENA study using its project accession."
        )

        # Credentials status
        with solara.Card("Webin Credentials"):
            if _webin_username():
                solara.Success(f"✓ Logged in as: {_webin_username()}")
            else:
                solara.Warning(
                    "No Webin credentials detected. "
                    "Set WEBIN_USERNAME and WEBIN_PASSWORD as environment variables."
                )
            if _env_test_server():
                solara.Info("Server: Test (wwwdev.ebi.ac.uk) — submissions are not permanent")
            else:
                solara.Warning("Server: Production (webin.ebi.ac.uk) — submissions are permanent")
            solara.Markdown(
                "_Server is controlled by the `WEBIN_TEST` environment variable._"
            )

        solara.HTML(tag="hr")

        # Inputs
        solara.InputText(
            label="Study / Project Accession (e.g. PRJEB12345)",
            value=study_accession,
            continuous_update=False,
        )

        solara.Select(
            label="Action",
            value=selected_action,
            values=AVAILABLE_ACTIONS,
        )

        solara.Info(ACTION_DESCRIPTIONS.get(selected_action.value, ""))

        if selected_action.value == "HOLD":
            solara.InputText(
                label="New Hold Until Date (YYYY-MM-DD)",
                value=new_hold_date,
                continuous_update=False,
            )

        can_submit = (
            bool(study_accession.value.strip())
            and bool(_webin_username())
            and bool(_webin_password())
            and not is_processing.value
        )

        with solara.Row():
            solara.Button(
                f"Apply {selected_action.value}",
                on_click=apply_action,
                color="primary",
                disabled=not can_submit,
            )

        # Status log
        if status_messages.value:
            with solara.Card("Result Log"):
                render_status_log()

        # Receipt details
        if result_receipt.value:
            receipt = result_receipt.value
            with solara.Card("Receipt"):
                if receipt.success:
                    solara.Success("✓ Action completed successfully")
                else:
                    solara.Error("✗ Action failed")
                if receipt.objects:
                    solara.Markdown("**Accessions:**")
                    for obj in receipt.objects:
                        if obj.accession:
                            solara.Markdown(
                                f"- {obj.object_type}: `{obj.accession}`"
                                + (f" (status: {obj.status})" if obj.status else "")
                            )
                with solara.Details("View Full Receipt"):
                    summary = format_receipt_summary(receipt)
                    solara.Markdown(f"```\n{summary}\n```")


@solara.component
def FTPUploadPanel():
    """
    Standalone panel for listing, checking, and uploading sequence files to
    the ENA Webin FTP server before running an ENA submission.

    Credentials are read from the WEBIN_USERNAME, WEBIN_PASSWORD, and
    WEBIN_TEST environment variables (same as ENAWorkflowGUI).

    Usage::

        >>> from dinapy.ena.workflow_gui import FTPUploadPanel
        >>> FTPUploadPanel()
    """

    from dinapy.ena.upload import ReadUploader

    # ── Credential helpers ────────────────────────────────────────────────
    def _webin_username() -> str:
        return os.environ.get("WEBIN_USERNAME", "")

    def _webin_password() -> str:
        return os.environ.get("WEBIN_PASSWORD", "")

    def _use_test_server() -> bool:
        return os.environ.get("WEBIN_TEST", "true").lower() not in ("false", "0", "no", "off")

    def _ftp_host() -> str:
        return "webin2.ebi.ac.uk" if _use_test_server() else "webin.ebi.ac.uk"

    # ── Component state ───────────────────────────────────────────────────
    seq_dir         = solara.use_reactive("")
    remote_dir      = solara.use_reactive("")
    is_processing   = solara.use_reactive(False)
    upload_progress = solara.use_reactive(None)   # (filename, bytes_done, total_bytes) | None
    status_messages = solara.use_reactive([])
    remote_files    = solara.use_reactive(None)   # dict[name, size] | None
    presence        = solara.use_reactive(None)   # dict[name, bool]  | None

    # threading.Event is not JSON-serialisable, so store it in a ref (not reactive)
    cancel_event = solara.use_ref(threading.Event())

    def add_status(message: str, msg_type: str = "info") -> None:
        ts = time.strftime("%H:%M:%S")
        status_messages.value = status_messages.value + [(ts, msg_type, message)]

    def render_status_log() -> None:
        lines = "".join(
            f"<div style='color:{_msg_color(t)};white-space:pre-wrap;word-break:break-all'>"
            f"[{ts}] {msg}</div>"
            for ts, t, msg in status_messages.value
        )
        solara.HTML(
            tag="div",
            unsafe_innerHTML=lines,
            style=(
                "max-height:300px;overflow-y:auto;font-family:monospace;"
                "font-size:0.82em;line-height:1.4;padding:6px 8px;"
                "background:rgba(0,0,0,0.04);border-radius:4px;"
                "border:1px solid rgba(0,0,0,0.1);"
            ),
        )

    def _check_credentials() -> tuple:
        """Return (rdir, host, uploader) after validating credentials only."""
        if not _webin_username() or not _webin_password():
            raise ValueError(
                "Webin credentials not found. "
                "Set WEBIN_USERNAME and WEBIN_PASSWORD environment variables."
            )
        rdir = remote_dir.value.strip() or None
        return rdir, _ftp_host(), ReadUploader()

    def _check_config() -> tuple:
        """Return (seq_dir_path, local_files, rdir, host, uploader) or raise ValueError."""
        rdir, host, uploader = _check_credentials()
        dir_str = seq_dir.value.strip()
        if not dir_str:
            raise ValueError("Please enter a local sequence file directory.")
        seq_path = Path(dir_str)
        if not seq_path.is_dir():
            raise ValueError(f"Directory not found: {seq_path}")
        local_files = sorted(seq_path.glob("*.gz"))
        if not local_files:
            raise ValueError(f"No .gz files found in: {seq_path}")
        return seq_path, local_files, rdir, host, uploader

    def _start_action():
        """Reset cancel flag and mark processing started."""
        cancel_event.current.clear()
        is_processing.value = True
        status_messages.value = []

    def _finish():
        is_processing.value = False

    # ── Actions ───────────────────────────────────────────────────────────
    def action_cancel() -> None:
        cancel_event.current.set()
        add_status("Cancelling — waiting for current step to finish...", "warning")

    def action_list_remote() -> None:
        _start_action()
        remote_files.value = None

        def _run():
            try:
                rdir, host, uploader = _check_credentials()
                add_status(f"Listing files on {host} ({_webin_username()})...", "info")
                files = uploader.list_remote_files(
                    host=host,
                    username=_webin_username(),
                    password=_webin_password(),
                    remote_dir=rdir,
                    use_tls=True,
                )
                remote_files.value = files
                if files:
                    add_status(f"✓ Found {len(files)} file(s) on FTP:", "success")
                    for name, size in sorted(files.items()):
                        size_str = f"{size / (1024**2):.2f} MB" if size > 0 else "n/a"
                        add_status(f"  {name}  ({size_str})", "info")
                else:
                    add_status("FTP account appears empty.", "warning")
            except Exception as e:
                add_status(f"Error: {e}", "error")
            finally:
                _finish()

        threading.Thread(target=_run, daemon=True).start()

    def action_check_presence() -> None:
        _start_action()
        presence.value = None

        def _run():
            try:
                _, local_files, rdir, host, uploader = _check_config()
                add_status(
                    f"Checking {len(local_files)} local file(s) against FTP...", "info"
                )
                result = uploader.check_files_on_ftp(
                    file_paths=local_files,
                    host=host,
                    username=_webin_username(),
                    password=_webin_password(),
                    remote_dir=rdir,
                    use_tls=True,
                )
                presence.value = result
                missing = [n for n, found in result.items() if not found]
                for name, found in result.items():
                    icon = "✓" if found else "✗"
                    add_status(f"  {icon} {name}", "success" if found else "warning")
                if missing:
                    add_status(
                        f"{len(missing)}/{len(local_files)} file(s) missing from FTP — "
                        "use Upload Missing Files to upload them.",
                        "warning",
                    )
                else:
                    add_status(
                        "✓ All files confirmed on FTP — ready for submission.", "success"
                    )
            except Exception as e:
                add_status(f"Error: {e}", "error")
            finally:
                _finish()

        threading.Thread(target=_run, daemon=True).start()

    def action_upload_missing() -> None:
        _start_action()

        def _run():
            try:
                _, local_files, rdir, host, uploader = _check_config()

                # Always do a fresh presence check before uploading so we never
                # re-upload files that are already on the FTP server.
                add_status(
                    f"Checking {len(local_files)} local file(s) against FTP before uploading...",
                    "info",
                )
                fresh_presence = uploader.check_files_on_ftp(
                    file_paths=local_files,
                    host=host,
                    username=_webin_username(),
                    password=_webin_password(),
                    remote_dir=rdir,
                    use_tls=True,
                )
                presence.value = fresh_presence  # keep the panel state in sync

                if cancel_event.current.is_set():
                    add_status("✗ Cancelled by user.", "warning")
                    return

                to_upload = [f for f in local_files if not fresh_presence.get(f.name, False)]

                if not to_upload:
                    add_status(
                        "✓ All files are already on FTP — nothing to upload.",
                        "success",
                    )
                    return

                already_present = len(local_files) - len(to_upload)
                if already_present:
                    add_status(
                        f"  {already_present} file(s) already on FTP — skipping.",
                        "info",
                    )

                add_status(f"Uploading {len(to_upload)} file(s) to {host}...", "info")
                all_ok = True
                for f in to_upload:
                    # Check for cancellation before starting each file
                    if cancel_event.current.is_set():
                        add_status("✗ Cancelled by user.", "warning")
                        return

                    size_mb = f.stat().st_size / (1024 ** 2)
                    add_status(f"  Computing MD5 for {f.name} ({size_mb:.2f} MB)...", "info")

                    _last_pct = [-1]

                    def _md5_progress(bytes_done: int, total: int, _fname=f.name) -> None:
                        pct = int(bytes_done / total * 100) if total > 0 else 0
                        milestone = (pct // 10) * 10
                        if milestone > _last_pct[0]:
                            _last_pct[0] = milestone
                            done_mb = bytes_done / (1024 ** 2)
                            add_status(
                                f"    MD5 {_fname}: {milestone}% ({done_mb:.1f}/{total / (1024**2):.1f} MB)",
                                "info",
                            )

                    try:
                        md5 = uploader.compute_md5(
                            f,
                            cancel_event=cancel_event.current,
                            progress_callback=_md5_progress,
                        )
                    except InterruptedError:
                        add_status("✗ Cancelled by user during MD5.", "warning")
                        return

                    # Check again after MD5 (can be slow for large files)
                    if cancel_event.current.is_set():
                        add_status("✗ Cancelled by user.", "warning")
                        return

                    add_status(f"  MD5: {md5[:10]}... — uploading...", "info")
                    upload_progress.value = (f.name, 0, f.stat().st_size)

                    def _on_progress(filename: str, bytes_done: int, total: int) -> None:
                        upload_progress.value = (filename, bytes_done, total)

                    result = uploader.upload_via_ftp(
                        file_paths=[f],
                        host=host,
                        username=_webin_username(),
                        password=_webin_password(),
                        remote_dir=rdir,
                        use_tls=True,
                        progress_callback=_on_progress,
                    )
                    upload_progress.value = None
                    status_str = result.get(f.name, "unknown")
                    if status_str == "success":
                        add_status(f"  ✓ {f.name}", "success")
                    else:
                        add_status(f"  ✗ {f.name}: {status_str}", "error")
                        all_ok = False

                if all_ok:
                    add_status("✓ All files uploaded successfully.", "success")
                else:
                    add_status("Some uploads failed — see errors above.", "error")

            except Exception as e:
                add_status(f"Error: {e}", "error")
            finally:
                upload_progress.value = None
                _finish()

        threading.Thread(target=_run, daemon=True).start()

    # ── Layout ────────────────────────────────────────────────────────────
    with solara.Card(title="ENA FTP Upload", elevation=2):
        solara.Markdown(
            "Upload sequence files to the ENA Webin FTP server **before** running "
            "an ENA submission."
        )

        # Credentials status
        with solara.Card("Webin Credentials"):
            if _webin_username():
                solara.Success(f"✓ Logged in as: {_webin_username()}")
            else:
                solara.Warning(
                    "No Webin credentials detected. "
                    "Set WEBIN_USERNAME and WEBIN_PASSWORD as environment variables."
                )
            if _use_test_server():
                solara.Info("FTP host: webin2.ebi.ac.uk (test)")
            else:
                solara.Warning("FTP host: webin.ebi.ac.uk (production)")
            solara.Markdown("_Host is controlled by the `WEBIN_TEST` environment variable._")

        solara.HTML(tag="hr")

        # Configuration inputs
        solara.InputText(
            label="Local sequence file directory (path to folder containing .gz files)",
            value=seq_dir,
            continuous_update=False,
        )
        solara.InputText(
            label="Remote subdirectory on FTP (optional, leave blank for root)",
            value=remote_dir,
            continuous_update=False,
        )

        solara.HTML(tag="hr")

        has_creds = bool(_webin_username()) and bool(_webin_password())
        can_act = has_creds and not is_processing.value
        can_act_dir = can_act and bool(seq_dir.value.strip())

        with solara.Row():
            solara.Button(
                "List Remote Files",
                on_click=action_list_remote,
                disabled=not can_act,
            )
            solara.Button(
                "Check File Presence",
                on_click=action_check_presence,
                disabled=not can_act_dir,
            )
            solara.Button(
                "Upload Missing Files",
                on_click=action_upload_missing,
                color="primary",
                disabled=not can_act_dir,
            )
            if is_processing.value:
                solara.Button(
                    "Cancel",
                    on_click=action_cancel,
                    color="error",
                )

        if is_processing.value:
            prog = upload_progress.value
            if prog is not None:
                fname, done, total = prog
                pct = (done / total * 100) if total > 0 else 0
                done_mb = done / (1024 ** 2)
                total_mb = total / (1024 ** 2)
                solara.Text(f"{fname} — {done_mb:.1f} / {total_mb:.1f} MB ({pct:.0f}%)")
                solara.ProgressLinear(value=pct, color="primary")
            else:
                solara.ProgressLinear(True)

        if status_messages.value:
            with solara.Card("Log"):
                render_status_log()