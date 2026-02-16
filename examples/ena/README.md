# ENA Submission Examples

This directory contains **practical code examples** for submitting DINA data to the European Nucleotide Archive (ENA). Examples range from simple single-entity submissions to complete end-to-end workflows.

## Start Here

**New to ENA submissions?** Start with:
1. [`complete_workflow_example.py`](#complete_workflow_examplepy) - Full DINA→ENA workflow with all steps
2. [`test_ena_submission.py`](#test_ena_submissionpy) - Simple test submission to verify setup

## Key Features

**ActionType Enum** - Type-safe submission actions:
```python
from dinapy.ena.models import ActionType
workflow.submit_project(project, action=ActionType.ADD)  # or MODIFY, VALIDATE, etc.
```

**Auto-Resolution**:
- Taxon IDs automatically resolved from scientific names via NCBI API
- Geographic locations derived from coordinates using reverse geocoding (Nominatim)
- Unique aliases generated with timestamps to avoid conflicts

**Unmapped Attributes** - DINA fields without ENA equivalents are automatically preserved as generic attributes

## XML Submissions

ENA also supports JSON payloads for limited resources, so XML will be enforced for now

**XML API** (`submit_experiment`, `submit_run`)
- Complete XSD coverage with all features
- Required for experiments and runs
- Supports all ENA action types (ADD, MODIFY, VALIDATE, etc.)

## What's Included

### Complete Workflows

#### complete_workflow_example.py
**RECOMMENDED STARTING POINT** - Full DINA→ENA submission workflow.

**Prerequisites:** None (uses embedded test data)

**Demonstrates:**
- Fetching data from DINA API (or using embedded test data)
- Deserializing DINA JSON responses into DTOs using schemas
- Mapping DINA entities to ENA models with auto-resolution
- Submitting to ENA in correct dependency order
- Handling accessions and linking entities
- Uploading sequence files to ENA FTP
- Complete error handling and receipt parsing
- Unique alias generation with timestamps

**What it submits:**
1. Project (study)
2. Sample (with auto-resolved taxon, reverse-geocoded location)
3. Experiment (with user-provided sequencing parameters)
4. Run (with file upload to ENA FTP)

**Run it:**
```bash
python complete_workflow_example.py
```

#### test_ena_submission.py
Simple test for verifying ENA credentials and connectivity.

**Prerequisites:** None (creates minimal test submissions)

**Key concepts:**
- Basic workflow validation
- XML API usage
- Receipt parsing
- Error handling

**Run it:**
```bash
python test_ena_submission.py
```

#### release_held_data.py
Demonstrates correct usage of ENA submission action types (ADD, RELEASE, MODIFY, etc.).

**Prerequisites:** None (demonstrates concepts and best practices)

**Key concepts:**
- Understanding ActionType enum (ADD, MODIFY, VALIDATE, HOLD, RELEASE, CANCEL)
- Why RELEASE doesn't work for initial submissions
- Correct workflow for releasing held data
- Common mistakes and how to avoid them

**Important - ENA Release Behavior:** 
- **ADD** (default): Data gets **2-year default hold period** (not public immediately)
- **ADD + hold_until_date**: Custom embargo period (private until specified date)
- **RELEASE**: Makes held data public immediately (before scheduled release date)

**To release data immediately**, you have two options:
1. Set `hold_until_date=date.today().isoformat()` when submitting with ADD
2. Submit with ADD, then use RELEASE action with the accession

**Run it:**
```bash
python release_held_data.py
```

### File Upload Example

#### upload_files_to_ftp.py
Upload sequencing files to ENA FTP before submitting a RUN.

**Prerequisites:** None (just ENA Webin credentials)

**Demonstrates:**
- Uploading files to ENA FTP with automatic MD5 calculation
- Progress bars for large file uploads
- Resume support for interrupted uploads
- Retry logic with exponential backoff
- Manifest file generation (MD5 checksums)
- Directory upload with pattern matching
- Dry run mode (compute checksums without uploading)

**Key concepts:**
- Files must be uploaded to FTP **before** submitting a RUN
- Automatic MD5 checksum calculation and verification
- Manifest files preserve checksums for RUN submission
- Resume support handles network interruptions
- Test vs. production FTP servers

**Run it:**
```bash
python upload_files_to_ftp.py
```

### XML API Examples

#### submit_experiment.py
Submit an experiment linked to an existing study and sample.

**Prerequisites:**
- ⚠️ **Requires project accession** (e.g., PRJEB123456)
- ⚠️ **Requires sample accession** (e.g., SAMEA123456)

**Key concepts:**
- Creating an `Experiment` model
- Linking to existing study/sample by accession
- Specifying library preparation details
- Platform and instrument configuration

**Run it:**
```bash
# First, get accessions from submit_project_xml.py and submit_sample_xml.py
python submit_experiment.py
```

#### submit_run.py
Submit sequencing runs with file uploads.

**Prerequisites:**
- ⚠️ **Requires experiment accession** (e.g., ERX123456)
- ⚠️ **Requires sequence files** (FASTQ/BAM)
- ⚠️ **Files must be uploaded to ENA FTP first**

**Key concepts:**
- Uploading files to ENA FTP with `upload_reads()`
- Creating `Run` models with file checksums
- Working with MD5 manifests
- Two approaches: upload+submit or reference pre-uploaded files

**Run it:**
```bash
# First, get experiment accession from submit_experiment.py
python submit_run.py
```

## 🔧 Setup

All examples require ENA Webin credentials. Create a `.env` file in your working directory:

```env
WEBIN_USERNAME=Webin-12345
WEBIN_PASSWORD=your_password
WEBIN_TEST=true
```

Or set environment variables:
```bash
export WEBIN_USERNAME="Webin-12345"
export WEBIN_PASSWORD="your_password"
export WEBIN_TEST="true"  # Use test server (recommended for development)
```

**Get Webin credentials:**
1. Register at [ENA Webin Portal](https://www.ebi.ac.uk/ena/submit/webin/)
2. Use test submissions until ready for production
3. Test server data is deleted within 24 hours

## � Submission Dependency Chain

ENA submissions must follow this order:

```
1. PROJECT (Study)
   ↓ (returns project accession)
2. SAMPLE
   ↓ (both project and sample accessions needed)
3. EXPERIMENT ──→ references PROJECT + SAMPLE
   ↓ (experiment accession needed)
4. UPLOAD FILES to ENA FTP ──→ get MD5 checksums
   ↓ (files must be on FTP server)
5. RUN ──→ references EXPERIMENT + uploaded files
```

**Important:**
- Projects and samples are **independent** (can submit in any order)
- Experiments **require** both project AND sample accessions
- **Files must be uploaded to FTP BEFORE submitting RUN** (see `upload_files_to_ftp.py`)
- Runs **require** experiment accession and uploaded sequence files with MD5 checksums
- Use test server (`test=True`) until ready for production

## Typical Workflow

1. **Submit Project** (Study)
   ```python
   # See submit_project.py for full example
   project = Project(alias="study_001", title="My Study", ...)
   receipt = workflow.submit_project(project)
   # → Returns project accession (e.g., PRJEB123456)
   ```

2. **Submit Sample** (with auto-resolution and mapping from DINA)
   ```python
   from dinapy.ena.mappers.dina_to_ena.mappers_dto import material_sample_to_ena
   
   # Map DINA MaterialSample + CollectingEvent to ENA Sample
   # Auto-resolves taxon ID from scientific name
   # Auto-derives geographic location from coordinates if needed
   ena_sample = material_sample_to_ena(
       material_sample=material_sample_dto,  # From DINA API
       collecting_event=collecting_event_dto,  # From DINA API
       email="researcher@example.com",  # For NCBI taxon lookup
       include_unmapped=True  # Preserves DINA fields as generic attributes
   )
   
   # Add unique timestamp to alias to avoid conflicts
   timestamp = str(int(time.time()))
   ena_sample.alias = f"{ena_sample.alias}_{timestamp}"
   
   receipt = workflow.submit_sample(ena_sample)
   sample_accession = receipt.get_accession('SAMPLE')  # e.g., SAMEA123456
   ```
   
   **Auto-resolution features:**
   - Taxon ID: Automatically queries NCBI Taxonomy API using scientific name from DINA
   - Geographic location: Uses dwcCountry, or reverse-geocodes from coordinates, or falls back to "not provided"
   - Collection date: Extracted from collecting event (endEventDateTime > startEventDateTime)
   - Unmapped attributes: All DINA-specific fields preserved as generic ENA attributes

3. **Submit Experiment**
   ```python
   # See submit_experiment.py for full example
   experiment = Experiment(
       alias="exp_001",
       study_ref={"accession": "PRJEB123456"},
       design={"sampleDescriptor": {"accession": "SAMEA123456"}, ...}
   )
   receipt = workflow.submit_experiment(experiment)
   # → Returns experiment accession (e.g., ERX123456)
   ```

4. **Upload Files to ENA FTP** (before submitting RUN)
   ```python
   # See upload_files_to_ftp.py for detailed example
   from dinapy.ena.upload import ReadUploader
   
   uploader = ReadUploader()
   result = uploader.prepare_and_upload_reads(
       file_paths=[Path("reads_R1.fastq.gz"), Path("reads_R2.fastq.gz")],
       host="webin2.ebi.ac.uk",  # Test server
       username=username,
       password=password,
       save_manifest=True,
       manifest_path=Path("manifest.txt")
   )
   # → Returns manifest with MD5 checksums for each file
   ```

5. **Submit Run** (requires experiment accession and uploaded files)
   ```python
   # See submit_run.py for full example
   # Use MD5 checksums from upload manifest
   run = Run(
       experiment_ref={"accession": "ERX123456"},
       files=[
           File(filename="reads_R1.fastq.gz", filetype="fastq", 
                checksumMethod="MD5", checksum=file_info['md5'])
       ]
   )
   receipt = workflow.submit_run(run)
   # → Returns run accession (e.g., ERR123456)
   ```

## 🏭 Production vs Test

By default, `ENASubmissionWorkflow(test=True)` uses the **test server** (`wwwdev.ebi.ac.uk`), which is reset nightly.

For **production** submissions:
```python
workflow = ENASubmissionWorkflow(test=False)  # or test=False
```

⚠️ **Warning**: Production submissions have **2-year default hold period**. Data is NOT public immediately!

**Release Data Immediately** (make public now):
```python
# Option 1: Set hold date to today
from datetime import date
workflow.submit_project_xml(
    project, 
    action="ADD",
    hold_until_date=date.today().isoformat()  # Public immediately
)

# Option 2: Submit then RELEASE
workflow.submit_project_xml(project, action="ADD")  # Gets 2-year hold
# Then immediately release:
release_xml = build_submission_xml_from_model(
    submission_alias="release_now",
    action=[{"type": "RELEASE", "target": "PRJEB123456"}]  # Your accession
)
workflow.api.submit_webin_xml(release_xml, path="/submit")
```

**Custom Embargo Period**:
```python
# Hold until specific future date
workflow.submit_project_xml(
    project, 
    action="ADD",
    hold_until_date="2026-12-31"  # Private until this date
)
```

## Error Handling

Scripts return exit code 0 on success, 1 on failure. Check stderr for error messages:

```bash
python submit_experiment.py ... || echo "Submission failed!"
```

## Learn More

- [ENA Webin Portal](https://www.ebi.ac.uk/ena/submit/webin/)
- [ENA Metadata Model](https://ena-docs.readthedocs.io/en/latest/submit/general-guide/metadata.html)
- [dinapy Documentation](../../README.md)
