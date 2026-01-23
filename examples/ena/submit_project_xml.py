"""
Example: Submit a project to ENA using XML API

This example demonstrates submitting a project using the XML-based submission method.
XML submission provides complete XSD coverage for advanced project features like:
- Umbrella projects (UMBRELLA_PROJECT)
- Related projects (RELATED_PROJECTS with parent/child/peer relationships)
- Project collaborators (COLLABORATORS)

Compare with submit_project.py which uses the JSON API.
"""

from dinapy.ena.receipt import format_receipt_summary
from dinapy.ena.submission import ENASubmissionWorkflow
from dinapy.ena.models import Project, Attribute

# Initialize workflow
workflow = ENASubmissionWorkflow(test=True)  # Use test server

# Create a project (study)
project = Project(
    alias="project_xml_001_test",
    title="Arctic Ocean Microbiome Study 2024",
    description="Comprehensive metagenomic analysis of Arctic Ocean sediment microbiomes",
    attributes=[
        Attribute(tag="study_type", value="Metagenomics"),
        Attribute(tag="study_abstract", value="This study investigates microbial diversity in Arctic Ocean sediments using shotgun metagenomics."),
    ]
)

# Submit via XML API
print(f"Submitting project '{project.alias}' via XML API...")
receipt = workflow.submit_project_xml(project)

# Print receipt
print("\n" + "="*60)
print(format_receipt_summary(receipt))
print("="*60)

if receipt.success:
    print(f"\nProject submitted successfully!")
    for obj in receipt.objects:
        print(f"  Alias: {obj.alias}")
        print(f"  Accession: {obj.accession}")
        print(f"  Status: {obj.status}")
else:
    print(f"\nSubmission failed!")
    for msg in receipt.messages:
        if msg.type == "ERROR":
            print(f"  [ERROR] {msg.text}")