"""
Submit an ENA Project (Study) via Webin API

This is a simple example showing how to submit a project to ENA.
Copy this code into a Jupyter notebook or run it as a standalone script.

Environment variables required:
    WEBIN_USERNAME: ENA Webin account username
    WEBIN_PASSWORD: ENA Webin account password
    WEBIN_TEST: Set to 'true' for test server (default: true)
"""

from dinapy.ena.models import Project, Attribute
from dinapy.ena.submission import ENASubmissionWorkflow


# ============================================================================
# 1. Create Project Model
# ============================================================================

project = Project(
    alias="my_project_001",
    title="Microbial Diversity in Arctic Soils",
    description="A comprehensive study examining bacterial and fungal diversity in permafrost-affected soils from the Canadian Arctic archipelago.",
    project_attributes=[
        Attribute(tag="Study Type", value="Metagenomics"),
        Attribute(tag="Data Policy", value="Open Access"),
    ]
)

print("Project to submit:")
print(f"  Alias: {project.alias}")
print(f"  Title: {project.title}")
print(f"  Description: {project.description[:50]}...")
print(f"  Attributes: {len(project.project_attributes or [])} custom attributes")
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
# 3. Submit Project
# ============================================================================

receipt = workflow.submit_project(
    project=project,
    center_name=None  # Optional: specify your center name
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
    project_accession = receipt.get_accession("PROJECT")
    if project_accession:
        print(f"\nProject Accession: {project_accession}")
        print(f"View at: https://wwwdev.ebi.ac.uk/ena/browser/view/{project_accession}")
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
