"""
Example: Submit multiple samples to ENA in a batch using XML API

This example demonstrates TRUE batch submission of multiple samples using the
submit_samples_xml() method. This submits all samples in a single SAMPLE_SET XML,
which is more efficient than submitting samples individually.

Key benefits of batch submission:
- All samples are submitted in one SAMPLE_SET with a single API call
- Single transaction reduces overhead
- More efficient for studies with many samples
- Better performance and reliability

Compare with submit_sample_xml.py which submits a single sample.
"""

from datetime import datetime
from dinapy.ena.receipt import format_receipt_summary
from dinapy.ena.submission import ENASubmissionWorkflow
from dinapy.ena.models import Sample, Organism, Attribute, ActionType

# Initialize workflow
workflow = ENASubmissionWorkflow(test=True)

# Generate unique timestamp for aliases
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Create multiple samples from the same study
# Note: Using simple units to avoid special character issues
samples = [
    Sample(
        alias=f"sample_batch_001_{timestamp}",
        title="Marine sediment sample from Arctic Ocean - Station A",
        description="Sediment sample collected from 500m depth at Station A",
        organism=Organism(
            taxon_id=410658,
            scientific_name="marine metagenome"
        ),
        attributes=[
            # MIxS mandatory fields
            Attribute(tag="investigation type", value="metagenome"),
            Attribute(tag="sequencing method", value="Illumina NovaSeq 6000"),
            Attribute(tag="collection date", value="2024-08-15"),
            Attribute(tag="geographic location (country and/or sea)", value="Arctic Ocean"),
            Attribute(tag="geographic location (latitude)", value="78.5", unit="DD"),
            Attribute(tag="geographic location (longitude)", value="15.2", unit="DD"),
            Attribute(tag="environment (biome)", value="marine biome [ENVO:00000447]"),
            Attribute(tag="environment (feature)", value="ocean floor [ENVO:00002150]"),
            Attribute(tag="environment (material)", value="sediment [ENVO:00002007]"),
            
            # Additional metadata
            Attribute(tag="depth", value="500", unit="m"),
            Attribute(tag="temperature", value="2.5", unit="degrees Celsius"),
            Attribute(tag="salinity", value="34.8", unit="PSU"),
            Attribute(tag="sample volume or weight for DNA extraction", value="10", unit="g"),
            Attribute(tag="project name", value="Arctic Microbiome Project 2024"),
        ]
    ),
    Sample(
        alias=f"sample_batch_002_{timestamp}",
        title="Marine sediment sample from Arctic Ocean - Station B",
        description="Sediment sample collected from 750m depth at Station B",
        organism=Organism(
            taxon_id=410658,
            scientific_name="marine metagenome"
        ),
        attributes=[
            # MIxS mandatory fields
            Attribute(tag="investigation type", value="metagenome"),
            Attribute(tag="sequencing method", value="Illumina NovaSeq 6000"),
            Attribute(tag="collection date", value="2024-08-16"),
            Attribute(tag="geographic location (country and/or sea)", value="Arctic Ocean"),
            Attribute(tag="geographic location (latitude)", value="78.8", unit="DD"),
            Attribute(tag="geographic location (longitude)", value="15.5", unit="DD"),
            Attribute(tag="environment (biome)", value="marine biome [ENVO:00000447]"),
            Attribute(tag="environment (feature)", value="ocean floor [ENVO:00002150]"),
            Attribute(tag="environment (material)", value="sediment [ENVO:00002007]"),
            
            # Additional metadata
            Attribute(tag="depth", value="750", unit="m"),
            Attribute(tag="temperature", value="2.1", unit="degrees Celsius"),
            Attribute(tag="salinity", value="34.9", unit="PSU"),
            Attribute(tag="sample volume or weight for DNA extraction", value="10", unit="g"),
            Attribute(tag="project name", value="Arctic Microbiome Project 2024"),
        ]
    ),
]

# Submit all samples in a SINGLE batch via XML API
print(f"Submitting {len(samples)} samples in a BATCH via XML API...")
print("Samples:")
for sample in samples:
    print(f"  - {sample.alias}: {sample.title}")

# TRUE BATCH SUBMISSION: All samples in one SAMPLE_SET
# Use unique submission_alias to avoid conflicts
receipt = workflow.submit_samples_xml(
    samples=samples,
    submission_alias=f"sub_batch_{timestamp}",
    action=ActionType.ADD
)

# Print receipt
print("\n" + "="*60)
print(format_receipt_summary(receipt))
print("="*60)

if receipt.success:
    print(f"\n✓ Batch submission successful! All {len(samples)} samples submitted in ONE request.")
    print("\nSample Accessions:")
    for sample in samples:
        # Find the accession from the receipt objects
        for obj in receipt.objects:
            if obj.object_type == 'SAMPLE' and obj.alias == sample.alias:
                print(f"  {sample.alias}: {obj.accession}")
                break
else:
    print(f"\n✗ Batch submission failed!")
    for msg in receipt.messages:
        if msg.type == "ERROR":
            print(f"  [ERROR] {msg.text}")

# ============================================================================
# ADDITIONAL EXAMPLES
# ============================================================================

print("\n" + "="*60)
print("ADDITIONAL USE CASES")
print("="*60)

# Example 1: Submit with hold date
print("\n1. Submitting with hold date (data will be held until specified date):")
print("   Code:")
print("   receipt = workflow.submit_samples_xml(")
print("       samples=samples,")
print("       submission_alias=f'sub_hold_{timestamp}',")
print("       action=ActionType.ADD,")
print("       hold_until_date='2025-12-31'")
print("   )")

# Example 2: Modify existing samples
print("\n2. Modifying existing samples (requires accessions):")
print("   Code:")
print("   # First, update your Sample objects with accessions")
print("   samples[0].accession = 'ERS123456'")
print("   samples[1].accession = 'ERS123457'")
print("   ")
print("   # Then submit with MODIFY action")
print("   receipt = workflow.submit_samples_xml(")
print("       samples=samples,")
print("       submission_alias=f'sub_modify_{timestamp}',")
print("       action=ActionType.MODIFY")
print("   )")

# Example 3: Validate without submitting
print("\n3. Validating samples without submission:")
print("   Code:")
print("   receipt = workflow.submit_samples_xml(")
print("       samples=samples,")
print("       submission_alias=f'sub_validate_{timestamp}',")
print("       action=ActionType.VALIDATE")
print("   )")

# Example 4: Release held samples
print("\n4. Releasing held samples (requires accessions):")
print("   Code:")
print("   receipt = workflow.submit_samples_xml(")
print("       samples=samples,")
print("       submission_alias=f'sub_release_{timestamp}',")
print("       action=ActionType.RELEASE")
print("   )")

print("\n" + "="*60)
print("TIPS:")
print("- Use unique submission_alias to avoid conflicts")
print("- Use 'degrees Celsius' instead of '°C' for temperature units")
print("- Ensure all MIxS mandatory fields are included")
print("- For single sample submission, see: submit_sample_xml.py")
print("="*60)
