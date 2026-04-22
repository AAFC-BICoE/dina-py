"""
Example: Mapping DINA entities to ENA XML models

This example demonstrates the complete DINA → ENA submission workflow:

1. Pull data from DINA and deserialize into DINA DTOs using schemas
2. Map DINA DTOs to ENA models using mapper functions
3. Submit to ENA using ENASubmissionWorkflow

DINA → ENA Entity Mapping:
==========================
ENA PROJECT      ← DINA Project
ENA SAMPLE       ← DINA MaterialSample + CollectingEvent
ENA EXPERIMENT   ← DINA MolecularAnalysisRun + USER CONFIG (library/platform params)
ENA RUN          ← DINA Metadata (object store)

IMPORTANT: ENA Experiment requires user-provided sequencing parameters
(library_strategy, library_source, library_selection, library_layout_type,
instrument_model) that cannot be directly mapped from DINA.
"""
from dinapy.schemas.project_pydantic import ProjectDocument
from dinapy.schemas.material_sample_pydantic import MaterialSampleDocument
from dinapy.schemas.collecting_event_pydantic import CollectingEventDocument
from dinapy.schemas.molecular_analysis_run_pydantic import MolecularAnalysisRunDocument
from dinapy.schemas.metadata_pydantic import MetadataDocument

from dinapy.ena.mappers.dina_to_ena.mappers_dto import (
    project_to_ena,
    material_sample_to_ena,
    molecular_analysis_run_to_ena,
    metadata_to_ena_run,
    batch_material_samples_to_ena
)


def example_project_mapping():
    """Map a DINA Project to ENA Project."""
    
    # Example DINA API response
    dina_api_response = {
        "data": {
            "id": "project-123",
            "type": "project",
            "attributes": {
                "name": "Marine Microbiome Study",
                "multilingualDescription": {
                    "descriptions": [
                        {"desc": "Study of marine microbial communities in the North Atlantic", "lang": "en"}
                    ]
                },
                "group": "aafc",
                "createdBy": "researcher1",
                "createdOn": "2024-01-15T10:00:00Z"
            }
        }
    }
    
    # Deserialize using pydantic model
    project_dto = ProjectDocument.deserialize(dina_api_response).data
    
    # Map to ENA Project
    ena_project = project_to_ena(
        project=project_dto,
        description_override="Metagenomic study of marine bacterial communities"
    )
    
    print(f"ENA Project:")
    print(f"  Alias: {ena_project.alias}")
    print(f"  Title: {ena_project.title}")
    print(f"  Description: {ena_project.description}")
    
    return ena_project


def example_sample_mapping():
    """Map a DINA MaterialSample to ENA Sample."""
    
    # Example DINA MaterialSample API response
    material_sample_response = {
        "data": {
            "id": "sample-456",
            "type": "material-sample",
            "attributes": {
                "materialSampleName": "SeaWater_NA_001",
                "barcode": "SW001",
                "group": "aafc",
                "preparationDate": "2024-06-15",
                "managedAttributes": {},
                "allowDuplicateName": False,
                "isRestricted": False
            }
        }
    }
    
    # Example CollectingEvent API response
    collecting_event_response = {
        "data": {
            "id": "ce-789",
            "type": "collecting-event",
            "attributes": {
                "dwcCountry": "Canada",
                "dwcStateProvince": "Nova Scotia",
                "dwcVerbatimLocality": "Bedford Basin",
                "endEventDateTime": "2024-06-15T14:30:00.000Z",
                "group": "aafc",
                "managedAttributes": {}
            }
        }
    }
    
    # Deserialize using pydantic models
    material_sample_dto = MaterialSampleDocument.deserialize(material_sample_response).data
    collecting_event_dto = CollectingEventDocument.deserialize(collecting_event_response).data
    
    # Map to ENA Sample
    # Note: taxon_id should be resolved from scientific names using external taxonomy service
    ena_sample = material_sample_to_ena(
        material_sample=material_sample_dto,
        collecting_event=collecting_event_dto,
        taxon_id=408172,  # NCBI taxon ID for marine metagenome
        checklist="ERC000050",  # GSC MIxS water checklist
        geographic_location="Canada: Nova Scotia, Bedford Basin"
    )
    
    print(f"\nENA Sample:")
    print(f"  Alias: {ena_sample.alias}")
    print(f"  Title: {ena_sample.title}")
    print(f"  Taxon ID: {ena_sample.organism.taxon_id}")
    print(f"  Attributes: {len(ena_sample.attributes)}")
    for attr in ena_sample.attributes:
        print(f"    - {attr.tag}: {attr.value}")
    
    return ena_sample


def example_experiment_mapping():
    """
    Map a DINA MolecularAnalysisRun to ENA Experiment.
    
    NOTE: Unlike Project and Sample, the Experiment mapping requires USER-PROVIDED
    sequencing parameters that cannot be directly mapped from DINA. These include:
    - library_strategy
    - library_source  
    - library_selection
    - library_layout_type
    - instrument_model
    
    These values should come from user configuration, form inputs, or a lookup table.
    """
    
    # Example DINA MolecularAnalysisRun API response
    # DINA provides: id (alias), name (title), and metadata
    molecular_run_response = {
        "data": {
            "id": "run-101",
            "type": "molecular-analysis-run",
            "attributes": {
                "name": "NovaSeq_Run_2024_06",
                "group": "aafc",
                "createdBy": "lab_tech1",
                "createdOn": "2024-06-20T09:00:00Z"
            }
        }
    }
    
    # Deserialize using pydantic model
    molecular_run_dto = MolecularAnalysisRunDocument.deserialize(molecular_run_response).data
    
    # ========================================================================
    # USER MUST PROVIDE: Sequencing parameters that aren't in DINA
    # ========================================================================
    # In a real application, these would come from:
    # - User form/dropdown selections
    # - Configuration file
    # - Lookup table based on run type
    # - Protocol/SOP documentation
    
    user_config = {
        "library_strategy": "AMPLICON",
        "library_source": "METAGENOMIC",
        "library_selection": "PCR",
        "library_layout_type": "PAIRED",
        "instrument_model": "Illumina NovaSeq 6000"
    }
    
    # Map to ENA Experiment
    # Requires ENA accessions from already-submitted project and sample
    ena_experiment = molecular_analysis_run_to_ena(
        molecular_run=molecular_run_dto,  # From DINA
        study_accession="PRJEB12345",     # From previous project submission
        sample_accession="ERS567890",      # From previous sample submission
        library_strategy=user_config["library_strategy"],
        library_source=user_config["library_source"],
        library_selection=user_config["library_selection"],
        library_layout_type=user_config["library_layout_type"],
        instrument_model=user_config["instrument_model"],
        design_description="16S rRNA amplicon sequencing of marine samples",
        nominal_length=300,    # For paired-end
        nominal_sdev=50.0      # For paired-end
    )
    
    print(f"\nENA Experiment:")
    print(f"  Alias: {ena_experiment.alias}")
    print(f"  Title: {ena_experiment.title}")
    print(f"  Study Ref: {ena_experiment.study_ref.accession}")
    print(f"  Sample Ref: {ena_experiment.design.sample_descriptor.accession}")
    print(f"  Library Strategy: {ena_experiment.design.library_descriptor.library_strategy}")
    print(f"  Instrument: {ena_experiment.platform.instrument_model}")
    
    return ena_experiment


def example_run_mapping():
    """Map DINA Metadata (object store) to ENA Run."""
    
    # Example DINA Metadata API response
    metadata_response = {
        "data": {
            "id": "metadata-202",
            "type": "metadata",
            "attributes": {
                "acCaption": "SeaWater NA 001 - Forward Reads",
                "originalFilename": "SW001_R1.fastq.gz",
                "filename": "SW001_R1.fastq.gz",
                "fileExtension": "fastq.gz",
                "bucket": "sequencing-data",
                "acHashValue": "d41d8cd98f00b204e9800998ecf8427e",
                "acHashFunction": "MD5",
                "group": "aafc"
            }
        }
    }
    
    # Deserialize using pydantic model
    metadata_dto = MetadataDocument.deserialize(metadata_response).data
    
    # Map to ENA Run
    ena_run = metadata_to_ena_run(
        metadata=metadata_dto,
        experiment_accession="ERX123456",  # ENA experiment accession
        # filetype and checksum will be derived from metadata attributes
    )
    
    print(f"\nENA Run:")
    print(f"  Alias: {ena_run.alias}")
    print(f"  Title: {ena_run.title}")
    print(f"  Experiment Ref: {ena_run.experiment_ref.accession}")
    print(f"  Files:")
    for data_block in ena_run.data_blocks:
        for file_obj in data_block.files:
            print(f"    - {file_obj.filename} ({file_obj.filetype})")
            print(f"      Checksum ({file_obj.checksum_method}): {file_obj.checksum}")
    
    return ena_run


def example_batch_mapping():
    """Batch map multiple DINA MaterialSamples to ENA Samples."""
    
    # Example: Multiple material samples
    sample_responses = [
        {
            "data": {
                "id": f"sample-{i}",
                "type": "material-sample",
                "attributes": {
                    "materialSampleName": f"SeaWater_NA_{i:03d}",
                    "barcode": f"SW{i:03d}",
                    "group": "aafc",
                    "allowDuplicateName": False,
                    "isRestricted": False
                }
            }
        }
        for i in range(1, 4)
    ]
    
    # Deserialize all samples
    material_sample_dtos = [
        MaterialSampleDocument.deserialize(resp).data for resp in sample_responses
    ]
    
    # Prepare taxon IDs (in real scenario, resolve from scientific names)
    taxon_ids = {
        "sample-1": 408172,  # marine metagenome
        "sample-2": 408172,
        "sample-3": 408172
    }
    
    # Batch map to ENA Samples
    ena_samples = batch_material_samples_to_ena(
        material_samples=material_sample_dtos,
        taxon_ids=taxon_ids,
        checklist="ERC000050"
    )
    
    print(f"\nBatch Mapped {len(ena_samples)} samples:")
    for sample in ena_samples:
        print(f"  - {sample.alias}: {sample.title}")
    
    return ena_samples


if __name__ == "__main__":
    print("=" * 80)
    print("DINA to ENA Mapping Examples")
    print("=" * 80)
    print()
    print("Workflow Overview:")
    print("  1. Pull data from DINA API and deserialize to DTOs")
    print("  2. Map DINA DTOs to ENA models:")
    print("       - ENA PROJECT      ← DINA Project")
    print("       - ENA SAMPLE       ← DINA MaterialSample + CollectingEvent")
    print("       - ENA EXPERIMENT   ← DINA MolecularAnalysisRun + USER CONFIG")
    print("       - ENA RUN          ← DINA Metadata")
    print("  3. Submit to ENA using ENASubmissionWorkflow")
    print()
    print("NOTE: Experiment mapping requires user-provided sequencing parameters")
    print("      (library strategy, source, selection, layout, instrument model)")
    print()
    print("=" * 80)
    
    # Run examples
    example_project_mapping()
    example_sample_mapping()
    example_experiment_mapping()
    example_run_mapping()
    example_batch_mapping()
    
    print("\n" + "=" * 80)
    print("All examples completed!")
    print("Next steps: Use ENASubmissionWorkflow to submit to ENA")
    print("=" * 80)
