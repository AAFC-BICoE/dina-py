# ENA Submission Examples

This directory contains **notebook-style code examples** for submitting data to the European Nucleotide Archive (ENA). These are simple, self-contained scripts that you can copy into Jupyter notebooks or run directly with Python.

## 🆕 JSON vs XML Submission Methods

ENA supports two submission methods:

**JSON API** (`submit_project`, `submit_sample`)
- Simpler payload format
- Has known bugs (e.g., description field validation)
- Incomplete XSD coverage (no umbrella_project, related_projects)

**XML API** (`submit_experiment`, `submit_run`)
- Complete XSD coverage
- No known bugs
- Well-documented via XSD schemas

## 📋 What's Included

### Complete Workflow Test

#### test_ena_submission.py
End-to-end test that submits both a project and sample to the live ENA test server.

**Prerequisites:** None (creates new test submissions)

**Key concepts:**
- Complete workflow demonstration
- XML API usage
- Receipt parsing and validation
- Automatic unique alias generation

**Run it:**
```bash
python test_ena_submission.py
```

### JSON API Examples (Legacy/Simple Use Cases)

#### submit_project.py
Simple example showing how to submit a project via JSON API.

**Prerequisites:** None (creates new project)

**Key concepts:**
- Creating a `Project` model
- Using `ENASubmissionWorkflow`
- Parsing submission receipts
- JSON API limitations

**Run it:**
```bash
python submit_project.py
```

#### submit_sample.py
Example showing how to submit a sample via JSON API

**Prerequisites:** None (creates new sample)

**Key concepts:**
- Creating a `Sample` model with `Organism` and attributes
- Using controlled vocabularies (ENVO ontology)
- MIxS metadata standards for environmental samples
- JSON API limitations (description field removed automatically)

**Run it:**
```bash
python submit_sample.py
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

All examples require ENA Webin credentials. Set them as environment variables:

```bash
export WEBIN_USERNAME="Webin-12345"
export WEBIN_PASSWORD="your_password"
export WEBIN_TEST="true"  # Use test server (default)
```

Or create a `.env` file in your working directory:

```
WEBIN_USERNAME=Webin-12345
WEBIN_PASSWORD=your_password
WEBIN_TEST=true
```

## � Submission Dependency Chain

ENA submissions must follow this order:

```
1. PROJECT (Study)
   ↓ (returns project accession)
2. SAMPLE
   ↓ (both project and sample accessions needed)
3. EXPERIMENT ──→ references PROJECT + SAMPLE
   ↓ (experiment accession needed)
4. RUN ──→ references EXPERIMENT + uploaded files
```

**Important:**
- Projects and samples are **independent** (can submit in any order)
- Experiments **require** both project AND sample accessions
- Runs **require** experiment accession and uploaded sequence files
- Use test server (`test=True`) until ready for production

## �🔄 Typical Workflow

1. **Submit Project** (Study)
   ```python
   # See submit_project.py for full example
   project = Project(alias="study_001", title="My Study", ...)
   receipt = workflow.submit_project(project)
   # → Returns project accession (e.g., PRJEB123456)
   ```

2. **Submit Sample**
   ```python
   # Similar pattern to project submission
   from dinapy.ena.models import Sample, SampleName, Attribute
   
   sample = Sample(
       alias="sample_001",
       title="Soil sample from site A",
       sample_name=SampleName(taxonId=410658, scientificName="soil metagenome"),
       sampleAttributes=[
           Attribute(tag="geographic location (country)", value="USA"),
           Attribute(tag="collection date", value="2023-01-15"),
           # ... more MIxS attributes
       ]
   )
   receipt = workflow.submit_sample(sample)
   # → Returns sample accession (e.g., SAMEA123456)
   ```

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

4. **Upload Reads & Submit Run** (requires experiment accession from step 3)
   ```python
   # See submit_run.py for full example with upload
   upload_result = workflow.upload_reads(file_paths=[...])
   run = Run(experiment_ref={"accession": "ERX123456"}, ...)  # Use accession from step 3
   receipt = workflow.submit_run(run)
   # → Returns run accession (e.g., ERR123456)
   ```

## 🏭 Production vs Test

By default, `ENASubmissionWorkflow(test=True)` uses the **test server** (`wwwdev.ebi.ac.uk`), which is reset nightly.

For **production** submissions:
```python
workflow = ENASubmissionWorkflow(test=False)  # or test=False
```

⚠️ **Warning**: Production submissions are permanent and will be made public after the embargo period!

⚠️ **Warning**: Production submissions are permanent and will be made public after the embargo period!

## Error Handling

Scripts return exit code 0 on success, 1 on failure. Check stderr for error messages:

```bash
python submit_experiment.py ... || echo "Submission failed!"
```

## Learn More

- [ENA Webin Portal](https://www.ebi.ac.uk/ena/submit/webin/)
- [ENA Metadata Model](https://ena-docs.readthedocs.io/en/latest/submit/general-guide/metadata.html)
- [dinapy Documentation](../../README.md)
