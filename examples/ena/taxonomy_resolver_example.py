"""
Example: Using the NCBI Taxonomy Resolver with DINA to ENA Mappers

This example shows how to:
1. Manually resolve taxon IDs from scientific names
2. Automatically resolve taxon IDs during mapping
3. Use a cache to avoid duplicate NCBI API calls
"""

from dinapy.schemas.material_sample_pydantic import MaterialSampleDocument
from dinapy.ena.mappers.dina_to_ena.mappers_dto import (
    material_sample_to_ena,
    batch_material_samples_to_ena,
    resolve_taxon_id_from_scientific_name,
    extract_scientific_name_from_material_sample
)


# =============================================================================
# Example 1: Manually resolve a taxon ID
# =============================================================================

def example_manual_taxonomy_lookup():
    """Manually look up taxon IDs from scientific names."""
    print("Example 1: Manual taxonomy lookup")
    print("=" * 60)
    
    # Some common scientific names
    organisms = [
        "Homo sapiens",
        "Escherichia coli",
        "Saccharomyces cerevisiae",
        "Arabidopsis thaliana"
    ]
    
    for sci_name in organisms:
        taxon_id = resolve_taxon_id_from_scientific_name(
            scientific_name=sci_name,
            email="your.email@institution.edu"  # Replace with your email
        )
        print(f"{sci_name:30} -> NCBI:txid{taxon_id}")
    
    print()


# =============================================================================
# Example 2: Auto-resolve during single sample mapping
# =============================================================================

def example_single_sample_auto_resolve():
    """Map a single material sample with automatic taxon ID resolution."""
    print("Example 2: Single sample with auto-resolve")
    print("=" * 60)
    
    # Simulated DINA API response for a material sample
    material_sample_json = {
        "data": {
            "id": "sample-123",
            "type": "material-sample",
            "attributes": {
                "materialSampleName": "Fish specimen 001",
                "group": "aafc",
                "barcode": "FISH001",
                "managedAttributes": {
                    "scientificName": "Salmo salar"  # Atlantic salmon
                },
                "allowDuplicateName": False,
                "isRestricted": False
            }
        }
    }
    
    # Deserialize using pydantic model
    material_sample_dto = MaterialSampleDocument.deserialize(material_sample_json).data
    
    # Map to ENA Sample - taxon ID will be auto-resolved
    ena_sample = material_sample_to_ena(
        material_sample=material_sample_dto,
        email="your.email@institution.edu",
        checklist="ERC000011"  # GSC MIxS host associated
    )
    
    print(f"Sample alias: {ena_sample.alias}")
    print(f"Sample title: {ena_sample.title}")
    print(f"Taxon ID: {ena_sample.organism.taxon_id}")
    print(f"  (Salmo salar should resolve to NCBI:txid8030)")
    print()


# =============================================================================
# Example 3: Batch mapping with taxonomy cache
# =============================================================================

def example_batch_with_cache():
    """Batch map multiple samples using a shared taxonomy cache."""
    print("Example 3: Batch mapping with taxonomy cache")
    print("=" * 60)
    
    # Simulated list of material samples
    samples_json = [
        {
            "data": {
                "id": "sample-001",
                "type": "material-sample",
                "attributes": {
                    "materialSampleName": "E. coli strain K12",
                    "group": "aafc",
                    "managedAttributes": {
                        "scientificName": "Escherichia coli"
                    },
                    "allowDuplicateName": False,
                    "isRestricted": False
                }
            }
        },
        {
            "data": {
                "id": "sample-002",
                "type": "material-sample",
                "attributes": {
                    "materialSampleName": "E. coli strain DH5alpha",
                    "group": "aafc",
                    "managedAttributes": {
                        "scientificName": "Escherichia coli"  # Same species
                    },
                    "allowDuplicateName": False,
                    "isRestricted": False
                }
            }
        },
        {
            "data": {
                "id": "sample-003",
                "type": "material-sample",
                "attributes": {
                    "materialSampleName": "Yeast culture",
                    "group": "aafc",
                    "managedAttributes": {
                        "scientificName": "Saccharomyces cerevisiae"
                    },
                    "allowDuplicateName": False,
                    "isRestricted": False
                }
            }
        }
    ]
    
    # Deserialize all samples
    material_sample_dtos = [
        MaterialSampleDocument.deserialize(s).data for s in samples_json
    ]
    
    # Batch map - taxonomy cache will prevent duplicate NCBI lookups
    ena_samples = batch_material_samples_to_ena(
        material_samples=material_sample_dtos,
        email="your.email@institution.edu",
        auto_resolve_taxa=True  # Enable auto-resolution
    )
    
    print(f"Mapped {len(ena_samples)} samples:")
    for sample in ena_samples:
        print(f"  - {sample.alias}: {sample.title} (taxon: {sample.organism.taxon_id})")
    
    print("\nNote: E. coli taxon ID should be 562")
    print("Note: S. cerevisiae taxon ID should be 4932")
    print()


# =============================================================================
# Example 4: Using organism data from DINA relationships
# =============================================================================

def example_with_organism_relationship():
    """Map sample using organism data from DINA organism relationship."""
    print("Example 4: Using DINA organism relationship")
    print("=" * 60)
    
    # Material sample
    material_sample_json = {
        "data": {
            "id": "sample-456",
            "type": "material-sample",
            "attributes": {
                "materialSampleName": "Plant specimen 042",
                "group": "aafc",
                "allowDuplicateName": False,
                "isRestricted": False
            }
        }
    }
    
    # Organism data from DINA organism relationship
    # (fetched separately via organism API)
    organism_data = {
        "data": {
            "id": "org-789",
            "type": "organism",
            "attributes": {
                "determination": [
                    {
                        "scientificName": "Arabidopsis thaliana",
                        "isPrimary": True,
                        "determiner": "Jane Smith",
                        "determinedOn": "2024-03-15"
                    }
                ]
            }
        }
    }
    
    # Deserialize
    material_sample_dto = MaterialSampleDocument.deserialize(material_sample_json).data
    
    # Map with organism data
    ena_sample = material_sample_to_ena(
        material_sample=material_sample_dto,
        organism_data=organism_data,
        email="your.email@institution.edu"
    )
    
    print(f"Sample: {ena_sample.title}")
    print(f"Taxon ID: {ena_sample.organism.taxon_id}")
    print(f"  (A. thaliana should resolve to NCBI:txid3702)")
    print()


# =============================================================================
# Example 5: Pre-resolved taxon IDs (skip NCBI lookup)
# =============================================================================

def example_pre_resolved_taxa():
    """Use pre-resolved taxon IDs to skip NCBI API calls."""
    print("Example 5: Pre-resolved taxon IDs")
    print("=" * 60)
    
    # If you've already resolved taxon IDs, you can provide them directly
    material_sample_json = {
        "data": {
            "id": "sample-999",
            "type": "material-sample",
            "attributes": {
                "materialSampleName": "Human tissue sample",
                "group": "aafc",
                "allowDuplicateName": False,
                "isRestricted": False
            }
        }
    }
    
    material_sample_dto = MaterialSampleDocument.deserialize(material_sample_json).data
    
    # Provide taxon ID directly (Homo sapiens = 9606)
    ena_sample = material_sample_to_ena(
        material_sample=material_sample_dto,
        taxon_id=9606  # Pre-resolved, no NCBI lookup needed
    )
    
    print(f"Sample: {ena_sample.title}")
    print(f"Taxon ID: {ena_sample.organism.taxon_id}")
    print("  (Provided directly, no NCBI lookup performed)")
    print()


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("\n")
    print("DINA to ENA Taxonomy Resolver Examples")
    print("=" * 60)
    print()
    
    # Run examples
    # NOTE: Uncomment to run (requires internet connection for NCBI API)
    
    example_manual_taxonomy_lookup()
    example_single_sample_auto_resolve()
    example_batch_with_cache()
    example_with_organism_relationship()
    example_pre_resolved_taxa()
    
    print("\n")
    print("To run these examples:")
    print("1. Uncomment the example functions above")
    print("2. Replace 'your.email@institution.edu' with your email")
    print("3. Ensure you have internet connection for NCBI API access")
    print("4. Run: python examples/ena/taxonomy_resolver_example.py")
    print()
