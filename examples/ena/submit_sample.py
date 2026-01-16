"""
Submit an ENA Sample via Webin API

This is a simple example showing how to submit a sample to ENA with MIxS-compliant metadata.
Copy this code into a Jupyter notebook or run it as a standalone script.

Environment variables required:
    WEBIN_USERNAME: ENA Webin account username
    WEBIN_PASSWORD: ENA Webin account password
    WEBIN_TEST: Set to 'true' for test server (default: true)
"""

from dinapy.ena.models import Sample, SampleName, Attribute
from dinapy.ena.submission import ENASubmissionWorkflow


# ============================================================================
# 1. Create Sample Model
# ============================================================================

sample = Sample(
    alias="sample_arctic_soil_001",
    title="Arctic permafrost soil sample from Resolute Bay",
    sample_name=SampleName(
        taxonId=410658,  # soil metagenome
        scientificName="soil metagenome"
    ),
    description="Soil sample collected from active layer above permafrost at 10cm depth",
    sampleAttributes=[
        # Required MIxS attributes for environmental samples
        Attribute(tag="geographic location (country and/or sea)", value="Canada"),
        Attribute(tag="geographic location (latitude)", value="74.6895 N"),
        Attribute(tag="geographic location (longitude)", value="94.8331 W"),
        Attribute(tag="collection date", value="2024-07-15"),
        Attribute(tag="environment (biome)", value="terrestrial biome [ENVO:00000446]"),
        Attribute(tag="environment (feature)", value="permafrost [ENVO:00000134]"),
        Attribute(tag="environment (material)", value="soil [ENVO:00001998]"),
        
        # Additional environmental metadata
        Attribute(tag="depth", value="0.1 m"),
        Attribute(tag="soil type", value="Cryosol"),
        Attribute(tag="temperature", value="-2 degrees Celsius"),
        Attribute(tag="pH", value="6.8"),
        Attribute(tag="collection method", value="soil corer"),
        
        # Project context
        Attribute(tag="project name", value="Arctic Microbial Diversity Study"),
        Attribute(tag="investigation type", value="metagenome"),
        Attribute(tag="sequencing method", value="Illumina NovaSeq 6000"),
    ]
)

print("Sample to submit:")
print(f"  Alias: {sample.alias}")
print(f"  Title: {sample.title}")
print(f"  Taxon: {sample.sample_name.scientificName} (taxid:{sample.sample_name.taxonId})")
print(f"  Attributes: {len(sample.sampleAttributes)} metadata fields")
print()


# ============================================================================
# 2. Initialize Workflow
# ============================================================================

# Use test=True for test server (data reset nightly)
# Use test=False for production (permanent submissions)
workflow = ENASubmissionWorkflow(test=True)

print("Submitting to ENA TEST server...")
print()


# ============================================================================
# 3. Submit Sample
# ============================================================================

receipt = workflow.submit_sample(
    sample=sample
)


# ============================================================================
# 4. Parse Receipt
# ============================================================================

print("=" * 60)
print("SUBMISSION RECEIPT")
print("=" * 60)
print()

if receipt.success:
    print("SUCCESS")
    sample_accession = receipt.get_accession("SAMPLE")
    if sample_accession:
        print(f"\nSample Accession: {sample_accession}")
        print(f"View at: https://wwwdev.ebi.ac.uk/ena/browser/view/{sample_accession}")
    else:
        print("\nNote: Accession not found in receipt (may be assigned later)")
else:
    print("FAILURE")
    errors = receipt.get_errors()
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")

# Show all messages
if receipt.messages:
    print("\nMessages:")
    for msg in receipt.messages:
        print(f" [{msg.type}] {msg.text}")

print()


# ============================================================================
# TIPS
# ============================================================================
print("\n💡 Tips:")
print("  - Use appropriate taxon ID from NCBI Taxonomy")
print("  - For metagenomes, use taxon IDs like:")
print("    • 410658 (soil metagenome)")
print("    • 412755 (marine metagenome)")
print("    • 749906 (gut metagenome)")
print("  - Check MIxS standards: https://genomicsstandardsconsortium.github.io/mixs/")
print("  - Use controlled vocabularies (e.g., ENVO ontology for environmental terms)")
