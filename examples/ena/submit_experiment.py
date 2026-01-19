"""
Submit an ENA Experiment - Simple Example

This is a notebook-style example you can copy and adapt.
Requires: WEBIN_USERNAME, WEBIN_PASSWORD in environment or .env file
"""
from dinapy.ena.models import (
    Experiment, Design, Platform, LibraryDescriptor, LibraryLayout, ObjectRef
)
from dinapy.ena.submission import ENASubmissionWorkflow

# =============================================================================
# 1. Create an Experiment Model (linking to existing study and sample)
# =============================================================================
experiment = Experiment(
    alias="my_experiment_001",
    title="Illumina sequencing of soil sample",
    
    # Reference existing study by accession
    study_ref=ObjectRef(accession="ERP123456"),
    
    # Design with library and sample descriptors
    design=Design(
        design_description="Whole genome sequencing of metagenomic sample",
        sample_descriptor=ObjectRef(accession="SAMEA123456"),
        library_descriptor=LibraryDescriptor(
            library_name="Lib_001",
            library_strategy="WGS",           # WGS, RNA-Seq, Amplicon, etc.
            library_source="METAGENOMIC",     # GENOMIC, METAGENOMIC, etc.
            library_selection="RANDOM",       # RANDOM, PCR, etc.
            library_layout=LibraryLayout(layout_type="PAIRED"),  # SINGLE or PAIRED
            library_construction_protocol="Standard Illumina protocol with NEBNext kit",
        )
    ),
    
    # Sequencing platform
    platform=Platform(instrument_model="Illumina NovaSeq 6000")
)

print(f"Experiment: {experiment.alias}")
print(f"Study: {experiment.study_ref.accession if experiment.study_ref.accession else experiment.study_ref.refname}")
print(f"Library: {experiment.design.library_descriptor.library_strategy}")
print()

# =============================================================================
# 2. Initialize Workflow
# =============================================================================
workflow = ENASubmissionWorkflow(test=True)

# =============================================================================
# 3. Submit Experiment
# =============================================================================
receipt = workflow.submit_experiment(experiment=experiment)

# =============================================================================
# 4. Check Results
# =============================================================================
if receipt.success:
    print("SUCCESS")
    exp_accession = receipt.get_accession("EXPERIMENT")
    print(f"Experiment Accession: {exp_accession}")
else:
    print("FAILURE")
    print(f"Errors: {receipt.get_errors()}")

# Get formatted summary
from dinapy.ena.receipt import format_receipt_summary
print("\n" + "="*60)
print(format_receipt_summary(receipt))
