"""
Submit an ENA Run with Sequence Files - Simple Example

This is a notebook-style example you can copy and adapt.
Shows two approaches:
  1. Upload files and submit run together
  2. Use pre-uploaded files with manifest

Requires: WEBIN_USERNAME, WEBIN_PASSWORD in environment or .env file
"""
from pathlib import Path
from dinapy.ena.models import Run, DataBlock, File, ObjectRef
from dinapy.ena.submission import ENASubmissionWorkflow

# =============================================================================
# APPROACH 1: Upload files and submit run together
# =============================================================================

# Initialize workflow
workflow = ENASubmissionWorkflow(test=True)

# Upload sequence files to ENA FTP (automatically calculates MD5)
# Option 1: Upload specific files
file_paths = [
    Path("reads_R1.fastq.gz"),
    Path("reads_R2.fastq.gz")
]

print("Uploading files to ENA FTP...")
upload_result = workflow.upload_reads(
    file_paths=file_paths,
    save_manifest=True,        # Saves MD5s to manifest.txt
    manifest_path=Path("manifest.txt")
)

# Option 2: Upload all FASTQ files from a directory
# upload_result = workflow.upload_reads(
#     file_paths=Path("./sequencing_data"),
#     file_pattern="*.fastq.gz",
#     save_manifest=True,
#     manifest_path=Path("manifest.txt")
# )

print(f"Uploaded {upload_result['uploaded']} files")
for file_info in upload_result['manifest']:
    print(f"  {file_info['filename']}: MD5={file_info['md5'][:16]}...")
print()

# Build File objects with MD5s from upload
files = [
    File(
        filename=file_info['filename'],
        filetype="fastq",
        checksumMethod="MD5",
        checksum=file_info['md5']
    )
    for file_info in upload_result['manifest']
]

# Create Run model linking to existing experiment
run = Run(
    alias="my_run_001",
    title="Paired-end sequencing of soil sample",
    experiment_ref=ObjectRef(accession="ERX123456"),  # Link to existing experiment
    data_blocks=[DataBlock(files=files)]
)

# Submit run
receipt = workflow.submit_run(run=run)

if receipt.success:
    print("SUCCESS")
    run_accession = receipt.get_accession("RUN")
    print(f"Run Accession: {run_accession}")
else:
    print("FAILURE")
    print(f"Errors: {receipt.get_errors()}")

from dinapy.ena.receipt import format_receipt_summary
print("\n" + "="*60)
print(format_receipt_summary(receipt))

# =============================================================================
# APPROACH 2: Use pre-uploaded files with known MD5 checksums
# =============================================================================

# If files are already on ENA FTP, just create File objects with MD5s
run_preupload = Run(
    alias="my_run_002",
    title="Run with pre-uploaded files",
    experiment_ref=ObjectRef(accession="ERX123456"),
    data_blocks=[
        DataBlock(files=[
            File(
                filename="reads_R1.fastq.gz",
                filetype="fastq",
                checksumMethod="MD5",
                checksum="a1b2c3d4e5f6..."  # Known MD5
            ),
            File(
                filename="reads_R2.fastq.gz",
                filetype="fastq",
                checksumMethod="MD5",
                checksum="f6e5d4c3b2a1..."  # Known MD5
            )
        ])
    ]
)

# Submit (files must already be on ENA FTP)
# receipt = workflow.submit_run(run=run_preupload)
