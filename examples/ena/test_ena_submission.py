#!/usr/bin/env python3
"""
End-to-End ENA Submission Test

This script tests the complete workflow by submitting a project and sample
to the ENA test server using the provided credentials.

Usage:
    python test_ena_submission.py

Environment variables required:
    WEBIN_USERNAME: ENA Webin account username
    WEBIN_PASSWORD: ENA Webin account password
"""

from dinapy.ena.models import Project, Sample, Organism, Attribute
from dinapy.ena.submission import ENASubmissionWorkflow
from dinapy.ena.receipt import format_receipt_summary
import random
import string

def generate_unique_alias(prefix):
    """Generate a unique alias with random suffix."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{random_suffix}"

def main():
    print("="*70)
    print("ENA SUBMISSION END-TO-END TEST")
    print("="*70)
    print()
    
    # Initialize workflow
    workflow = ENASubmissionWorkflow(test=True)
    print(f"Workflow initialized (test mode)")
    print(f"  Server: https://wwwdev.ebi.ac.uk/ena/submit/webin-v2")
    print()
    
    # =========================================================================
    # TEST 1: Submit a Project
    # =========================================================================
    print("-" * 70)
    print("TEST 1: Project Submission")
    print("-" * 70)
    
    project_alias = generate_unique_alias("test_project")
    project = Project(
        alias=project_alias,
        title="Test Project - Arctic Soil Metagenomics",
        description="Automated test submission for dina-py library validation. This project studies microbial diversity in Arctic permafrost soils.",
        project_attributes=[
            Attribute(tag="Study Type", value="Metagenomics"),
            Attribute(tag="Data Policy", value="Open Access"),
        ]
    )
    
    print(f"Project alias: {project.alias}")
    print(f"Title: {project.title}")
    print("Submitting...")
    
    project_receipt = workflow.submit_project(project=project)
    
    print()
    print(format_receipt_summary(project_receipt))
    
    if project_receipt.success:
        project_accession = project_receipt.get_accession("PROJECT")
        project_status = project_receipt.get_status("PROJECT")
        print(f"\nProject submitted successfully!")
        if project_accession:
            print(f"\nProject Accession: {project_accession}")
            # print link if project is public
            if project_status == "PUBLIC":      
                print(f"View at: https://wwwdev.ebi.ac.uk/ena/browser/view/{project_accession}")
    else:
        print(f"\nProject submission failed")
        errors = project_receipt.get_errors()
        if errors:
            for error in errors:
                print(f"   Error: {error}")
    
    print()
    
    # =========================================================================
    # TEST 2: Submit a Sample
    # =========================================================================
    print("-" * 70)
    print("TEST 2: Sample Submission")
    print("-" * 70)
    
    sample_alias = generate_unique_alias("test_sample")
    sample = Sample(
        alias=sample_alias,
        title="Arctic Permafrost Soil Sample - Automated Test",
        organism=Organism(
            taxon_id=410658,  # soil metagenome
            scientific_name="soil metagenome"
        ),
        description="Automated test sample for dina-py library validation",
        attributes=[
            # Required MIxS attributes
            Attribute(tag="geographic location (country and/or sea)", value="Canada"),
            Attribute(tag="geographic location (latitude)", value="74.6895", unit="DD"),
            Attribute(tag="geographic location (longitude)", value="-94.8331", unit="DD"),
            Attribute(tag="collection date", value="2024-07-15"),
            Attribute(tag="environment (biome)", value="terrestrial biome"),
            Attribute(tag="environment (feature)", value="permafrost"),
            Attribute(tag="environment (material)", value="soil"),
            Attribute(tag="project name", value="Test Project - Arctic Soil"),
            Attribute(tag="investigation type", value="metagenome"),
            Attribute(tag="sequencing method", value="Illumina NovaSeq 6000"),
        ]
    )
    
    print(f"Sample alias: {sample.alias}")
    print(f"Title: {sample.title}")
    print(f"Organism: {sample.organism.scientific_name} (taxon ID: {sample.organism.taxon_id})")
    print(f"Attributes: {len(sample.attributes)} metadata fields")
    print("Submitting...")
    
    sample_receipt = workflow.submit_sample(sample=sample)
    
    print()
    print(format_receipt_summary(sample_receipt))
    
    if sample_receipt.success:
        sample_accession = sample_receipt.get_accession("SAMPLE")
        sample_status = sample_receipt.get_status("SAMPLE")
        print(f"\nSample submitted successfully!")
        if sample_accession:
            print(f"   Accession: {sample_accession}")
            # print view link is sample is public
            if sample_status == "PUBLIC":
                print(f"   View at: https://wwwdev.ebi.ac.uk/ena/browser/view/{sample_accession}")
    else:
        print(f"\nSample submission failed")
        errors = sample_receipt.get_errors()
        if errors:
            for error in errors:
                print(f"   Error: {error}")
    
    print()
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    project_status = "PASS" if project_receipt.success else "FAIL"
    sample_status = "PASS" if sample_receipt.success else "FAIL"
    
    print(f"Project submission: {project_status}")
    print(f"Sample submission:  {sample_status}")
    print()
    
    if project_receipt.success and sample_receipt.success:
        print("All tests passed!")
        print()
        print("Note: Test submissions are automatically deleted after 24 hours.")
        return 0
    else:
        print("Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())
