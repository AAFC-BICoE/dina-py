"""
Submit an ENA Experiment - Simple Example

This is a notebook-style example you can copy and adapt.
Requires: WEBIN_USERNAME, WEBIN_PASSWORD in environment or .env file
"""
from dinapy.ena.models import Experiment
from dinapy.ena.submission import ENASubmissionWorkflow

# =============================================================================
# 1. Create an Experiment Model (linking to existing study and sample)
# =============================================================================
experiment = Experiment(
    alias="my_experiment_001",
    title="Illumina sequencing of soil sample",
    
    # Reference existing study by accession
    study_ref={"accession": "ERP123456"},
    
    # Reference existing sample by accession
    # Or use {"refname": "sample_alias"} if submitting together
    design={
        "designDescription": "Whole genome sequencing of metagenomic sample",
        "sampleDescriptor": {"accession": "SAMEA123456"},
        
        "libraryDescriptor": {
            "libraryName": "Lib_001",
            "libraryStrategy": "WGS",           # WGS, RNA-Seq, Amplicon, etc.
            "librarySource": "METAGENOMIC",     # GENOMIC, METAGENOMIC, etc.
            "librarySelection": "RANDOM",       # RANDOM, PCR, etc.
            "libraryLayout": {"layoutType": "PAIRED"},  # SINGLE or PAIRED
            "libraryConstructionProtocol": "Standard Illumina protocol with NEBNext kit",
        }
    },
    
    # Sequencing platform
    platform={"instrumentModel": "Illumina NovaSeq 6000"}
)

print(f"Experiment: {experiment.alias}")
print(f"Study: {experiment.study_ref}")
print(f"Library: {experiment.design['libraryDescriptor']['libraryStrategy']}")
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
    print("✅ SUCCESS")
    exp_accession = receipt.get_accession("EXPERIMENT")
    print(f"Experiment Accession: {exp_accession}")
else:
    print("❌ FAILURE")
    print(f"Errors: {receipt.get_errors()}")

# Get formatted summary
print("\n" + "="*60)
print(workflow.api.get_receipt_summary(receipt))
