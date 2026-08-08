# ENA Submission Workflow — Logic Reference

This document describes the end-to-end logical flow of `workflow_gui.py`, the
interactive DINA → ENA submission workflow.

---

## Overview

The workflow is **sequence-file-oriented**: it starts from a directory of local
`.fastq.gz` files that have already been uploaded to ENA's FTP server, resolves
the associated DINA material samples, and submits the full ENA metadata chain:

```
Study → Sample(s) → Experiment → Run
```

Each `.fastq.gz` (default extension, but can be any other specified) file (or R1/R2 pair)
 produces one **entry** that maps to one
experiment and one run. An entry may link to one or more DINA material samples,
which become one ENA sample or a SAMPLE_SET/POOL respectively.

---

## Unique Identifiers (Aliases)

ENA uses **aliases** to deduplicate objects within a submission account. The
following stable, deterministic aliases are used:

| Object | Alias format | Example |
|--------|-------------|---------|
| Study (new) | `{study_name}_{unix_timestamp}` | `MyStudy_1745000000` |
| Sample | DINA material sample UUID | `019a30f9-500e-76e4-8706-1ae9e7994726` |
| Experiment | `exp_{stem}` | `exp_NS.1300.002.UDP0090_i7---UDP0090_i5.GAR19-S039F` |
| Run | `run_{stem}` | `run_NS.1300.002.UDP0090_i7---UDP0090_i5.GAR19-S039F` |

Where `stem` is the filename base of the sequence file without extension.

- **Study** aliases include a timestamp so each new-study submission is unique.
  Re-using an existing study bypasses submission entirely.
- **Sample** aliases are DINA UUIDs — stable across re-runs. ENA detects
  already-registered samples by this alias.
- **Experiment** and **Run** aliases are derived from the sequence filename —
  stable and deterministic, so ENA can detect duplicates on retry.

---

## Step-by-Step Flow

### Step 1 — Configuration

The user provides:
- Webin credentials (`WEBIN_USERNAME`, `WEBIN_PASSWORD`, `WEBIN_TEST` from `.env`)
- Study mode: **new** (title/description entered) or **existing** (PRJEB accession)
- Hold date, default NCBI taxon ID, library parameters

### Step 2 — Files & Library

The user provides:
- Path to the local sequence file directory
- File glob pattern (default `*.fastq.gz`)
- R1/R2 suffixes for PAIRED layout
- Library strategy, source, selection, instrument model

### Step 3 — Verify & Lookup (two phases, run in background thread)

**Phase 1: FTP scan & file grouping**

1. Scan the directory for files matching the pattern.
2. For PAIRED layout, group R1+R2 files by shared stem.
3. Connect to ENA FTP and verify each file is present.
4. Entries with missing FTP files are flagged (warning) and later excluded.

**Phase 2: MD5 + DINA sample lookup** (after user selects entries to process)

1. Compute MD5 checksums for all FTP-confirmed files.
   - Results are cached in a temp file keyed by `{path}:{size}:{mtime}` to avoid
     re-hashing unchanged files on subsequent runs.
2. For each entry, look up the associated DINA material sample:
   - Query the object-store search index by filename to get the **attachment UUID**.
   - Query the material sample search index by that attachment UUID.
   - Deduplicate by sample UUID across files in the same entry.
3. Entries with no DINA sample found are excluded with a warning.
4. All remaining entries advance to Step 4.

### Step 4 — Review

Displays a table of all entries with:
- Sequence file name(s) and MD5(s)
- FTP presence status
- Resolved DINA sample UUID(s)
- Any previously stored ENA accessions (from a prior session)

### Step 5 — Submit (background thread)

All submission happens in a single background thread. Per-entry results are
flushed to state periodically so progress is not lost if the workflow crashes
mid-run.

#### [1/4] Study

| Condition | Action |
|-----------|--------|
| `study_mode == "existing"` | Use the user-supplied `PRJEB...` accession — no API call |
| `study_mode == "new"` | Submit `Project` with `action=ADD`. On success, store the returned `PRJEB...` accession. On failure, raise (abort entire workflow). |

No "already exists" recovery for studies — a new alias is generated each time
via the timestamp suffix.

#### Pre-fetch (before the per-entry loop)

All DINA material sample records referenced by any entry are fetched in parallel
(via `ThreadPoolExecutor`) and cached in memory. This avoids N serial API calls
inside the hot submission loop.

#### Per-entry loop: [2/4] Samples

**Skip gate:** If `entry["ena_run_accession"]` is already set (from a previous
session's state), the entire entry is skipped — samples, experiment, and run are
all bypassed. **Zero API calls are made.**

> This is the only path where no API calls are made. If `ena_run_accession` is
> not pre-set, all three submissions are attempted regardless of whether the
> objects already exist in ENA — ENA's "already exists" responses are handled
> at each layer as described below.

For each entry that is not skipped:

1. Map each DINA material sample to an ENA `Sample` object using the DINA UUID
   as the alias.
2. Submit with `action=ADD` and the configured hold date.
3. **Already exists recovery:** ENA returns `"already exists"` in the error
   message, but provides only an `ERA...` (submission-level) accession — not
   the real `ERS.../SAMEA...` accession. In this case the alias (DINA UUID) is
   stored as a `refname` for use in the experiment design, and the entry
   continues.
4. On any other failure, the entry raises an exception (logged, workflow
   continues to next entry via outer `try/except`).

Single sample → `submit_sample_xml`.  
Multiple samples → `submit_samples_xml` (SAMPLE_SET).

#### Per-entry loop: [3/4] Experiment

1. Build a `Design` referencing the sample(s):
   - **Single sample:** `ObjectRef(accession=SAMEA...)` if a real accession was
     returned, otherwise `ObjectRef(refname=dina_uuid)`.
   - **Multiple samples (pool):** `PoolMember` list, each using accession or
     refname the same way.
2. Submit `Experiment` with `action=ADD`, alias `exp_{stem}`.
3. **Already exists recovery:** Same ERA-only problem as samples. If `"already
   exists"` is in the errors, store `ena_experiment_accession = None` and keep
   the alias so the run step can reference by `refname`.
4. On any other failure, raise.

#### Per-entry loop: [4/4] Run

1. Build `Run` referencing the experiment:
   - `ObjectRef(accession=ERX...)` if a real ERX accession was stored.
   - `ObjectRef(refname=exp_{stem})` if the experiment already existed and only
     an ERA was returned.
2. Attach files with filenames and MD5 checksums (`filetype=fastq`).
3. Submit `Run` with `action=ADD`, alias `run_{stem}`.
4. **Already exists recovery — two patterns:**
   - **Pattern A:** ENA message contains `"submitted in ERR[0-9]+"` → extract
     the ERR accession and store it. Entry marked as success.
   - **Pattern B:** ENA message contains `"already exists in the submission
     account"` (returns ERA, not ERR) → no ERR accession recoverable. Entry
     marked as already-registered; a note is logged but no failure is raised.
5. On any other failure, log the error and a warning; the entry does not have
   a run accession.

### Step 6 — Results

Displays:
- Study accession
- Per-entry table: `stem | Sample(s) | Exp | Run`
  - Sample column shows `—` when only a DINA UUID alias is available (no real
    SAMEA accession was returned by ENA)
- Summary counts: submitted / already in ENA / not submitted
- Downloadable CSV with all accessions

---

## "Already Exists" Behaviour Summary

ENA's XML submission API always returns an `ERA...` (submission-level)
accession when a duplicate is detected — never the real `ERS/SAMEA`, `ERX`, or
`ERR` accession. The workflow handles this at every layer:

| Layer | ENA returns on duplicate | Recovery |
|-------|--------------------------|----------|
| Sample | `ERA...` | Store DINA UUID alias as `refname` |
| Experiment | `ERA...` | Store alias `exp_{stem}` as `refname` |
| Run (pattern A) | `ERR...` in message | Extract and store ERR accession |
| Run (pattern B) | `ERA...` in message | Mark as registered; ERR unknown |

---

## MD5 Cache

MD5 checksums are cached in the system temp directory in a file named
`dina_md5_cache_{dir_hash}.json`, keyed by `{absolute_path}:{size}:{mtime}`.
The cache is invalidated automatically if the file changes. This means large
batches can be resumed without re-hashing all files.

---

## Session Persistence

`sequence_entries` is a Solara reactive variable that persists across Step
re-runs within the same kernel session. If `ena_run_accession` is already set
on an entry (from a prior successful submission in the same session), the
submission loop skips that entry entirely. This allows partial batch recovery
without re-submitting already-complete entries.
