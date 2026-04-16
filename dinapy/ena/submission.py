"""
ENA Submission Workflow Orchestrator

High-level convenience class for coordinating the full ENA submission workflow:
1. Create Pydantic models
2. Generate XML
3. Upload sequence files via FTP
4. Submit metadata via WebinAPI
5. Parse and return receipts

This simplifies the submission process by handling all the boilerplate.
"""
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import logging
import os
import time
from dotenv import load_dotenv

from dinapy.apis.webin_api.webin_api import WebinAPI
from dinapy.ena.models import (
    Project, Sample, Experiment, Run,
    Submission, Action, Attribute, ActionType
)
from dinapy.ena.mappers.xml_builder.submission import build_submission_xml_from_model
from dinapy.ena.mappers.xml_builder.project import build_project_xml_from_model
from dinapy.ena.mappers.xml_builder.sample import build_sample_xml_from_model, build_samples_xml_from_models
from dinapy.ena.mappers.xml_builder.experiment import build_experiment_xml_from_model
from dinapy.ena.mappers.xml_builder.run import build_run_xml_from_model
from dinapy.ena.receipt import ENAReceipt, ENAObject, ENAMessage
from dinapy.ena.upload import ReadUploader

logger = logging.getLogger(__name__)


class ENASubmissionWorkflow:
    """
    High-level orchestrator for ENA submissions.
    
    Handles the complete workflow from models to submission receipts.
    
    Submission Action Types:
    -----------------------
    - ADD: Submit new objects (default, use for initial submissions)
    - MODIFY: Update existing objects (requires accession)
    - VALIDATE: Validate XML without submitting to database
    - HOLD: Set or update hold date for data release
    - RELEASE: Release held data immediately (requires existing accession)
    - CANCEL: Cancel a previous submission
    
    IMPORTANT: RELEASE, MODIFY, and HOLD actions require objects to already
    exist in ENA with accessions. For new submissions, always use ADD (default).
    
    To release held data:
    1. First submit with ADD (object gets accession)
    2. Later submit a new submission XML referencing the accession with RELEASE action
    3. Cannot use RELEASE in the same submission as ADD
    
    Example:
        >>> workflow = ENASubmissionWorkflow(
        ...     username="Webin-12345",
        ...     password="secret",
        ...     test=True
        ... )
        >>> 
        >>> # Submit a project
        >>> project = Project(
        ...     alias="my_project_001",
        ...     title="My Research Project",
        ...     description="Study of microbial diversity"
        ... )
        >>> receipt = workflow.submit_project(project)
        >>> print(f"Project accession: {receipt.get_accession('PROJECT')}")
    """
    
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        test: bool = True,
        webin_api: Optional[WebinAPI] = None
    ):
        """
        Initialize the submission workflow.
        
        Args:
            username: ENA Webin username (or use WEBIN_USERNAME env var)
            password: ENA Webin password (or use WEBIN_PASSWORD env var)
            test: Use test server (wwwdev) if True, production if False
            webin_api: Pre-configured WebinAPI instance (optional)
        """
        # Load .env file if present (works in notebooks and scripts)
        load_dotenv()
        
        # Get credentials from arguments or environment variables
        username = username or os.getenv("WEBIN_USERNAME")
        password = password or os.getenv("WEBIN_PASSWORD")
        
        self.api = webin_api or WebinAPI(
            username=username,
            password=password,
            test=test
        )
        self.test = test
        self.username = username or self.api.username
        self.password = password or self.api.password
    
    def submit_project(
        self,
        project: Project,
        submission_alias: Optional[str] = None,
        action: Union[ActionType, str] = ActionType.ADD
    ) -> ENAReceipt:
        """
        Submit a project (study) to ENA via JSON API.
        
        Args:
            project: Project Pydantic model
            submission_alias: Unique submission alias (auto-generated if None)
            action: Submission action (default: ADD for new submissions)
                - ADD: Submit new objects (use for initial submission)
                - MODIFY: Update existing objects (requires accession)
                - VALIDATE: Validate XML without submitting
                
                WARNING: For initial submissions, always use ADD (default).
                RELEASE, HOLD actions may not work correctly via JSON API.
            
        Returns:
            Parsed ENAReceipt object
        """
        submission_alias = submission_alias or f"sub_{project.alias}"
        
        # Convert ActionType enum to string if needed
        action_str = action.value if isinstance(action, ActionType) else action
        
        # Warn about common mistakes
        if action_str in ['RELEASE', 'MODIFY', 'HOLD']:
            logger.warning(
                f"Action '{action_str}' requires existing accessions and may not work via JSON API. "
                f"For NEW submissions, use action=ActionType.ADD (default). "
                f"For RELEASE/MODIFY, consider using submit_project_xml() instead."
            )
        
        # Serialize project and clean up empty nested objects
        project_data = project.model_dump(by_alias=True, exclude_none=True)
        
        # Remove empty lists from top level
        project_data = {k: v for k, v in project_data.items() 
                       if not (isinstance(v, list) and len(v) == 0)}
        
        # Clean up nested sequencingProject if it only has empty lists
        if 'sequencingProject' in project_data:
            seq_proj = project_data['sequencingProject']
            if isinstance(seq_proj, dict):
                # Remove empty lists from sequencingProject
                seq_proj_cleaned = {k: v for k, v in seq_proj.items() 
                                   if not (isinstance(v, list) and len(v) == 0)}
                if not seq_proj_cleaned:
                    # If empty after cleaning, keep as empty object (ENA expects this)
                    project_data['sequencingProject'] = {}
                else:
                    project_data['sequencingProject'] = seq_proj_cleaned
        
        # Use Webin v2 JSON API for projects
        payload = {
            "submission": {
                "alias": submission_alias,
                "actions": [{"type": action_str}]
            },
            "projects": [project_data]
        }
        
        logger.info(f"Submitting project '{project.alias}' via JSON API")
        resp = self.api.post_json("/submit", payload=payload)
        
        # Webin v2 JSON endpoint returns JSON, not XML receipt
        # Parse accordingly
        if resp.headers.get("content-type", "").startswith("application/json"):
            logger.warning("JSON response received; returning custom receipt")
            return self._parse_json_response(resp, "PROJECT")
        
        return self.api.parse_receipt(resp)
    
    def submit_sample(
        self,
        sample: Sample,
        submission_alias: Optional[str] = None,
        action: Union[ActionType, str] = ActionType.ADD
    ) -> ENAReceipt:
        """
        Submit a sample to ENA via JSON API.
        
        Args:
            sample: Sample Pydantic model
            submission_alias: Unique submission alias (auto-generated if None)
            action: Submission action (default: ADD for new submissions)
                - ADD: Submit new objects (use for initial submission)
                - MODIFY: Update existing objects (requires accession)
                - VALIDATE: Validate XML without submitting
                
                WARNING: For initial submissions, always use ADD (default).
                RELEASE, HOLD actions may not work correctly via JSON API.
            
        Returns:
            Parsed ENAReceipt object
        """
        submission_alias = submission_alias or f"sub_{sample.alias}"
        
        # Convert ActionType enum to string if needed
        action_str = action.value if isinstance(action, ActionType) else action
        
        # Warn about common mistakes
        if action_str in ['RELEASE', 'MODIFY', 'HOLD']:
            logger.warning(
                f"Action '{action_str}' requires existing accessions and may not work via JSON API. "
                f"For NEW submissions, use action=ActionType.ADD (default). "
                f"For RELEASE/MODIFY, consider using submit_sample_xml() instead."
            )
        
        # Serialize sample and remove empty lists to avoid API issues
        sample_data = sample.model_dump(by_alias=True, exclude_none=True)
        # Remove empty lists (ENA API may not accept empty sampleLinks, etc.)
        sample_data = {k: v for k, v in sample_data.items() 
                      if not (isinstance(v, list) and len(v) == 0)}
        
        # WORKAROUND: ENA JSON API has a bug with 'description' field
        # It fails XML validation: "Expected element 'SAMPLE_NAME' instead of 'DESCRIPTION'"
        # Remove description until ENA fixes their JSON-to-XML converter
        if 'description' in sample_data:
            logger.warning(f"Removing 'description' field due to ENA API bug - use 'title' instead")
            del sample_data['description']
        
        # Use Webin v2 JSON API for samples
        payload = {
            "submission": {
                "alias": submission_alias,
                "actions": [{"type": action_str}]
            },
            "samples": [sample_data]
        }
        
        logger.info(f"Submitting sample '{sample.alias}' via JSON API")
        resp = self.api.post_json("/submit", payload=payload)
        
        if resp.headers.get("content-type", "").startswith("application/json"):
            logger.warning("JSON response received; returning custom receipt")
            return self._parse_json_response(resp, "SAMPLE")
        return self.api.parse_receipt(resp)
    
    def submit_project_xml(
        self,
        project: Project,
        submission_alias: Optional[str] = None,
        action: Union[ActionType, str] = ActionType.ADD,
        hold_until_date: Optional[str] = None
    ) -> ENAReceipt:
        """
        Submit a project (study) to ENA via Webin v2 XML API.
        
        This method uses XML submission which provides complete XSD coverage
        
        Args:
            project: Project Pydantic model
            submission_alias: Unique submission alias (auto-generated if None)
            action: Submission action (default: ADD for new submissions)
                - ADD: Submit new objects (use for initial submission)
                - MODIFY: Update existing objects (requires accession in studyRef)
                - VALIDATE: Validate XML without submitting
                - HOLD: Set hold date for data release
                - RELEASE: Release held data (requires existing accession, not for initial submission)
                - CANCEL: Cancel previous submission
                
                WARNING: MODIFY, RELEASE, and HOLD require objects to already exist with accessions.
                For initial submissions, always use ADD (default).
            hold_until_date: Optional hold date (ISO format YYYY-MM-DD). If provided with ADD action,
                             creates two actions: ADD + HOLD. Example: "2025-12-31"
            
        Returns:
            Parsed ENAReceipt object
            
        Example:
            # Submit with immediate release
            receipt = workflow.submit_project_xml(project, action=ActionType.ADD)
            
            # Submit with hold date (embargo until publication)
            receipt = workflow.submit_project_xml(project, action=ActionType.ADD,
                                                 hold_until_date="2025-12-31")
        """
        submission_alias = submission_alias or f"sub_{project.alias}"
        
        # Convert ActionType enum to string if needed
        action_str = action.value if isinstance(action, ActionType) else action
        
        # Warn about common mistakes
        if action_str in ['RELEASE', 'MODIFY', 'HOLD']:
            logger.warning(
                f"Action '{action_str}' typically requires existing accessions. "
                f"For NEW submissions, use action=ActionType.ADD (default). "
                f"Use {action_str} only for updating already-submitted objects."
            )
        
        # Build actions list
        if hold_until_date and action_str.upper() == "ADD":
            # ADD with HOLD date
            actions = [
                {"type": "ADD"},
                {"type": "HOLD", "HoldUntilDate": hold_until_date}
            ]
        else:
            actions = action_str
        
        # Build XML using xml_builder functions
        submission_xml = build_submission_xml_from_model(
            submission_alias=submission_alias,
            action=actions,
            hold_until_date=hold_until_date if action_str.upper() == "HOLD" else None
        )
        project_xml = build_project_xml_from_model(project)
        
        logger.info(f"Submitting project '{project.alias}' via Webin v2 XML API")
        resp = self.api.submit_webin_xml(
            submission_xml=submission_xml,
            project_xml=project_xml,
            path="/submit"
        )
        
        return self.api.parse_receipt(resp)
    
    def submit_samples_xml(
        self,
        samples: List[Sample],
        submission_alias: Optional[str] = None,
        action: Union[ActionType, str] = ActionType.ADD,
        hold_until_date: Optional[str] = None
    ) -> ENAReceipt:
        """
        Submit multiple samples to ENA in a single batch via Webin v2 XML API.
        
        This is more efficient than submitting samples individually when you have
        many samples from the same study. All samples are submitted in one SAMPLE_SET.
        
        Args:
            samples: List of Sample Pydantic models
            submission_alias: Unique submission alias (auto-generated if None)
            action: Submission action (default: ADD for new submissions)
                - ADD: Submit new objects (use for initial submission)
                - MODIFY: Update existing objects (requires accessions)
                - VALIDATE: Validate XML without submitting
                - HOLD: Set hold date for data release
                - RELEASE: Release held data (requires existing accessions)
                - CANCEL: Cancel previous submission
                
                WARNING: For initial submissions, always use ADD (default).
            hold_until_date: Optional hold date (ISO format YYYY-MM-DD). If provided with ADD action,
                automatically creates ADD + HOLD action list.
            
        Returns:
            Parsed ENAReceipt object with accessions for all submitted samples
            
        Example:
            >>> samples = [sample1, sample2, sample3]
            >>> receipt = workflow.submit_samples_xml(samples, action=ActionType.ADD)
            >>> for sample in samples:
            ...     accession = receipt.get_accession('SAMPLE', sample.alias)
        """
        from dinapy.ena.mappers.xml_builder.sample import build_samples_xml_from_models
        
        if not samples:
            raise ValueError("samples list cannot be empty")
        
        submission_alias = submission_alias or f"sub_batch_{len(samples)}_samples"
        
        # Convert ActionType enum to string if needed
        action_str = action.value if isinstance(action, ActionType) else action

        # Warn about common mistakes
        if action_str in ['RELEASE', 'MODIFY', 'HOLD']:
            logger.warning(
                f"Action '{action_str}' typically requires existing accessions. "
                f"For NEW submissions, use action=ActionType.ADD (default)."
            )
        
        # Build actions list
        if hold_until_date and action_str.upper() == "ADD":
            # ADD with HOLD date
            actions = [
                {"type": "ADD"},
                {"type": "HOLD", "HoldUntilDate": hold_until_date}
            ]
        else:
            actions = action_str
            
        # Build XML using xml_builder functions
        submission_xml = build_submission_xml_from_model(
            submission_alias=submission_alias,
            action=actions,
            hold_until_date=hold_until_date if action_str.upper() == "HOLD" else None
        )
        
        sample_xml = build_samples_xml_from_models(samples)
        
        sample_aliases = [s.alias for s in samples]
        logger.info(f"Submitting {len(samples)} samples in batch via Webin v2 XML API: {sample_aliases}")
        resp = self.api.submit_webin_xml(
            submission_xml=submission_xml,
            sample_xml=sample_xml,
            path="/submit"
        )
        
        return self.api.parse_receipt(resp)

    def submit_sample_xml(
        self,
        sample: Sample,
        submission_alias: Optional[str] = None,
        action: Union[ActionType, str] = ActionType.ADD,
        hold_until_date: Optional[str] = None
    ) -> ENAReceipt:
        """
        Submit a sample to ENA via Webin v2 XML API.
        
        This method uses XML submission which provides complete XSD coverage
        
        Args:
            sample: Sample Pydantic model
            submission_alias: Unique submission alias (auto-generated if None)
            action: Submission action (default: ADD for new submissions)
                - ADD: Submit new objects (use for initial submission)
                - MODIFY: Update existing objects (requires accession)
                - VALIDATE: Validate XML without submitting
                - HOLD: Set hold date for data release
                - RELEASE: Release held data (requires existing accession)
                - CANCEL: Cancel previous submission
                
                WARNING: For initial submissions, always use ADD (default).
            
        Returns:
            Parsed ENAReceipt object
        """
        submission_alias = submission_alias or f"sub_{sample.alias}"
        
        # Convert ActionType enum to string if needed
        action_str = action.value if isinstance(action, ActionType) else action

        # Warn about common mistakes
        if action_str in ['RELEASE', 'MODIFY', 'HOLD']:
            logger.warning(
                f"Action '{action_str}' typically requires existing accessions. "
                f"For NEW submissions, use action=ActionType.ADD (default)."
            )
        
                # Build actions list
        if hold_until_date and action_str.upper() == "ADD":
            # ADD with HOLD date
            actions = [
                {"type": "ADD"},
                {"type": "HOLD", "HoldUntilDate": hold_until_date}
            ]
        else:
            actions = action_str
            
        # Build XML using xml_builder functions
        submission_xml = build_submission_xml_from_model(
            submission_alias=submission_alias,
            action=actions,
            hold_until_date=hold_until_date if action_str.upper() == "HOLD" else None

        )
        
        sample_xml = build_sample_xml_from_model(sample)
        
        logger.info(f"Submitting sample '{sample.alias}' via Webin v2 XML API")
        resp = self.api.submit_webin_xml(
            submission_xml=submission_xml,
            sample_xml=sample_xml,
            path="/submit"
        )
        
        return self.api.parse_receipt(resp)
    
    def _validate_xml(
        self,
        label: str,
        submission_alias: str,
        **xml_kwargs,
    ) -> None:
        """
        Send XML to ENA with action=VALIDATE and raise ValueError if it fails.

        Args:
            label: Human-readable name for error messages (e.g. "experiment").
            submission_alias: Alias to use for the validation submission.
            **xml_kwargs: Keyword arguments forwarded to ``api.submit_xml``
                          (e.g. ``experiment_xml=...``, ``run_xml=...``).

        Raises:
            ValueError: If ENA reports validation errors.
        """
        val_submission_xml = build_submission_xml_from_model(
            submission_alias=f"{submission_alias}_validate",
            action="VALIDATE",
        )
        logger.info(f"Pre-validating {label} XML with ENA VALIDATE action")
        val_resp = self.api.submit_xml(
            submission_xml=val_submission_xml,
            test=self.test,
            **xml_kwargs,
        )
        val_receipt = self.api.parse_receipt(val_resp)
        if not val_receipt.success:
            errors = val_receipt.get_errors()
            raise ValueError(
                f"ENA validation failed for {label}: "
                + (";".join(errors) if errors else "(no error detail returned)")
            )
        logger.info(f"{label.capitalize()} XML passed ENA pre-validation")

    def submit_experiment(
        self,
        experiment: Experiment,
        submission_alias: Optional[str] = None,
        action: Union[ActionType, str] = ActionType.ADD,
        validate_first: bool = False,
    ) -> ENAReceipt:
        """
        Submit an experiment to ENA via drop-box XML API.
        
        Args:
            experiment: Experiment Pydantic model
            submission_alias: Unique submission alias (auto-generated if None)
            action: Submission action (default: ADD for new submissions)
                - ADD: Submit new objects (use for initial submission)
                - MODIFY: Update existing objects (requires accession)
                - VALIDATE: Validate XML without submitting
                
                WARNING: For initial submissions, always use ADD (default).
            validate_first: If True, send the XML with action=VALIDATE before
                the real submission. Raises ValueError if ENA rejects the XML,
                allowing callers to abort early before any objects are persisted.
            
        Returns:
            Parsed ENAReceipt object
        """
        submission_alias = submission_alias or f"sub_{experiment.alias}"
        
        # Convert ActionType enum to string if needed
        action_str = action.value if isinstance(action, ActionType) else action
        
        # Warn about common mistakes
        if action_str in ['RELEASE', 'MODIFY', 'HOLD']:
            logger.warning(
                f"Action '{action_str}' is unusual for experiments. "
                f"For NEW submissions, use action=ActionType.ADD (default)."
            )
        
        experiment_xml = build_experiment_xml_from_model(experiment)

        # Pre-validate before committing
        if validate_first and action_str not in ("VALIDATE",):
            self._validate_xml(
                label="experiment",
                submission_alias=submission_alias,
                experiment_xml=experiment_xml,
            )

        # Build XML using xml_builder functions
        submission_xml = build_submission_xml_from_model(
            submission_alias=submission_alias,
            action=action_str
        )
        
        logger.info(f"Submitting experiment '{experiment.alias}' via drop-box XML API")
        resp = self.api.submit_xml(
            submission_xml=submission_xml,
            experiment_xml=experiment_xml,
            test=self.test
        )
        
        return self.api.parse_receipt(resp)
    
    def submit_run(
        self,
        run: Run,
        submission_alias: Optional[str] = None,
        center_name: Optional[str] = None,
        action: Union[ActionType, str] = ActionType.ADD,
        validate_first: bool = False,
    ) -> ENAReceipt:
        """
        Submit a run to ENA via drop-box XML API.
        
        Note: Sequence files must already be uploaded to ENA FTP before submitting the run.
        Use upload_reads() method or ReadUploader directly to upload files first.
        
        Args:
            run: Run Pydantic model with file references
            submission_alias: Unique submission alias (auto-generated if None)
            center_name: Center name for submission (optional)
            action: Submission action (default: ADD for new submissions)
                - ADD: Submit new objects (use for initial submission)
                - MODIFY: Update existing objects (requires accession)
                - VALIDATE: Validate XML without submitting
                
                WARNING: For initial submissions, always use ADD (default).
            validate_first: If True, send the XML with action=VALIDATE before
                the real submission. Raises ValueError if ENA rejects the XML,
                allowing callers to abort before any objects are persisted.
            
        Returns:
            Parsed ENAReceipt object
        """
        submission_alias = submission_alias or f"sub_{run.alias}"
        
        # Convert ActionType enum to string if needed
        action_str = action.value if isinstance(action, ActionType) else action
        
        # Warn about common mistakes
        if action_str in ['RELEASE', 'MODIFY', 'HOLD']:
            logger.warning(
                f"Action '{action_str}' is unusual for runs. "
                f"For NEW submissions, use action=ActionType.ADD (default)."
            )
        
        run_xml = build_run_xml_from_model(run)

        # Pre-validate before committing
        if validate_first and action_str not in ("VALIDATE",):
            self._validate_xml(
                label="run",
                submission_alias=submission_alias,
                run_xml=run_xml,
            )

        # Build XML
        submission_xml = build_submission_xml_from_model(
            submission_alias=submission_alias,
            center_name=center_name,
            action=action_str
        )
        
        logger.info(f"Submitting run '{run.alias}' via drop-box XML API")
        resp = self.api.submit_xml(
            submission_xml=submission_xml,
            run_xml=run_xml,
            test=self.test
        )
        
        return self.api.parse_receipt(resp)
    
    def submit_project_sample_experiment(
        self,
        project: Project,
        sample: Sample,
        experiment: Experiment,
        submission_alias: Optional[str] = None,
        center_name: Optional[str] = None,
        action: Union[ActionType, str] = ActionType.ADD
    ) -> ENAReceipt:
        """
        Submit project, sample, and experiment together via Webin v2 XML endpoint.
        
        This is useful when submitting related objects that reference each other by alias.
        
        Args:
            project: Project Pydantic model
            sample: Sample Pydantic model
            experiment: Experiment Pydantic model
            submission_alias: Unique submission alias (auto-generated if None)
            center_name: Center name for submission (optional)
            action: Submission action (default: ADD for new submissions)
                - ADD: Submit new objects (use for initial submission)
                - VALIDATE: Validate XML without submitting
                
                WARNING: For initial submissions, always use ADD (default).
            
        Returns:
            Parsed ENAReceipt object
        """
        submission_alias = submission_alias or f"sub_{experiment.alias}"
        
        # Convert ActionType enum to string if needed
        action_str = action.value if isinstance(action, ActionType) else action
        
        # Warn about common mistakes
        if action_str in ['RELEASE', 'MODIFY', 'HOLD']:
            logger.warning(
                f"Action '{action_str}' is not appropriate for combined new submissions. "
                f"Use action=ActionType.ADD (default) for new objects."
            )
        
        # Build all XML sections
        submission_xml = build_submission_xml_from_model(
            submission_alias=submission_alias,
            center_name=center_name,
            action=action_str
        )
        project_xml = build_project_xml_from_model(project)
        sample_xml = build_sample_xml_from_model(sample)
        experiment_xml = build_experiment_xml_from_model(experiment)
        
        logger.info(f"Submitting project+sample+experiment via Webin v2 XML")
        resp = self.api.submit_webin_xml(
            submission_xml=submission_xml,
            project_xml=project_xml,
            sample_xml=sample_xml,
            experiment_xml=experiment_xml,
            path="/submit"
        )
        
        return self.api.parse_receipt(resp)
    
    def upload_reads(
        self,
        file_paths: Union[Path, List[Path]],
        remote_dir: str = ".",
        save_manifest: bool = True,
        manifest_path: Path = Path("manifest.txt"),
        max_retries: int = 3,
        file_pattern: str = "*"
    ) -> Dict[str, Any]:
        """
        Upload sequence read files to ENA FTP server.
        
        This must be done before submitting a RUN that references these files.
        
        Args:
            file_paths: Either a Path to a directory (will upload all matching files) 
                        or a List of Path objects to upload
            remote_dir: Remote directory on ENA FTP (default: home directory)
            save_manifest: Save manifest with MD5 checksums to file
            manifest_path: Path object for saving manifest file
            max_retries: Number of upload retry attempts
            file_pattern: Glob pattern for files when file_paths is a directory (default: "*" for all files)
            
        Returns:
            Dictionary with upload results and manifest info:
            {
                'uploaded': int,  # number of files uploaded
                'results': {filename: status},
                'manifest': [{'filename': ..., 'md5': ..., 'size': ...}],
                'manifest_file': Path or None
            }
            
        Example:
            >>> # Upload specific files
            >>> result = workflow.upload_reads(
            ...     file_paths=[Path("reads_R1.fastq.gz"), Path("reads_R2.fastq.gz")]
            ... )
            >>> 
            >>> # Upload all files from a directory
            >>> result = workflow.upload_reads(
            ...     file_paths=Path("./sequencing_data")
            ... )
            >>> 
            >>> # Upload only FASTQ files from a directory
            >>> result = workflow.upload_reads(
            ...     file_paths=Path("./sequencing_data"),
            ...     file_pattern="*.fastq.gz"
            ... )
            >>> 
            >>> print(f"Uploaded {result['uploaded']} files")
            >>> for file_info in result['manifest']:
            ...     print(f"{file_info['filename']}: MD5={file_info['md5']}")
        """
        # Handle directory input
        if isinstance(file_paths, Path):
            if file_paths.is_dir():
                logger.info(f"Scanning directory '{file_paths}' for files matching '{file_pattern}'")
                files_list = sorted(file_paths.glob(file_pattern))
                # Filter out directories, only keep files
                files_list = [f for f in files_list if f.is_file()]
                if not files_list:
                    raise ValueError(f"No files found in directory '{file_paths}' matching pattern '{file_pattern}'")
                logger.info(f"Found {len(files_list)} files to upload")
                file_paths = files_list
            else:
                # Single file provided as Path
                file_paths = [file_paths]
        
        uploader = ReadUploader()
        
        logger.info(f"Uploading {len(file_paths)} read files to ENA FTP")
        result = uploader.prepare_and_upload_reads(
            file_paths=file_paths,
            host="webin2.ebi.ac.uk" if self.test else "webin.ebi.ac.uk",
            username=self.username,
            password=self.password,
            remote_dir=remote_dir,
            use_tls=False,  # ENA FTP doesn't use TLS
            resume=False,
            verify=True,
            save_manifest=save_manifest,
            manifest_path=manifest_path,
            max_retries=max_retries
        )
        
        logger.info(f"Upload complete: {result['uploaded']} files uploaded")
        return result
    
    def update_study_action(
        self,
        accession: str,
        action: Union[ActionType, str],
        hold_until_date: Optional[str] = None,
        submission_alias: Optional[str] = None,
    ) -> ENAReceipt:
        """
        Apply a lifecycle action to an existing ENA study/project.

        Use this to update the hold/embargo date (HOLD), immediately release
        held data (RELEASE), cancel a previous submission (CANCEL), or
        validate the action without persisting (VALIDATE).

        Args:
            accession: ENA project accession (e.g. PRJEB12345).
            action: One of HOLD, RELEASE, CANCEL, VALIDATE (from ActionType).
                    ADD and MODIFY are not supported here — use submit_project_xml
                    for those.
            hold_until_date: New hold/embargo date (YYYY-MM-DD).  Required when
                             action is HOLD.
            submission_alias: Optional unique alias for this submission.  A
                              timestamped alias is auto-generated when omitted.

        Returns:
            Parsed ENAReceipt object.

        Raises:
            ValueError: If action is HOLD but hold_until_date is not provided, or
                        if action is ADD/MODIFY (unsupported by this method).

        Example:
            # Release a previously held study immediately
            receipt = workflow.update_study_action("PRJEB12345", action="RELEASE")

            # Move the embargo date forward
            receipt = workflow.update_study_action(
                "PRJEB12345", action="HOLD", hold_until_date="2027-01-01"
            )
        """
        action_str = action.value if isinstance(action, ActionType) else str(action).upper()

        if action_str in ("ADD", "MODIFY"):
            raise ValueError(
                f"Action '{action_str}' is not supported by update_study_action. "
                "Use submit_project_xml() to add or modify study metadata."
            )

        if action_str == "HOLD" and not hold_until_date:
            raise ValueError("hold_until_date is required for HOLD action.")

        submission_alias = submission_alias or (
            f"sub_{action_str.lower()}_{accession}_{int(time.time())}"
        )

        # Build the action dict.  The 'target' attribute on the element tells ENA
        # which object to affect; HoldUntilDate is added for HOLD.
        action_config: Dict[str, Any] = {"type": action_str, "target": accession}
        if action_str == "HOLD":
            action_config["HoldUntilDate"] = hold_until_date

        submission_xml = build_submission_xml_from_model(
            submission_alias=submission_alias,
            action=[action_config],
        )

        logger.info(f"Applying {action_str} action to study {accession}")
        logger.debug("Submission XML:\n%s", submission_xml)
        try:
            resp = self.api.submit_webin_xml(
                submission_xml=submission_xml,
                path="/submit",
            )
        except Exception as e:
            # Attach the generated XML so callers can display it for debugging
            e._submission_xml = submission_xml
            raise
        logger.debug("Response status: %s", resp.status_code)
        logger.debug("Response body:\n%s", resp.text)
        receipt = self.api.parse_receipt(resp)
        # Attach generated XML for GUI-level debugging
        receipt._submission_xml = submission_xml
        return receipt

    def _parse_json_response(self, response, object_type: str) -> ENAReceipt:
        """
        Parse JSON response from Webin v2 JSON endpoints into ENAReceipt format.
        
        ENA JSON response format:
        {
            "success": true/false,
            "receiptDate": "2026-01-19T18:27:12.144Z",
            "submission": {"alias": "...", "accession": "..."},
            "messages": {"info": [...], "error": [...], "warning": [...]},
            "actions": ["ADD"],
            "samples": [{"accession": "...", "alias": "...", "status": "..."}],
            "projects": [{"accession": "...", "alias": "...", "status": "..."}]
        }
        
        Note: ENA returns plural arrays (samples, projects) not singular objects.
        """        
        try:
            data = response.json()
        except Exception:
            return ENAReceipt(
                success=False,
                messages=[ENAMessage(type="ERROR", text="Failed to parse JSON response")]
            )
        
        receipt = ENAReceipt(
            success=data.get("success", False),
            receipt_date=data.get("receiptDate")
        )
        
        # Parse messages
        messages = data.get("messages", {})
        for msg_type in ["info", "error", "warning"]:
            for msg_text in messages.get(msg_type, []):
                receipt.messages.append(ENAMessage(
                    type=msg_type.upper(),
                    text=msg_text
                ))
        
        # Parse actions
        receipt.actions.extend(data.get("actions", []))
        
        # Parse submission object (always present)
        submission = data.get("submission", {})
        if submission:
            receipt.objects.append(ENAObject(
                object_type="SUBMISSION",
                accession=submission.get("accession"),
                alias=submission.get("alias")
            ))
        
        # Parse object-specific array (ENA returns plural: "projects", "samples", etc.)
        object_key = object_type.lower() + "s"
        for obj_data in data.get(object_key, []):
            receipt.objects.append(ENAObject(
                object_type=object_type,
                accession=obj_data.get("accession"),
                alias=obj_data.get("alias"),
                status=obj_data.get("status")
            ))
        
        return receipt