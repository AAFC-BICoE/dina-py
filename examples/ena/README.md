# ENA Submission Examples

This directory contains **notebook-style code examples** for submitting data to the European Nucleotide Archive (ENA). These are simple, self-contained scripts that you can copy into Jupyter notebooks or run directly with Python.

## 📋 What's Included

### submit_project.py
Simple example showing how to submit a project (study) to ENA.

**Key concepts:**
- Creating a `Project` model
- Using `ENASubmissionWorkflow`
- Parsing submission receipts

**Run it:**
```bash
python submit_project.py
```

### submit_sample.py
Example showing how to submit a sample with MIxS-compliant metadata.

**Key concepts:**
- Creating a `Sample` model with `SampleName` and attributes
- Using controlled vocabularies (ENVO ontology)
- MIxS metadata standards for environmental samples
- Choosing appropriate taxon IDs for metagenomes

**Run it:**
```bash
python submit_sample.py
```

### submit_experiment.py
Example showing how to submit an experiment linked to an existing study and sample.

**Key concepts:**
- Creating an `Experiment` model
- Linking to existing study/sample by accession
- Specifying library preparation details

**Run it:**
```bash
python submit_experiment.py
```

### submit_run.py
Example showing two approaches for submitting sequencing runs:
1. Upload files and submit run together
2. Submit run referencing pre-uploaded files

**Key concepts:**
- Uploading files to ENA FTP with `upload_reads()`
- Creating `Run` models with file checksums
- Working with MD5 manifests

**Run it:**
```bash
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

## 🔄 Typical Workflow

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

4. **Upload Reads & Submit Run**
   ```python
   # See submit_run.py for full example with upload
   upload_result = workflow.upload_reads(file_paths=[...])
   run = Run(experiment_ref={"accession": "ERX123456"}, ...)
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
