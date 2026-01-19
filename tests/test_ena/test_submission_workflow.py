"""
Tests for ENA submission workflow.

Tests the ENASubmissionWorkflow class with mocked API calls.
"""

import unittest
from unittest.mock import Mock, patch
import json
from pathlib import Path

from dinapy.ena.submission import ENASubmissionWorkflow
from dinapy.ena.models import (
    Sample, Organism, Attribute,
    Project, Experiment, Run,
    Design, Platform, LibraryDescriptor, LibraryLayout,
    ObjectRef, DataBlock, File
)
from dinapy.ena.receipt import ENAReceipt


class TestENASubmissionWorkflow(unittest.TestCase):
    """Test ENASubmissionWorkflow class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the WebinAPI to avoid real network calls
        self.mock_api = Mock()
        self.workflow = ENASubmissionWorkflow(
            username="test_user",
            password="test_pass",
            test=True,
            webin_api=self.mock_api
        )
    
    def test_workflow_initialization(self):
        """Test workflow initialization."""
        self.assertEqual(self.workflow.username, "test_user")
        self.assertEqual(self.workflow.password, "test_pass")
        self.assertTrue(self.workflow.test)
        self.assertEqual(self.workflow.api, self.mock_api)
    
    def test_workflow_env_variables(self):
        """Test workflow initialization from environment variables."""
        with patch.dict('os.environ', {
            'WEBIN_USERNAME': 'env_user',
            'WEBIN_PASSWORD': 'env_pass'
        }):
            workflow = ENASubmissionWorkflow(test=True, webin_api=self.mock_api)
            self.assertEqual(workflow.username, 'env_user')
            self.assertEqual(workflow.password, 'env_pass')


class TestProjectSubmission(unittest.TestCase):
    """Test project submission."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.workflow = ENASubmissionWorkflow(
            username="test",
            password="test",
            test=True,
            webin_api=self.mock_api
        )
        
        self.project = Project(
            alias="test_project",
            title="Test Project",
            description="A test project"
        )
    
    def test_submit_project_success(self):
        """Test successful project submission."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "accession": "PRJEB12345",
            "alias": "test_project"
        }
        mock_response.headers.get.return_value = "application/json"
        
        self.mock_api.post_json.return_value = mock_response
        
        # Submit project
        receipt = self.workflow.submit_project(self.project)
        
        # Verify API was called
        self.mock_api.post_json.assert_called_once()
        call_args = self.mock_api.post_json.call_args
        
        # Verify payload structure
        payload = call_args[1]['payload']
        self.assertIn('submission', payload)
        self.assertIn('projects', payload)
        self.assertEqual(len(payload['projects']), 1)
        self.assertEqual(payload['projects'][0]['alias'], 'test_project')
    
    def test_submit_project_custom_alias(self):
        """Test project submission with custom submission alias."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.headers.get.return_value = "application/json"
        self.mock_api.post_json.return_value = mock_response
        
        self.workflow.submit_project(
            self.project,
            submission_alias="custom_sub_alias"
        )
        
        call_args = self.mock_api.post_json.call_args
        payload = call_args[1]['payload']
        self.assertEqual(payload['submission']['alias'], 'custom_sub_alias')


class TestSampleSubmission(unittest.TestCase):
    """Test sample submission."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.workflow = ENASubmissionWorkflow(
            username="test",
            password="test",
            test=True,
            webin_api=self.mock_api
        )
        
        self.sample = Sample(
            alias="test_sample",
            title="Test Sample",
            organism=Organism(
                taxon_id=9606,
                scientific_name="Homo sapiens"
            ),
            attributes=[
                Attribute(tag="collection date", value="2024-01-01"),
                Attribute(tag="geographic location (country and/or sea)", value="Canada")
            ]
        )
    
    def test_submit_sample_success(self):
        """Test successful sample submission."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "accession": "SAMEA123456",
            "alias": "test_sample"
        }
        mock_response.headers.get.return_value = "application/json"
        
        self.mock_api.post_json.return_value = mock_response
        
        # Submit sample
        receipt = self.workflow.submit_sample(self.sample)
        
        # Verify API was called
        self.mock_api.post_json.assert_called_once()
        call_args = self.mock_api.post_json.call_args
        
        # Verify payload structure
        payload = call_args[1]['payload']
        self.assertIn('submission', payload)
        self.assertIn('samples', payload)
        self.assertEqual(len(payload['samples']), 1)
        
        # Verify sample data
        sample_data = payload['samples'][0]
        self.assertEqual(sample_data['alias'], 'test_sample')
        self.assertEqual(sample_data['title'], 'Test Sample')
        self.assertIn('organism', sample_data)
        self.assertEqual(sample_data['organism']['taxonId'], 9606)
        self.assertIn('attributes', sample_data)
        self.assertEqual(len(sample_data['attributes']), 2)
    
    def test_submit_sample_json_format(self):
        """Test that sample submission uses correct JSON format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.headers.get.return_value = "application/json"
        self.mock_api.post_json.return_value = mock_response
        
        self.workflow.submit_sample(self.sample)
        
        call_args = self.mock_api.post_json.call_args
        payload = call_args[1]['payload']
        
        # Verify organism structure (not sampleName)
        sample_data = payload['samples'][0]
        self.assertIn('organism', sample_data)
        self.assertNotIn('sampleName', sample_data)
        
        # Verify attributes (not sampleAttributes)
        self.assertIn('attributes', sample_data)
        self.assertNotIn('sampleAttributes', sample_data)


class TestExperimentSubmission(unittest.TestCase):
    """Test experiment submission."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.workflow = ENASubmissionWorkflow(
            username="test",
            password="test",
            test=True,
            webin_api=self.mock_api
        )
        
        self.experiment = Experiment(
            alias="test_experiment",
            title="Test Experiment",
            studyRef=ObjectRef(accession="PRJEB12345"),
            design=Design(
                designDescription="Test design",
                sampleDescriptor=ObjectRef(accession="SAMEA123456"),
                libraryDescriptor=LibraryDescriptor(
                    libraryStrategy="WGS",
                    librarySource="GENOMIC",
                    librarySelection="RANDOM",
                    libraryLayout=LibraryLayout(layoutType="PAIRED")
                )
            ),
            platform=Platform(instrumentModel="Illumina NovaSeq 6000")
        )
    
    def test_submit_experiment_uses_xml(self):
        """Test that experiment submission uses XML API."""
        mock_response = Mock()
        self.mock_api.submit_xml.return_value = mock_response
        self.mock_api.parse_receipt.return_value = ENAReceipt(success=True)
        
        self.workflow.submit_experiment(self.experiment)
        
        # Verify XML submission was called
        self.mock_api.submit_xml.assert_called_once()
        call_args = self.mock_api.submit_xml.call_args
        
        # Verify XML strings were passed
        self.assertIn('submission_xml', call_args[1])
        self.assertIn('experiment_xml', call_args[1])


class TestRunSubmission(unittest.TestCase):
    """Test run submission."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.workflow = ENASubmissionWorkflow(
            username="test",
            password="test",
            test=True,
            webin_api=self.mock_api
        )
        
        self.run = Run(
            alias="test_run",
            experimentRef=ObjectRef(accession="ERX123456"),
            dataBlocks=[
                DataBlock(
                    files=[
                        File(
                            filename="reads_R1.fastq.gz",
                            filetype="fastq",
                            checksum="abc123",
                            checksumMethod="MD5"
                        )
                    ]
                )
            ]
        )
    
    def test_submit_run_uses_xml(self):
        """Test that run submission uses XML API."""
        mock_response = Mock()
        self.mock_api.submit_xml.return_value = mock_response
        self.mock_api.parse_receipt.return_value = ENAReceipt(success=True)
        
        self.workflow.submit_run(self.run)
        
        # Verify XML submission was called
        self.mock_api.submit_xml.assert_called_once()
        call_args = self.mock_api.submit_xml.call_args
        
        # Verify XML strings were passed
        self.assertIn('submission_xml', call_args[1])
        self.assertIn('run_xml', call_args[1])


class TestCombinedSubmission(unittest.TestCase):
    """Test combined project+sample+experiment submission."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.workflow = ENASubmissionWorkflow(
            username="test",
            password="test",
            test=True,
            webin_api=self.mock_api
        )
        
        self.project = Project(
            alias="test_project",
            title="Test Project"
        )
        
        self.sample = Sample(
            alias="test_sample",
            organism=Organism(taxon_id=9606),
            attributes=[Attribute(tag="test", value="value")]
        )
        
        self.experiment = Experiment(
            alias="test_experiment",
            studyRef=ObjectRef(refname="test_project"),
            design=Design(
                designDescription="Test",
                sampleDescriptor=ObjectRef(refname="test_sample"),
                libraryDescriptor=LibraryDescriptor(
                    libraryStrategy="WGS",
                    librarySource="GENOMIC",
                    librarySelection="RANDOM",
                    libraryLayout=LibraryLayout(layoutType="SINGLE")
                )
            ),
            platform=Platform(instrumentModel="Illumina MiSeq")
        )
    
    def test_submit_combined(self):
        """Test combined submission."""
        mock_response = Mock()
        self.mock_api.submit_webin_xml.return_value = mock_response
        self.mock_api.parse_receipt.return_value = ENAReceipt(success=True)
        
        self.workflow.submit_project_sample_experiment(
            project=self.project,
            sample=self.sample,
            experiment=self.experiment
        )
        
        # Verify Webin XML API was called
        self.mock_api.submit_webin_xml.assert_called_once()
        call_args = self.mock_api.submit_webin_xml.call_args
        
        # Verify all XML components were passed
        self.assertIn('submission_xml', call_args[1])
        self.assertIn('project_xml', call_args[1])
        self.assertIn('sample_xml', call_args[1])
        self.assertIn('experiment_xml', call_args[1])


class TestReadUpload(unittest.TestCase):
    """Test read file upload functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.workflow = ENASubmissionWorkflow(
            username="test",
            password="test",
            test=True,
            webin_api=self.mock_api
        )
    
    @patch('dinapy.ena.submission.ReadUploader')
    def test_upload_reads(self, mock_uploader_class):
        """Test read file upload."""
        # Mock the uploader
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader
        mock_uploader.prepare_and_upload_reads.return_value = {
            'uploaded': 2,
            'results': {
                'file1.fastq.gz': 'success',
                'file2.fastq.gz': 'success'
            },
            'manifest': [
                {'filename': 'file1.fastq.gz', 'md5': 'abc123', 'size': 1000},
                {'filename': 'file2.fastq.gz', 'md5': 'def456', 'size': 2000}
            ],
            'manifest_file': Path('manifest.txt')
        }
        
        # Upload files
        result = self.workflow.upload_reads(
            file_paths=['file1.fastq.gz', 'file2.fastq.gz']
        )
        
        # Verify upload was called
        mock_uploader.prepare_and_upload_reads.assert_called_once()
        
        # Verify result
        self.assertEqual(result['uploaded'], 2)
        self.assertEqual(len(result['manifest']), 2)


class TestJSONResponseParsing(unittest.TestCase):
    """Test JSON response parsing helper."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.workflow = ENASubmissionWorkflow(
            username="test",
            password="test",
            test=True,
            webin_api=self.mock_api
        )
    
    def test_parse_json_response_success(self):
        """Test parsing successful JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "accession": "SAMEA123456",
            "alias": "test_sample"
        }
        
        receipt = self.workflow._parse_json_response(mock_response, "SAMPLE")
        
        self.assertTrue(receipt.success)
        self.assertEqual(len(receipt.objects), 1)
        self.assertEqual(receipt.objects[0].accession, "SAMEA123456")
        self.assertEqual(receipt.objects[0].alias, "test_sample")
    
    def test_parse_json_response_failure(self):
        """Test parsing failed JSON response."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.side_effect = Exception("Invalid JSON")
        
        receipt = self.workflow._parse_json_response(mock_response, "SAMPLE")
        
        self.assertFalse(receipt.success)
        self.assertEqual(len(receipt.messages), 1)


if __name__ == "__main__":
    unittest.main()
