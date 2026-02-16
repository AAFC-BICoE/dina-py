"""
Complete DINA → ENA Submission Workflow Example

This example demonstrates the full end-to-end workflow for submitting
sequencing data from DINA to ENA:

1. Pull data from DINA API
2. Deserialize into DINA DTOs using schemas  
3. Map DINA DTOs to ENA models
4. Submit to ENA and handle receipts

DINA → ENA Entity Mapping:
==========================
ENA PROJECT      ← DINA Project
ENA SAMPLE       ← DINA MaterialSample + CollectingEvent  
ENA EXPERIMENT   ← DINA MolecularAnalysisRun + USER CONFIG
ENA RUN          ← DINA Metadata (object store)

Requirements:
- WEBIN_USERNAME and WEBIN_PASSWORD environment variables
- Sequence files uploaded to ENA FTP before submitting RUN
"""
from pathlib import Path
from typing import Dict, Any
import os
import time
from datetime import date
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# DINA schemas for deserialization
from dinapy.schemas.project_schema import ProjectSchema
from dinapy.schemas.materialsampleschema import MaterialSampleSchema
from dinapy.schemas.collectingeventschema import CollectingEventSchema
from dinapy.schemas.molecular_analysis_run_schema import MolecularAnalysisRunSchema
from dinapy.schemas.metadata_schema import MetadataSchema

# DINA → ENA mappers
from dinapy.ena.mappers.dina_to_ena.mappers_dto import (
    project_to_ena,
    material_sample_to_ena,
    molecular_analysis_run_to_ena,
    metadata_to_ena_run
)

# ENA submission workflow
from dinapy.ena.submission import ENASubmissionWorkflow


def complete_submission_workflow():
    """
    Complete example of DINA → ENA submission workflow.
    
    This function demonstrates:
    1. Fetching data from DINA (simulated with mock data)
    2. Mapping DINA DTOs to ENA models
    3. Submitting to ENA test server
    4. Handling receipts and accessions
    """
    
    # ========================================================================
    # STEP 1: Pull data from DINA API
    # ========================================================================
    print("=" * 80)
    print("STEP 1: Fetching data from DINA")
    print("=" * 80)
    
    # In a real application, you would fetch from DINA API:
    # from dinapy.client.dina_api_client import DinaApiClient
    # client = DinaApiClient(base_url="https://dina.example.com/api", api_key="...")
    # project_response = client.get("project/project-123")
    
    # For this example, we'll use mock DINA API responses
    project_response = {
        "data": {
            "id": "project-marine-2024",
            "type": "project",
            "attributes": {
                "name": "Marine Microbiome Study 2024",
                "multilingualDescription": {
                    "descriptions": [{
                        "desc": "Metagenomic analysis of marine bacterial communities in Atlantic coastal waters",
                        "lang": "en"
                    }]
                },
                "group": "marine-lab",
                "startDate": "2024-01-01",
                "status": "Active"
            }
        }
    }
    
    material_sample_response = {
        "data": {
            "id": "019a26c5-3463-7b8f-a7bb-c620eb74f1bd",
            "type": "material-sample",
            "attributes": {
                "version": 1,
                "group": "overy-lab",
                "createdOn": "2025-10-27T17:44:09.561756Z",
                "createdBy": "hermansa",
                "dwcCatalogNumber": None,
                "dwcOtherCatalogNumbers": [
                    "IBT 12396; DAOMC251664; DAOM749218"
                ],
                "materialSampleName": "KAS2398-7",
                "identifiers": {},
                "materialSampleType": "MOLECULAR_SAMPLE",
                "preparationDate": None,
                "preservationType": None,
                "preparationFixative": None,
                "preparationMaterials": None,
                "preparationSubstrate": None,
                "managedAttributes": {
                    "notes": "Inoculation done by R.Assabgui",
                    "fraction": "0",
                    "fermentation_time": "15d",
                    "fermentation_type": "Agar Plug",
                    "extraction_solvent": "ethyl acetate",
                    "fermentation_media": "CYA",
                    "resuspension_solvent": "methanol",
                    "fermentation_temperature": "25"
                },
                "preparationManagedAttributes": {
                    "inoculation_date": "2017-06-12"
                },
                "extensionValues": {},
                "preparationRemarks": None,
                "dwcDegreeOfEstablishment": None,
                "targetOrganismPrimaryScientificName": "Penicillium hesseltinei",
                "targetOrganismPrimaryClassification": {
                    "phylum": "Ascomycota",
                    "genus": "Penicillium",
                    "species": "hesseltinei",
                    "family": "Aspergillaceae",
                    "kingdom": "Fungi",
                    "class": "Eurotiomycetes",
                    "order": "Eurotiales"
                },
                "barcode": None,
                "publiclyReleasable": None,
                "notPubliclyReleasableReason": None,
                "tags": None,
                "materialSampleState": None,
                "materialSampleRemarks": None,
                "stateChangedOn": None,
                "stateChangeRemarks": None,
                "allowDuplicateName": False,
                "restrictionFieldsExtension": {},
                "isRestricted": False,
                "restrictionRemarks": None,
                "sourceSet": "wb_upload_1767721328746",
                "isBaseForSplitByType": None,
                "associations": []
            },
            "relationships": {
                "organism": {
                    "data": [
                        {
                            "id": "019b9466-e0f2-7f12-ba61-c888688abfd3",
                            "type": "organism"
                        }
                    ]
                },
                "collection": {
                    "data": {
                        "id": "01975b31-cb4b-7865-95e0-9ae7a47c8d68",
                        "type": "collection"
                    }
                }
            }
        },
        "included": [
            {
                "id": "01975b31-cb4b-7865-95e0-9ae7a47c8d68",
                "type": "collection",
                "attributes": {
                    "createdOn": "2025-06-10T18:54:39.548401Z",
                    "createdBy": "hermansa",
                    "group": "overy-lab",
                    "name": "KAS Collection",
                    "code": "KAS",
                    "multilingualDescription": {
                        "descriptions": [
                            {
                                "lang": "en",
                                "desc": "Collection of fungal strains from Keith Seifert, AAFC"
                            }
                        ]
                    },
                    "webpage": None,
                    "contact": None,
                    "address": None,
                    "remarks": None
                }
            },
            {
                "id": "019b9466-e0f2-7f12-ba61-c888688abfd3",
                "type": "organism",
                "attributes": {
                    "group": "overy-lab",
                    "isTarget": None,
                    "lifeStage": None,
                    "sex": None,
                    "remarks": None,
                    "dwcVernacularName": None,
                    "managedAttributes": {},
                    "determination": [
                        {
                            "verbatimScientificName": "Penicillium hesseltinei",
                            "verbatimDeterminer": None,
                            "verbatimDate": None,
                            "scientificName": None,
                            "transcriberRemarks": None,
                            "verbatimRemarks": None,
                            "determinationRemarks": None,
                            "typeStatus": None,
                            "typeStatusEvidence": None,
                            "determiner": None,
                            "determinedOn": None,
                            "qualifier": None,
                            "scientificNameSource": "CUSTOM",
                            "scientificNameDetails": {
                                "labelHtml": None,
                                "classificationPath": "Fungi|Ascomycota|Eurotiomycetes|Eurotiales|Aspergillaceae|Penicillium|hesseltinei",
                                "classificationRanks": "kingdom|phylum|class|order|family|genus|species",
                                "sourceUrl": None,
                                "recordedOn": None,
                                "currentName": None,
                                "isSynonym": None
                            },
                            "isPrimary": True,
                            "isFiledAs": None,
                            "managedAttributes": None
                        }
                    ],
                    "createdOn": "2026-01-06T17:42:08.883202Z",
                    "createdBy": "hermansa"
                }
            }
        ],
        "meta": {
            "moduleVersion": "0.113"
        }
        }
    
    collecting_event_response = {
    "data":
        {
            "id": "99394b6d-14fd-4d57-906f-3c5b3c6b0721",
            "type": "collecting-event",
            "attributes": {
                "version": 0,
                "dwcFieldNumber": None,
                "dwcRecordNumber": None,
                "otherRecordNumbers": None,
                "group": "phillips-lab",
                "createdBy": "s-seqdbsoil",
                "createdOn": "2024-03-07T14:53:50.83186Z",
                "geoReferenceAssertions": [
                    {
                        "dwcDecimalLatitude": 45.38021304178923,
                        "dwcDecimalLongitude": -75.71705545760129,
                        "dwcCoordinateUncertaintyInMeters": None,
                        "createdOn": "2024-03-07T14:53:50.832872921Z",
                        "dwcGeoreferencedDate": None,
                        "georeferencedBy": None,
                        "literalGeoreferencedBy": None,
                        "dwcGeoreferenceProtocol": None,
                        "dwcGeoreferenceSources": None,
                        "dwcGeoreferenceRemarks": None,
                        "dwcGeodeticDatum": None,
                        "isPrimary": True,
                        "dwcGeoreferenceVerificationStatus": None
                    }
                ],
                "eventGeom": {
                    "type": "Point",
                    "crs": {
                        "type": "name",
                        "properties": {
                            "name": "EPSG:4326"
                        }
                    },
                    "coordinates": [
                        -75.71705545760129,
                        45.38021304178923
                    ]
                },
                "dwcVerbatimCoordinates": "45.38021304178923 -75.71705545760129",
                "dwcRecordedBy": None,
                "startEventDateTime": "2018-11-08",
                "endEventDateTime": None,
                "verbatimEventDateTime": None,
                "dwcVerbatimLocality": None,
                "host": None,
                "managedAttributes": {
                    "site_codes": "CEF",
                    "seq_db_legacy": "{\"Collection Info\":{\"id\":1056766,\"latitude\":\"45.38021304178923\",\"longitude\":\"-75.71705545760129\",\"year\":\"2018\",\"month\":\"11\",\"day\":\"08\",\"zeroPaddedDate\":\"2018-11-008\",\"notes\":\"Cores kept intact and on ice until transport back to lab\",\"elevation\":70.0,\"depth\":\"0.35-0.50\",\"lastModified\":\"2021-05-10T23:06:01.586+00:00\",\"latLon\":\"45.38021304178923 -75.71705545760129\",\"siteCodes\":\"CEF\",\"protocol\":{\"id\":227,\"type\":\"COLLECTION_EVENT\",\"name\":\"AAFC_Phillips_FieldTrialSampling_2020.docx\",\"version\":\"\",\"description\":\"\",\"steps\":\"\",\"notes\":\"\",\"reference\":\"\",\"equipment\":\"\",\"forwardPrimerConcentration\":\"\",\"reversePrimerConcentration\":\"\",\"reactionMixVolume\":\"\",\"reactionMixVolumePerTube\":\"\",\"group\":{\"id\":458,\"groupName\":\"GI_Phillips\",\"description\":\"\",\"defaultRead\":false,\"defaultWrite\":false,\"defaultDelete\":false,\"defaultCreate\":false,\"lastModified\":\"2021-01-15T16:25:33.348+00:00\"},\"reactionComponents\":[{\"reactionComponentId\":1073,\"name\":\"\",\"concentration\":\"\",\"lastModified\":\"2021-03-05T00:51:36.746+00:00\",\"id\":1073}],\"lastModified\":\"2021-03-05T00:51:36.667+00:00\"}},\"MIxS Specifications\":{\"id\":786796,\"envPackage\":\"Soil\",\"dnaStorageConditions\":\"neg 80oC; up to 14months\",\"sampVolWeDnaExt\":\"0.25g\",\"waterContent\":\"0.15795519816197587\",\"curLandUse\":\"\",\"curVegetation\":\"\",\"curVegetationMeth\":\"Visual\",\"waterContentSoilMeth\":\"Gravimetric (dry)\",\"poolDnaExtracts\":\"Yes; 2 x 0.25g\",\"storeCond\":\"6months/-80oC\",\"linkClimateInfo\":\"https://climate.weather.gc.ca/climate_normals/index_e.html\",\"annualSeasonTemp\":\"6.6\",\"growingDegreeDays\":\"2135\",\"lastModified\":\"2021-05-10T23:06:01.588+00:00\"}}",
                    "growing_degree_days": "2135"
                },
                "dwcVerbatimLatitude": "45.38021304178923",
                "dwcVerbatimLongitude": "-75.71705545760129",
                "dwcVerbatimCoordinateSystem": None,
                "dwcVerbatimSRS": None,
                "dwcVerbatimElevation": None,
                "dwcVerbatimDepth": None,
                "dwcCountry": "Canada",
                "dwcCountryCode": None,
                "dwcStateProvince": None,
                "habitat": None,
                "dwcMinimumElevationInMeters": 70.00,
                "dwcMinimumDepthInMeters": 0.35,
                "dwcMaximumElevationInMeters": None,
                "dwcMaximumDepthInMeters": 0.50,
                "substrate": None,
                "remarks": "Cores kept intact and on ice until transport back to lab",
                "publiclyReleasable": None,
                "notPubliclyReleasableReason": None,
                "tags": None,
                "geographicPlaceNameSource": None,
                "geographicPlaceNameSourceDetail": None,
                "geographicThesaurus": None,
                "extensionValues": {
                    "mixs_soil_v4": {
                        "store_cond": "6months/-80oC",
                        "env_package": "Soil",
                        "water_content": "0.15795519816197587",
                        "link_climate_info": "https://climate.weather.gc.ca/climate_normals/index_e.html",
                        "pool_dna_extracts": "Yes; 2 x 0.25g",
                        "annual_season_temp": "6.6",
                        "cur_vegetation_meth": "Visual",
                        "samp_vol_we_dna_ext": "0.25g",
                        "water_content_soil_meth": "Gravimetric (dry)"
                    },
                    "mixs_soil_v5": {
                        "dna_storage_conditons": "neg 80oC; up to 14months"
                    }
                }
            }
        }
    }
    
    molecular_run_response = {
        "data": {
            "id": "run-novaseq-202406",
            "type": "molecular-analysis-run",
            "attributes": {
                "name": "NovaSeq_Marine_June2024",
                "group": "marine-lab"
            }
        }
    }
    
    metadata_response = {
       "data": {
            "id": "0195d323-6f68-74b3-a323-985d87d3bbc5",
            "type": "metadata",
            "attributes": {
                "createdBy": "s-data-migration",
                "createdOn": "2025-03-26T15:47:49.737271Z",
                "bucket": "gagne-lab",
                "fileIdentifier": "0195d323-3f63-7e3b-a38c-79521487c9c9",
                "originalFilename": "AT30-7.xls",
                "filename": None,
                "fileExtension": ".xls",
                "resourceExternalURL": None,
                "sourceSet": None,
                "dcFormat": "application/vnd.ms-excel",
                "dcType": "UNDETERMINED",
                "acCaption": "AT30-7.xls",
                "acDigitizationDate": None,
                "xmpMetadataDate": "2025-03-26T15:47:49.739512Z",
                "xmpRightsWebStatement": "https://open.canada.ca/en/open-government-licence-canada",
                "dcRights": "© His Majesty The King in Right of Canada, as represented by the Minister of Agriculture and Agri-Food | © Sa Majesté le Roi du chef du Canada, représentée par le ministre de l’Agriculture et de l’Agroalimentaire",
                "xmpRightsOwner": "Government of Canada",
                "xmpRightsUsageTerms": "Government of Canada Usage Term",
                "orientation": None,
                "acHashFunction": "SHA-1",
                "acHashValue": "60b7fd2ea5b8e8117e2d476ea9b519dc99f026fa",
                "publiclyReleasable": False,
                "notPubliclyReleasableReason": "default based on Type : Undetermined",
                "group": "gagne-lab",
                "managedAttributes": {}
            }
        }
    }
    
    print(f"✓ Fetched Project: {project_response['data']['id']}")
    print(f"✓ Fetched MaterialSample: {material_sample_response['data']['id']}")
    print(f"✓ Fetched CollectingEvent: {collecting_event_response['data']['id']}")
    print(f"✓ Fetched MolecularAnalysisRun: {molecular_run_response['data']['id']}")
    print(f"✓ Fetched Metadata: {metadata_response['data']['id']}")
    print()
    
    # ========================================================================
    # STEP 2: Deserialize DINA responses into DTOs
    # ========================================================================
    print("=" * 80)
    print("STEP 2: Deserializing DINA data using schemas")
    print("=" * 80)
    
    project_dto = ProjectSchema().load(project_response)
    material_sample_dto = MaterialSampleSchema().load(material_sample_response)
    collecting_event_dto = CollectingEventSchema().load(collecting_event_response)
    molecular_run_dto = MolecularAnalysisRunSchema().load(molecular_run_response)
    metadata_dto = MetadataSchema().load(metadata_response)
    
    print("✓ Deserialized all DINA entities into DTOs")
    print()
    
    # ========================================================================
    # STEP 3: Map DINA DTOs to ENA models
    # ========================================================================
    print("=" * 80)
    print("STEP 3: Mapping DINA DTOs to ENA models")
    print("=" * 80)
    
    # Generate timestamp for unique aliases
    timestamp = str(int(time.time()))
    print(f"Using timestamp: {timestamp}")
    print()
    
    # Map Project
    ena_project = project_to_ena(
        project=project_dto,
        include_unmapped=True
    )
    ena_project.alias = f"{ena_project.alias}_{timestamp}"
    print(f"✓ Mapped Project: {ena_project.alias}")
    print(f"  Title: {ena_project.title}")
    print(f"  Unmapped attributes: {len([a for a in ena_project.attributes if not a.tag.startswith('ENA')])}")
    
    # Map Sample (with auto-resolved taxon ID)
    ena_sample = material_sample_to_ena(
        material_sample=material_sample_dto,
        collecting_event=collecting_event_dto,
        taxon_id=408172,  # NCBI taxon: marine metagenome
        email="researcher@example.com",  # For NCBI lookups if needed
        include_unmapped=True
    )
    ena_sample.alias = f"{ena_sample.alias}_{timestamp}"
    print(f"✓ Mapped Sample: {ena_sample.alias}")
    print(f"  Title: {ena_sample.title}")
    print(f"  Taxon: {ena_sample.organism.taxon_id}")
    print(f"  Total attributes: {len(ena_sample.attributes)}")
    
    # Map Experiment - USER MUST PROVIDE sequencing parameters
    # These parameters cannot be mapped from DINA and must come from user config
    user_sequencing_config = {
        "library_strategy": "AMPLICON",
        "library_source": "METAGENOMIC",
        "library_selection": "PCR",
        "library_layout_type": "PAIRED",
        "instrument_model": "Illumina NovaSeq 6000"
    }
    
    print(f"✓ User sequencing configuration:")
    for key, value in user_sequencing_config.items():
        print(f"    {key}: {value}")
    
    # Note: We'll need ENA accessions after submitting project and sample
    # For now, we'll use dummy accessions in the mapping
    ena_experiment = molecular_analysis_run_to_ena(
        molecular_run=molecular_run_dto,
        study_accession="PLACEHOLDER_PROJECT",  # Will be replaced after project submission
        sample_accession="PLACEHOLDER_SAMPLE",  # Will be replaced after sample submission
        library_strategy=user_sequencing_config["library_strategy"],
        library_source=user_sequencing_config["library_source"],
        library_selection=user_sequencing_config["library_selection"],
        library_layout_type=user_sequencing_config["library_layout_type"],
        instrument_model=user_sequencing_config["instrument_model"],
        design_description="16S rRNA amplicon sequencing of marine water samples",
        nominal_length=300,
        nominal_sdev=50.0,
        include_unmapped=True
    )
    ena_experiment.alias = f"{ena_experiment.alias}_{timestamp}"
    print(f"✓ Mapped Experiment: {ena_experiment.alias}")
    print(f"  Title: {ena_experiment.title}")
    
    # Map Run
    ena_run = metadata_to_ena_run(
        metadata=metadata_dto,
        experiment_accession="PLACEHOLDER_EXPERIMENT",  # Will be replaced after experiment submission
        filetype="fastq",
        include_unmapped=True
    )
    ena_run.alias = f"{ena_run.alias}_{timestamp}"
    print(f"✓ Mapped Run: {ena_run.alias}")
    print(f"  Title: {ena_run.title}")
    print(f"  Files: {len(ena_run.data_blocks[0].files)}")
    print()
    
    # ========================================================================
    # STEP 4: Initialize ENA submission workflow
    # ========================================================================
    print("=" * 80)
    print("STEP 4: Initializing ENA submission workflow")
    print("=" * 80)
    
    # Check for credentials
    if not os.getenv("WEBIN_USERNAME") or not os.getenv("WEBIN_PASSWORD"):
        print("⚠ WARNING: WEBIN_USERNAME and WEBIN_PASSWORD not set")
        print("⚠ Cannot proceed with actual submission")
        print()
        print("To submit to ENA test server, set environment variables:")
        print("  export WEBIN_USERNAME=Webin-XXXXX")
        print("  export WEBIN_PASSWORD=your_password")
        print()
        print("=" * 80)
        print("Workflow demonstration complete (without actual submission)")
        print("=" * 80)
        return
    
    workflow = ENASubmissionWorkflow(
        username=os.getenv("WEBIN_USERNAME"),
        password=os.getenv("WEBIN_PASSWORD"),
        test=True  # Use test server
    )
    print("✓ Initialized ENASubmissionWorkflow (test mode)")
    print()
    
    # ========================================================================
    # STEP 5: Submit to ENA (in correct order)
    # ========================================================================
    print("=" * 80)
    print("STEP 5: Submitting to ENA")
    print("=" * 80)
    
    # 5a. Submit Project with hold date set to present day
    today = date.today().isoformat()
    print("\n[1/4] Submitting Project...")
    
    try:
        project_receipt = workflow.submit_project_xml(
            ena_project, 
            action="ADD",
            hold_until_date=today
        )
        if project_receipt.success:
            project_accession = project_receipt.get_accession("PROJECT")
            print(f"✓ Project submitted with ADD + HOLD (today)")
            print(f"  Accession: {project_accession}")
            print(f"  Hold date: {today} (today - should be public immediately)")
        else:
            print(f"✗ Project submission failed:")
            for msg in project_receipt.messages:
                print(f"    {msg.type}: {msg.text}")
            return
    except Exception as e:
        print(f"✗ Exception during project submission: {e}")
        return
    
    # 5b. Submit Sample with hold date set to today
    print("\n[2/4] Submitting Sample...")
    print(f"  Note: Using hold_until_date={today} (today) for immediate release")
    try:
        sample_receipt = workflow.submit_sample_xml(
            ena_sample, 
            action="ADD",
            hold_until_date=today
        )
        if sample_receipt.success:
            sample_accession = sample_receipt.get_accession("SAMPLE")
            print(f"✓ Sample submitted with ADD + HOLD (today)")
            print(f"  Accession: {sample_accession}")
        else:
            print(f"✗ Sample submission failed:")
            for msg in sample_receipt.messages:
                print(f"    {msg.type}: {msg.text}")
            return
    except Exception as e:
        print(f"✗ Exception during sample submission: {e}")
        return
    
    # 5c. Create and submit Experiment
    print("\n[3/4] Submitting Experiment...")
    print(f"  Using Project Accession: {project_accession}")
    print(f"  Using Sample Accession: {sample_accession}")

    ena_experiment = molecular_analysis_run_to_ena(
        molecular_run=molecular_run_dto,
        study_accession=project_accession,
        sample_accession=sample_accession,
        library_strategy=user_sequencing_config["library_strategy"],
        library_source=user_sequencing_config["library_source"],
        library_selection=user_sequencing_config["library_selection"],
        library_layout_type=user_sequencing_config["library_layout_type"],
        instrument_model=user_sequencing_config["instrument_model"],
        design_description="16S rRNA amplicon sequencing of marine water samples",
        nominal_length=300,
        nominal_sdev=50.0,
        include_unmapped=True
    )
    ena_experiment.alias = f"{ena_experiment.alias}_{timestamp}"
    print(f"  Experiment Alias: {ena_experiment.alias}")
    
    try:
        experiment_receipt = workflow.submit_experiment(
            ena_experiment, 
            action="ADD")
        if experiment_receipt.success:
            experiment_accession = experiment_receipt.get_accession("EXPERIMENT")
            print(f"  Accession: {experiment_accession}")
        else:
            print(f"✗ Experiment submission failed:")
            for msg in experiment_receipt.messages:
                print(f"    {msg.type}: {msg.text}")
            return
    except Exception as e:
        print(f"✗ Exception during experiment submission: {e}")
        return
    
    # 5d. Create Run and prepare for submission
    print("\n[4/4] Creating Run and preparing for submission...")
    print(f"  Using Experiment Accession: {experiment_accession}")
    
    # Now create Run
    ena_run = metadata_to_ena_run(
        metadata=metadata_dto,
        experiment_accession=experiment_accession,
        filetype="fastq",
        include_unmapped=True
    )
    ena_run.alias = f"{ena_run.alias}_{timestamp}"
    print(f"  Run Alias: {ena_run.alias}")
    
    print("\n⚠ NOTE: In a real workflow, you would:")
    print("  1. Upload actual FASTQ files to ENA FTP using workflow.upload_reads()")
    print("  2. Update run with actual file checksums")
    print("  3. Submit run with reference to uploaded files")
    print()
    print("Example - Upload specific files:")
    print("  result = workflow.upload_reads([")
    print("      Path('SW_ATL_001_R1.fastq.gz'),")
    print("      Path('SW_ATL_001_R2.fastq.gz')")
    print("  ])")
    print()
    print("Example - Upload all files from directory:")
    print("  result = workflow.upload_reads(")
    print("      file_paths=Path('./sequencing_data'),")
    print("      file_pattern='*.fastq.gz'")
    print("  )")
    print()
    
    # Note: In production, only submit run after uploading files
    print("✓ Run prepared with real accessions (file upload and submission skipped in demo)")
    print()
    
    # ========================================================================
    # STEP 6: Summary
    # ========================================================================
    print("=" * 80)
    print("SUBMISSION SUMMARY")
    print("=" * 80)
    print(f"Project Accession:    {project_accession}")
    print(f"Sample Accession:     {sample_accession}")
    print(f"Experiment Accession: {experiment_accession}")
    print(f"Run Status:           Prepared (not submitted in demo)")
    print()
    print("Next steps:")
    print("1. Upload sequence files to ENA FTP")
    print("2. Submit RUN with file references")
    print("3. Monitor submission status in Webin Portal")
    print("=" * 80)


def workflow_with_batch_samples():
    """
    Example showing batch processing of multiple samples.
    """
    print("\n" + "=" * 80)
    print("BATCH PROCESSING EXAMPLE")
    print("=" * 80)
    
    from dinapy.ena.mappers.dina_to_ena.mappers_dto import batch_material_samples_to_ena
    
    # Simulate multiple samples from DINA
    sample_responses = [
        {
            "data": {
                "id": f"sample-{i}",
                "type": "material-sample",
                "attributes": {
                    "materialSampleName": f"SeaWater_ATL_{i:03d}",
                    "barcode": f"SW-ATL-{i:03d}",
                    "group": "marine-lab",
                    "effectiveScientificName": "marine metagenome",
                    "allowDuplicateName": False,
                    "isRestricted": False
                }
            }
        }
        for i in range(1, 6)  # 5 samples
    ]
    
    # Deserialize
    sample_dtos = [MaterialSampleSchema().load(resp) for resp in sample_responses]
    print(f"Deserialized {len(sample_dtos)} samples")
    
    # Batch map to ENA
    taxon_ids = {f"sample-{i}": 408172 for i in range(1, 6)}
    
    ena_samples = batch_material_samples_to_ena(
        material_samples=sample_dtos,
        taxon_ids=taxon_ids,
        email="researcher@example.com",
        auto_resolve_taxa=False
    )
    
    print(f"✓ Batch mapped {len(ena_samples)} samples to ENA format")
    for sample in ena_samples[:3]:  # Show first 3
        print(f"  - {sample.alias}: {sample.title}")
    print(f"  ... and {len(ena_samples) - 3} more")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  COMPLETE DINA → ENA SUBMISSION WORKFLOW".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Run complete workflow
    complete_submission_workflow()
    
    # Show batch processing example
    workflow_with_batch_samples()
    
    print("\n")
    print("=" * 80)
    print("DOCUMENTATION COMPLETE")
    print("=" * 80)
    print()
    print("Key Takeaways:")
    print("  1. DINA DTOs map to ENA entities with clear relationships")
    print("  2. Experiment requires user-provided sequencing parameters")
    print("  3. Submission order: Project → Sample → Experiment → Run")
    print("  4. Use ENASubmissionWorkflow for simplified submission")
    print("  5. Upload files before submitting RUN")
    print()
