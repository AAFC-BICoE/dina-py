"""
Interactive Solara GUI for DINA to ENA submission workflow.

This module provides a user-friendly graphical interface for submitting
material samples from DINA collections to the European Nucleotide Archive (ENA).

The workflow consists of 6 steps:
1. Configuration - Set up credentials and entity IDs
2. Fetch & Map - Retrieve data from DINA and map to ENA models
3. Sequencing Config - Configure experiment parameters
4. Upload Files - Upload sequence files to ENA FTP
5. Submit - Submit metadata to ENA
6. Results - View accessions and submission receipts

Usage:
    >>> from dinapy.ena.workflow_gui import ENAWorkflowGUI
    >>> ENAWorkflowGUI()  # Launch the interactive GUI
"""

import time
from datetime import date
from pathlib import Path
from typing import List, Optional

import solara
import reacton.ipywidgets as w

from dinapy.apis.collectionapi.materialsampleapi import MaterialSampleAPI
from dinapy.apis.collectionapi.ena_helpers import prepare_sample_for_ena_mapping
from dinapy.ena.submission import ENASubmissionWorkflow
from dinapy.ena.models import Project, Experiment, Design, LibraryDescriptor, LibraryLayout, Platform, ObjectRef


@solara.component
def ENAWorkflowGUI():
    """Interactive GUI for DINA to ENA submission workflow"""

    solara.lab.ThemeToggle()

    # State management
    current_step = solara.use_reactive(1)
    
    # Configuration state
    webin_username = solara.use_reactive("")
    webin_password = solara.use_reactive("")
    use_test_server = solara.use_reactive(True)
    
    # DINA entity IDs
    collection_id = solara.use_reactive("")
    
    # Sequencing configuration
    library_strategy = solara.use_reactive("AMPLICON")
    library_source = solara.use_reactive("METAGENOMIC")
    library_selection = solara.use_reactive("PCR")
    library_layout = solara.use_reactive("PAIRED")
    instrument_model = solara.use_reactive("Illumina NovaSeq 6000")
    design_description = solara.use_reactive("")
    nominal_length = solara.use_reactive(300)
    nominal_sdev = solara.use_reactive(50.0)
    
    # Submission options
    skip_run_submission = solara.use_reactive(False)
    hold_date = solara.use_reactive(date.today().isoformat())
    
    # Submission results
    status_messages = solara.use_reactive([])
    project_accession = solara.use_reactive("")
    sample_accession = solara.use_reactive("")
    experiment_accession = solara.use_reactive("")
    run_accession = solara.use_reactive("")
    run_status = solara.use_reactive("")
    
    # Submission receipts (for detailed info)
    project_receipt = solara.use_reactive(None)
    sample_receipt = solara.use_reactive(None)
    experiment_receipt = solara.use_reactive(None)
    run_receipt = solara.use_reactive(None)
    
    # Fetched data storage - STORE BOTH samples AND included data
    fetched_samples = solara.use_reactive([])
    fetched_included = solara.use_reactive([])
    collection_name = solara.use_reactive("")
    
    # File upload state
    upload_directory = solara.use_reactive("")
    file_pattern = solara.use_reactive("*.fastq.gz")
    use_preupload = solara.use_reactive(False)
    manifest_path = solara.use_reactive("")
    uploaded_files = solara.use_reactive([])
    
    # Processing state
    is_processing = solara.use_reactive(False)
    
    def add_status(message: str, msg_type: str = "info"):
        """Add a status message with type (info, success, warning, error)"""
        timestamp = time.strftime("%H:%M:%S")
        status_messages.value = status_messages.value + [(timestamp, msg_type, message)]
    
    def display_receipt_details(receipt, title: str):
        """Display detailed receipt information"""
        from dinapy.ena.receipt import format_receipt_summary
        
        if not receipt:
            return
        
        with solara.Card(title):
            if receipt.success:
                solara.Success(f"✓ {title} - SUCCESS")
            else:
                solara.Error(f"✗ {title} - FAILURE")
            
            # Show accessions
            if receipt.objects:
                solara.Markdown("**Accessions:**")
                for obj in receipt.objects:
                    if obj.accession:
                        solara.Markdown(f"- {obj.object_type}: `{obj.accession}` (status: {obj.status or 'N/A'})")
            
            # Show errors
            errors = receipt.get_errors()
            if errors:
                solara.Markdown("**Errors:**")
                for err in errors:
                    solara.Error(err)
            
            # Show warnings
            warnings = receipt.get_warnings()
            if warnings:
                solara.Markdown("**Warnings:**")
                for warn in warnings:
                    solara.Warning(warn)
            
            # Show info messages
            infos = receipt.get_info()
            if infos:
                solara.Markdown("**Info:**")
                for info in infos:
                    solara.Info(info)
            
            # Show full formatted summary in expandable section
            with solara.Details("View Full Receipt"):
                summary = format_receipt_summary(receipt)
                solara.Markdown(f"```\n{summary}\n```")
    
    def fetch_and_map_data():
        """Step 2: Fetch DINA data from collection and map to ENA models"""
        is_processing.value = True
        status_messages.value = []
        
        try:
            add_status("Initializing Material Sample API...", "info")
            material_sample_api = MaterialSampleAPI()
            
            add_status(f"Fetching material samples from collection: {collection_id.value}", "info")
            
            # Fetch all material samples in the collection with related entities
            response = material_sample_api.get_by_collection(
                collection_uuid=collection_id.value,
                include=['collectingEvent', 'organism', 'attachment', 'collection', 'preparationType']
            )
            
            # Extract the data
            samples_data = response.json().get('data', [])
            included_data = response.json().get('included', [])
            
            # Store BOTH the fetched data AND included entities
            fetched_samples.value = samples_data
            fetched_included.value = included_data
            
            # Extract collection name from included data
            for item in included_data:
                if item.get('type') == 'collection':
                    collection_name.value = item.get('attributes', {}).get('name', 'Unknown Collection')
                    break
            
            add_status(f"✓ Fetched {len(samples_data)} material samples", "success")
            add_status(f"✓ Collection: {collection_name.value}", "success")
            add_status(f"✓ Fetched {len(included_data)} related entities", "success")
            
            # Count related entities by type
            entity_counts = {}
            for item in included_data:
                entity_type = item.get('type', 'unknown')
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            
            for entity_type, count in entity_counts.items():
                add_status(f"  - {entity_type}: {count}", "info")
            
            if len(samples_data) == 0:
                add_status("⚠ No material samples found in this collection", "warning")
            else:
                add_status("Ready to configure sequencing parameters", "success")
            
            current_step.value = 3
            
        except Exception as e:
            add_status(f"Error: {str(e)}", "error")
        finally:
            is_processing.value = False
    
    def upload_files():
        """Step 4: Upload sequencing files to ENA FTP"""
        is_processing.value = True
        status_messages.value = []
        
        try:
            if use_preupload.value:
                # Using pre-uploaded files
                add_status("Using pre-uploaded files with manifest", "info")
                
                if not manifest_path.value or not Path(manifest_path.value).exists():
                    add_status("Please provide a valid manifest file path", "error")
                    is_processing.value = False
                    return
                
                # Read manifest file
                import csv
                manifest_data = []
                with open(manifest_path.value, 'r') as f:
                    reader = csv.DictReader(f, delimiter='\t')
                    for row in reader:
                        manifest_data.append({
                            'filename': row['filename'],
                            'md5': row['checksum']
                        })
                
                uploaded_files.value = manifest_data
                add_status(f"✓ Loaded manifest with {len(manifest_data)} files", "success")
                for file_info in manifest_data:
                    add_status(f"  - {file_info['filename']}: MD5={file_info['md5'][:16]}...", "info")
                
            else:
                # Upload new files
                add_status("Initializing ENA FTP upload...", "info")
                
                if not upload_directory.value:
                    add_status("Please provide a directory path", "error")
                    is_processing.value = False
                    return
                
                dir_path = Path(upload_directory.value)
                if not dir_path.exists():
                    add_status(f"Directory not found: {upload_directory.value}", "error")
                    is_processing.value = False
                    return
                
                # Find matching files
                matching_files = list(dir_path.glob(file_pattern.value))
                
                if not matching_files:
                    add_status(f"No files matching pattern '{file_pattern.value}' found", "warning")
                    is_processing.value = False
                    return
                
                add_status(f"Found {len(matching_files)} files to upload", "info")
                
                # Initialize ENA workflow for upload
                try:
                    workflow = ENASubmissionWorkflow(
                        username=webin_username.value,
                        password=webin_password.value,
                        test=use_test_server.value
                    )
                    
                    # Upload files
                    add_status("Uploading files to ENA FTP...", "info")
                    upload_result = workflow.upload_reads(matching_files)
                    
                    # Process upload result
                    uploaded_files.value = [
                        {'filename': f.name, 'md5': upload_result.get(f.name, 'unknown')} 
                        for f in matching_files
                    ]
                    add_status(f"✓ Uploaded {len(matching_files)} files successfully", "success")
                    
                except Exception as upload_error:
                    add_status(f"Upload error: {str(upload_error)}", "error")
                    is_processing.value = False
                    return
            
            current_step.value = 5
            
        except Exception as e:
            add_status(f"Error during upload: {str(e)}", "error")
        finally:
            is_processing.value = False
    
    def submit_to_ena():
        """Step 5: Submit to ENA with real API calls"""
        is_processing.value = True
        status_messages.value = []
        
        try:
            add_status("Starting ENA submission...", "info")
            
            # Initialize ENA workflow
            workflow = ENASubmissionWorkflow(
                username=webin_username.value,
                password=webin_password.value,
                test=use_test_server.value
            )
            
            # Get all samples for submission
            if not fetched_samples.value:
                add_status("No samples to submit. Please fetch data first.", "error")
                is_processing.value = False
                return
            
            included_data = fetched_included.value
            all_samples = fetched_samples.value
            
            # Diagnostic: Check if we have data
            add_status(f"Working with {len(all_samples)} samples and {len(included_data)} included entities", "info")
            
            timestamp = str(int(time.time()))
            
            # Storage for all accessions
            all_sample_accessions = []
            all_experiment_accessions = []
            
            # Track failures for summary
            failed_samples = []
            failed_experiments = []
            
            # [1/3] Submit Project (once for the collection)
            add_status("[1/3] Preparing and submitting Project...", "info")
            try:
                add_status("Creating ENA Project from collection data...", "info")
                
                project_alias = f"collection_{collection_id.value}_{timestamp}"
                project_title = collection_name.value or "DINA Collection Metagenomics Study"
                project_description = f"Metagenomic study from DINA collection {collection_id.value} with {len(fetched_samples.value)} samples"
                
                ena_project = Project(
                    alias=project_alias,
                    title=project_title,
                    description=project_description
                )
                
                add_status(f"Submitting project: {project_title}", "info")
                receipt = workflow.submit_project_xml(ena_project, action="ADD", hold_until_date=hold_date.value)
                project_receipt.value = receipt
                
                if receipt.success:
                    project_accession.value = receipt.get_accession("PROJECT") or receipt.get_accession("STUDY")
                    add_status(f"✓ Project submitted: {project_accession.value}", "success")
                    
                    # Show warnings if any
                    for warning in receipt.get_warnings():
                        add_status(f"Project warning: {warning}", "warning")
                else:
                    for error in receipt.get_errors():
                        add_status(f"Project error: {error}", "error")
                    raise Exception("Project submission failed")
                
            except Exception as e:
                add_status(f"Project submission error: {str(e)}", "error")
                raise
            
            # [2/N] Submit ALL Samples (and optionally Experiments)
            if skip_run_submission.value:
                add_status(f"[2/2] Preparing and submitting {len(all_samples)} Samples...", "info")
                add_status("ℹ Skipping Experiment and Run submissions as requested", "info")
            else:
                add_status(f"[2/3] Preparing and submitting {len(all_samples)} Samples and Experiments...", "info")
            
            for idx, sample_data in enumerate(all_samples, 1):
                try:
                    sample_name = sample_data.get('attributes', {}).get('materialSampleName', f'Sample_{idx}')
                    add_status(f"\n--- Processing sample {idx}/{len(all_samples)}: {sample_name} ---", "info")
                    
                    # Prepare sample for ENA using the helper function
                    ms_dto, ce_dto, org_data = prepare_sample_for_ena_mapping(sample_data, included_data)
                    
                    # Diagnostic information - check date and geographic fields (first sample only)
                    if idx == 1:
                        if ce_dto:
                            add_status(f"✓ Found collecting event", "success")
                            
                            # Check date-related fields
                            ce_attrs = ce_dto.attributes
                            date_fields = ['startEventDateTime', 'endEventDateTime', 'dwcEventDate', 'verbatimEventDateTime']
                            found_date = False
                            for field in date_fields:
                                if hasattr(ce_attrs, field):
                                    value = getattr(ce_attrs, field, None)
                                    if value is not None:
                                        add_status(f"  {field}: {value}", "info")
                                        if value != 'undefined' and value != '':
                                            found_date = True
                            
                            if not found_date:
                                add_status(f"  ℹ No valid date fields in source data - mapper will use fallback", "warning")
                            
                            # Check geographic fields
                            geo_fields = ['dwcCountry', 'dwcStateProvince', 'dwcVerbatimLatitude', 'dwcVerbatimLongitude']
                            found_geo = False
                            for field in geo_fields:
                                if hasattr(ce_attrs, field):
                                    value = getattr(ce_attrs, field, None)
                                    if value and value != 'undefined' and value != '':
                                        add_status(f"  {field}: {value}", "info")
                                        found_geo = True
                            
                            if not found_geo:
                                add_status(f"  ℹ No geographic fields in source data - mapper will use fallback", "warning")
                        else:
                            add_status("ℹ No collecting event - mapper will provide fallback values", "warning")
                    
                    # Reload mapper module to get latest code changes
                    import importlib
                    from dinapy.ena.mappers.dina_to_ena import mappers_dto
                    importlib.reload(mappers_dto)
                    from dinapy.ena.mappers.dina_to_ena.mappers_dto import material_sample_to_ena
                    
                    # Map to ENA
                    ena_sample = material_sample_to_ena(
                        material_sample=ms_dto,
                        collecting_event=ce_dto,
                        organism_data=org_data,
                        email="your.email@example.com",
                        include_unmapped=True
                    )
                    ena_sample.alias = f"{ena_sample.alias}_{timestamp}"
                    
                    # Submit sample
                    add_status(f"Submitting sample {idx}...", "info")
                    receipt = workflow.submit_sample_xml(ena_sample, action="ADD", hold_until_date=hold_date.value)
                    
                    if receipt.success:
                        current_sample_accession = receipt.get_accession("SAMPLE")
                        all_sample_accessions.append(current_sample_accession)
                        add_status(f"✓ Sample {idx} submitted: {current_sample_accession}", "success")
                        
                        # Store first sample accession for display
                        if idx == 1:
                            sample_accession.value = current_sample_accession
                            sample_receipt.value = receipt
                        
                        # Submit Experiment for this sample (only if not skipping sequencing data)
                        if not skip_run_submission.value:
                            add_status(f"Creating experiment for sample {idx}...", "info")
                            
                            experiment_alias = f"exp_{current_sample_accession}_{timestamp}"
                            experiment_title = f"Sequencing experiment for {sample_name}"
                            
                            # Build library descriptor
                            library_desc = LibraryDescriptor(
                                library_strategy=library_strategy.value,
                                library_source=library_source.value,
                                library_selection=library_selection.value,
                                library_layout=LibraryLayout(
                                    layout_type=library_layout.value,
                                    nominal_length=nominal_length.value if library_layout.value == "PAIRED" else None,
                                    nominal_sdev=nominal_sdev.value if library_layout.value == "PAIRED" else None
                                )
                            )
                            
                            # Build design
                            design = Design(
                                design_description=design_description.value or f"{library_strategy.value} sequencing",
                                sample_descriptor=ObjectRef(accession=current_sample_accession),
                                library_descriptor=library_desc
                            )
                            
                            # Build platform
                            platform = Platform(
                                instrument_model=instrument_model.value
                            )
                            
                            # Create experiment
                            ena_experiment = Experiment(
                                alias=experiment_alias,
                                title=experiment_title,
                                study_ref=ObjectRef(accession=project_accession.value),
                                design=design,
                                platform=platform
                            )
                            
                            add_status(f"Submitting experiment {idx}...", "info")
                            receipt = workflow.submit_experiment(ena_experiment, action="ADD")
                            
                            if receipt.success:
                                current_experiment_accession = receipt.get_accession("EXPERIMENT")
                                all_experiment_accessions.append(current_experiment_accession)
                                add_status(f"✓ Experiment {idx} submitted: {current_experiment_accession}", "success")
                                
                                # Store first experiment accession for display
                                if idx == 1:
                                    experiment_accession.value = current_experiment_accession
                                    experiment_receipt.value = receipt
                            else:
                                error_msgs = receipt.get_errors()
                                for error in error_msgs:
                                    add_status(f"Experiment {idx} error: {error}", "error")
                                failed_experiments.append((idx, sample_name, '; '.join(error_msgs)))
                    else:
                        error_msgs = receipt.get_errors()
                        for error in error_msgs:
                            add_status(f"Sample {idx} error: {error}", "error")
                        failed_samples.append((idx, sample_name, '; '.join(error_msgs)))
                    
                except Exception as e:
                    import traceback
                    add_status(f"✗ Error processing sample {idx} ({sample_name}):", "error")
                    add_status(f"  Error type: {type(e).__name__}", "error")
                    add_status(f"  Error message: {str(e)}", "error")
                    # Show first few lines of traceback for context
                    tb_lines = traceback.format_exc().split('\n')
                    for line in tb_lines[-5:-1]:
                        if line.strip():
                            add_status(f"  {line}", "error")
                    failed_samples.append((idx, sample_name, f"{type(e).__name__}: {str(e)}"))
            
            # After processing all samples, show summary
            if skip_run_submission.value:
                add_status(f"\n✓ Completed: {len(all_sample_accessions)} samples submitted", "success")
                add_status(f"ℹ Experiments and Runs skipped. Use Project accession ({project_accession.value}) and Sample accessions to submit sequencing data later.", "info")
            else:
                add_status(f"\n✓ Completed: {len(all_sample_accessions)} samples, {len(all_experiment_accessions)} experiments", "success")
            
            # Show failure summary if any
            if failed_samples or failed_experiments:
                add_status(f"\n⚠ FAILURE SUMMARY:", "warning")
                
                if failed_samples:
                    add_status(f"\nFailed Samples: {len(failed_samples)}/{len(all_samples)}", "error")
                    for idx, name, error in failed_samples[:10]:
                        add_status(f"  [{idx}] {name}: {error[:80]}...", "error")
                    if len(failed_samples) > 10:
                        add_status(f"  ...and {len(failed_samples) - 10} more", "error")
                
                if failed_experiments:
                    add_status(f"\nFailed Experiments: {len(failed_experiments)}", "error")
                    for idx, name, error in failed_experiments[:10]:
                        add_status(f"  [{idx}] {name}: {error[:80]}...", "error")
                    if len(failed_experiments) > 10:
                        add_status(f"  ...and {len(failed_experiments) - 10} more", "error")
            
            # [3/3] Run submission (currently not implemented)
            if skip_run_submission.value:
                add_status("[3/3] Run submission skipped (as requested)", "info")
                run_status.value = "Skipped by user"
            else:
                add_status("[3/3] Run submission requires metadata entity", "info")
                add_status(f"ℹ Would submit with {len(uploaded_files.value)} uploaded files", "info")
                run_status.value = f"Would submit with {len(uploaded_files.value)} files"
            
            add_status("✓ Submission workflow completed", "success")
            current_step.value = 6
            
        except Exception as e:
            add_status(f"Fatal error during submission: {str(e)}", "error")
        finally:
            is_processing.value = False
    
    # Main UI Layout
    with solara.Card(title="ENA Submission Workflow", elevation=2):
        # Progress indicator
        solara.Markdown(f"### Step {current_step.value} of 6")
        solara.ProgressLinear(value=(current_step.value / 6) * 100)
        
        # Step indicators
        with solara.Row():
            for i, step_name in enumerate(["Config", "Fetch", "Sequencing", "Seq. Data", "Submit", "Results"], 1):
                color = "primary" if i == current_step.value else ("success" if i < current_step.value else "default")
                solara.Button(
                    f"{i}. {step_name}",
                    color=color,
                    disabled=True,
                    style={"margin": "5px"}
                )
        
        solara.HTML(tag="hr")
        
        # Step 1: Configuration
        if current_step.value == 1:
            solara.Markdown("## Step 1: Configuration")
            solara.Markdown("Configure your ENA credentials and DINA entity identifiers.")
            
            with solara.Card("WEBIN Credentials"):
                solara.InputText(label="WEBIN Username", value=webin_username)
                solara.InputText(label="WEBIN Password", value=webin_password, password=True)
                solara.Checkbox(label="Use Test Server (recommended for testing)", value=use_test_server)
            
            with solara.Card("DINA Entity IDs"):
                solara.InputText(label="Collection ID", value=collection_id, continuous_update=False)
            
            with solara.Row():
                solara.Button(
                    "Next: Fetch & Map Data →",
                    on_click=lambda: setattr(current_step, 'value', 2),
                    color="primary",
                    disabled=not all([collection_id.value])
                )
        
        # Step 2: Fetch & Map
        elif current_step.value == 2:
            solara.Markdown("## Step 2: Fetch & Map Data")
            solara.Markdown("Retrieve material samples from DINA collection with related entities.")
            
            solara.Info(f"This will fetch all material samples from collection UUID: **{collection_id.value}**")
            
            # Show fetched data summary if available
            if len(fetched_samples.value) > 0:
                with solara.Card("Fetched Data Summary", elevation=1):
                    solara.Success(f"**Collection:** {collection_name.value}")
                    solara.Success(f"**Material Samples:** {len(fetched_samples.value)}")
                    
                    # Show first few sample names
                    solara.Markdown("**Sample Names (first 5):**")
                    for i, sample in enumerate(fetched_samples.value[:5]):
                        sample_name = sample.get('attributes', {}).get('materialSampleName', 'Unknown')
                        sample_id = sample.get('id', 'No ID')[:8]
                        solara.Markdown(f"- {sample_name} (ID: {sample_id}...)")
                    
                    if len(fetched_samples.value) > 5:
                        solara.Markdown(f"*...and {len(fetched_samples.value) - 5} more samples*")
            
            if status_messages.value:
                with solara.Card("Fetch Status"):
                    for timestamp, msg_type, msg in status_messages.value:
                        color = {
                            "info": "blue",
                            "success": "green",
                            "warning": "orange",
                            "error": "red"
                        }.get(msg_type, "grey")
                        solara.Markdown(f"<span style='color:{color}'>[{timestamp}] {msg}</span>")
            
            with solara.Row():
                solara.Button("← Back", on_click=lambda: setattr(current_step, 'value', 1))
                solara.Button(
                    "Fetch Data",
                    on_click=fetch_and_map_data,
                    color="primary",
                    disabled=is_processing.value
                )
        
        # Step 3: Sequencing Configuration
        elif current_step.value == 3:
            solara.Markdown("## Step 3: Sequencing Configuration")
            solara.Markdown("Configure experiment parameters for ENA submission.")
            
            with solara.Card("Library Information"):
                solara.Select(
                    label="Library Strategy",
                    value=library_strategy,
                    values=["AMPLICON", "WGS", "WGA", "WXS", "RNA-Seq", "ChIP-Seq", "ATAC-seq"]
                )
                solara.Select(
                    label="Library Source",
                    value=library_source,
                    values=["METAGENOMIC", "GENOMIC", "TRANSCRIPTOMIC", "METATRANSCRIPTOMIC", "SYNTHETIC", "VIRAL RNA"]
                )
                solara.Select(
                    label="Library Selection",
                    value=library_selection,
                    values=["PCR", "RANDOM", "RANDOM PCR", "RT-PCR", "HMPR", "MF", "CF-S", "CF-M", "CF-H", "CF-T"]
                )
                solara.Select(
                    label="Library Layout",
                    value=library_layout,
                    values=["PAIRED", "SINGLE"]
                )
            
            with solara.Card("Instrument & Design"):
                solara.Select(
                    label="Instrument Model",
                    value=instrument_model,
                    values=[
                        "Illumina NovaSeq 6000",
                        "Illumina MiSeq",
                        "Illumina HiSeq 2500",
                        "NextSeq 500",
                        "PacBio Sequel",
                        "Oxford Nanopore MinION"
                    ]
                )
                solara.InputText(
                    label="Design Description",
                    value=design_description,
                    continuous_update=False
                )
                solara.InputInt(label="Nominal Length (bp)", value=nominal_length)
                solara.InputFloat(label="Nominal Standard Deviation", value=nominal_sdev)
            
            with solara.Row():
                solara.Button("← Back", on_click=lambda: setattr(current_step, 'value', 2))
                solara.Button(
                    "Next: Upload Files →",
                    on_click=lambda: setattr(current_step, 'value', 4),
                    color="primary"
                )
        
        # Step 4: Upload Files
        elif current_step.value == 4:
            solara.Markdown("## Step 4: Upload Sequencing Files")
            solara.Markdown("Upload sequence files to ENA FTP server or skip RUN submission.")
            
            with solara.Card("RUN Submission Options"):
                solara.Checkbox(
                    label="Skip RUN submission (I'll submit RUN separately later)",
                    value=skip_run_submission
                )
                
                if skip_run_submission.value:
                    solara.Info("RUN submission will be skipped. Only Project, Sample, and Experiment will be submitted.")
            
            # Only show file upload options if NOT skipping RUN submission
            if not skip_run_submission.value:
                solara.Info("Files must be on ENA's FTP server before submitting a RUN.")
                
                with solara.Card("Upload Options"):
                    solara.Checkbox(
                        label="Use pre-uploaded files (I already have files on ENA FTP)",
                        value=use_preupload
                    )
                    
                    if use_preupload.value:
                        solara.Markdown("### Pre-uploaded Files")
                        solara.Markdown("Provide a manifest file (TSV format) with columns: `filename` and `checksum`")
                        solara.InputText(
                            label="Manifest File Path",
                            value=manifest_path,
                            continuous_update=False
                        )
                    else:
                        solara.Markdown("### Upload New Files")
                        solara.InputText(
                            label="Directory Path",
                            value=upload_directory,
                            continuous_update=False
                        )
                        solara.InputText(
                            label="File Pattern (e.g., *.fastq.gz)",
                            value=file_pattern,
                            continuous_update=False
                        )
                
                if len(uploaded_files.value) > 0:
                    with solara.Card("Uploaded Files Summary"):
                        solara.Success(f"**Files Ready:** {len(uploaded_files.value)}")
                        for file_info in uploaded_files.value[:5]:
                            md5_short = file_info['md5'][:16]
                            solara.Markdown(f"- {file_info['filename']} (MD5: {md5_short}...)")
                
                if status_messages.value:
                    with solara.Card("Upload Status"):
                        for timestamp, msg_type, msg in status_messages.value:
                            color = {
                                "info": "blue",
                                "success": "green",
                                "warning": "orange",
                                "error": "red"
                            }.get(msg_type, "grey")
                            solara.Markdown(f"<span style='color:{color}'>[{timestamp}] {msg}</span>")
            
            with solara.Row():
                solara.Button("← Back", on_click=lambda: setattr(current_step, 'value', 3))
                
                if skip_run_submission.value:
                    solara.Button(
                        "Next: Submit →",
                        on_click=lambda: setattr(current_step, 'value', 5),
                        color="primary"
                    )
                else:
                    solara.Button(
                        "Upload Files" if not use_preupload.value else "Load Manifest",
                        on_click=upload_files,
                        color="primary",
                        disabled=is_processing.value
                    )
                    if len(uploaded_files.value) > 0:
                        solara.Button(
                            "Next: Submit →",
                            on_click=lambda: setattr(current_step, 'value', 5),
                            color="success"
                        )
        
        # Step 5: Submit
        elif current_step.value == 5:
            solara.Markdown("## Step 5: Submit to ENA")
            solara.Warning("⚠ This will submit data to ENA. Review all configuration first.")
            
            with solara.Card("Submission Order"):
                if skip_run_submission.value:
                    solara.Markdown("""
1. **Project** - Submit study information with hold date
2. **Sample** - Submit all samples with collecting event data
3. **Experiment** - ⏭️ **Skipped**
4. **Run** - ⏭️ **Skipped**
                    """)
                else:
                    solara.Markdown("""
1. **Project** - Submit study information
2. **Sample** - Submit all samples
3. **Experiment** - Submit experiments for each sample
4. **Run** - Submit run with uploaded files (not yet implemented)
                    """)
            
            with solara.Card("Submission Options"):
                solara.InputText(
                    label="Hold Until Date (YYYY-MM-DD)",
                    value=hold_date,
                    continuous_update=False
                )
            
            if status_messages.value:
                with solara.Card("Submission Progress"):
                    for timestamp, msg_type, msg in status_messages.value:
                        color = {
                            "info": "blue",
                            "success": "green",
                            "warning": "orange",
                            "error": "red"
                        }.get(msg_type, "grey")
                        solara.Markdown(f"<span style='color:{color}'>[{timestamp}] {msg}</span>")
            
            with solara.Row():
                solara.Button("← Back", on_click=lambda: setattr(current_step, 'value', 4))
                solara.Button(
                    "Submit to ENA",
                    on_click=submit_to_ena,
                    color="primary",
                    disabled=is_processing.value or not webin_username.value
                )
        
        # Step 6: Results
        elif current_step.value == 6:
            solara.Markdown("## Step 6: Submission Results")
            
            with solara.Card("Accession Numbers"):
                if project_accession.value:
                    solara.Success(f"**Project:** {project_accession.value}")
                if sample_accession.value:
                    solara.Success(f"**Sample:** {sample_accession.value}")
                if experiment_accession.value:
                    solara.Success(f"**Experiment:** {experiment_accession.value}")
                if run_accession.value:
                    solara.Success(f"**Run:** {run_accession.value}")
                if run_status.value:
                    solara.Info(f"**Run Status:** {run_status.value}")
            
            # Display detailed receipts
            if project_receipt.value:
                display_receipt_details(project_receipt.value, "Project Submission Receipt")
            
            if sample_receipt.value:
                display_receipt_details(sample_receipt.value, "Sample Submission Receipt")
            
            if experiment_receipt.value:
                display_receipt_details(experiment_receipt.value, "Experiment Submission Receipt")
            
            if run_receipt.value:
                display_receipt_details(run_receipt.value, "Run Submission Receipt")
            
            # Show submission log
            if status_messages.value:
                with solara.Card("Submission Log"):
                    for timestamp, msg_type, msg in status_messages.value:
                        color = {
                            "info": "blue",
                            "success": "green",
                            "warning": "orange",
                            "error": "red"
                        }.get(msg_type, "grey")
                        solara.Markdown(f"<span style='color:{color}'>[{timestamp}] {msg}</span>")
            
            def reset_workflow():
                current_step.value = 1
                status_messages.value = []
                project_accession.value = ""
                sample_accession.value = ""
                experiment_accession.value = ""
                run_accession.value = ""
                run_status.value = ""
                project_receipt.value = None
                sample_receipt.value = None
                experiment_receipt.value = None
                run_receipt.value = None
            
            with solara.Row():
                solara.Button(
                    "← Start New Submission",
                    on_click=reset_workflow
                )
