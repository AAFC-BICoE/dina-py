"""
Example: Submit a sample to ENA using XML API

This example demonstrates submitting a sample using the XML-based submission method.
XML submission provides:
- Complete XSD coverage

Compare with submit_sample.py which uses the JSON API.
"""

from dinapy.ena.receipt import format_receipt_summary
from dinapy.ena.submission import ENASubmissionWorkflow
from dinapy.ena.models import Sample, Organism, Attribute

# Initialize workflow
workflow = ENASubmissionWorkflow(test=True)

# Create a sample with MIxS metadata
sample = Sample(
    alias="sample_xml_001_test",
    title="Marine sediment sample from Arctic Ocean",
    description="Sediment sample collected from 500m depth",
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
        Attribute(tag="temperature", value="2.5", unit="°C"),
        Attribute(tag="salinity", value="34.8", unit="PSU"),
        Attribute(tag="sample volume or weight for DNA extraction", value="10", unit="g"),
        Attribute(tag="nucleic acid extraction", value="Qiagen DNeasy PowerSoil Kit"),
        Attribute(tag="project name", value="Arctic Microbiome Project 2024"),
    ]
)

# Submit via XML API
print(f"Submitting sample '{sample.alias}' via XML API...")
receipt = workflow.submit_sample_xml(sample)

# Print receipt
print("\n" + "="*60)
print(format_receipt_summary(receipt))
print("="*60)

if receipt.success:
    print(f"\nSample submitted successfully!")
    for obj in receipt.objects:
        print(f"  Alias: {obj.alias}")
        print(f"  Accession: {obj.accession}")
        print(f"  Status: {obj.status}")
else:
    print(f"\nSubmission failed!")
    for msg in receipt.messages:
        if msg.type == "ERROR":
            print(f"  [ERROR] {msg.text}")