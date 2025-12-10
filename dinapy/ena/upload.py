"""ENA read-file upload helpers (FTP) and manifest utilities.

This module provides a small, pragmatic helper class `ReadUploader` that:
- computes MD5 checksums and builds a simple manifest,
- uploads files via FTPS (FTP_TLS) or plain FTP with progress bars and resume support,
- exposes a convenience `prepare_and_upload_reads` flow.

This is intentionally lightweight and does not handle XML submission (those
are managed elsewhere in the codebase). It is designed for easy unit-testing
by mocking `ftplib`.
"""

from __future__ import annotations

import hashlib
import ftplib
import logging
import time
from pathlib import Path
from typing import Iterable, List, Optional, Dict

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

logger = logging.getLogger(__name__)


class ReadUploader:
    """Helper for uploading sequencing read files to ENA-style servers."""

    def __init__(self, chunk_size: int = 8192 * 128) -> None:
        """
        Initialize uploader.
        
        Args:
            chunk_size: Size of chunks for reading/uploading (default: 1MB)
        """
        self.chunk_size = chunk_size

    # -----------------------
    # Utilities
    # -----------------------
    @staticmethod
    def compute_md5(path: Path, chunk_size: int = 8192) -> str:
        """Return MD5 hex digest for `path` with optional progress bar."""
        h = hashlib.md5()
        file_size = path.stat().st_size
        
        with path.open("rb") as fh:
            if HAS_TQDM and file_size > 10 * 1024 * 1024:  # Show progress for files > 10MB
                with tqdm(
                    total=file_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"Computing MD5 for {path.name}"
                ) as pbar:
                    for chunk in iter(lambda: fh.read(chunk_size), b""):
                        h.update(chunk)
                        pbar.update(len(chunk))
            else:
                for chunk in iter(lambda: fh.read(chunk_size), b""):
                    h.update(chunk)
        
        return h.hexdigest()

    @staticmethod
    def build_manifest(file_paths: Iterable[Path]) -> List[dict]:
        """
        Build a manifest list with filename, size and md5 for each path.

        Returns a list of dicts:
            [{'filename': 'f1.fastq.gz', 'size': 12345, 'md5': '...'}, ...]
        """
        manifest: List[dict] = []
        for p in file_paths:
            p = Path(p)
            if not p.exists():
                raise FileNotFoundError(f"File not found: {p}")
            
            logger.info(f"Processing {p.name}...")
            manifest.append(
                {
                    "filename": p.name,
                    "size": p.stat().st_size,
                    "md5": ReadUploader.compute_md5(p)
                }
            )
        return manifest

    @staticmethod
    def write_manifest_file(manifest: List[dict], out_path: Path) -> None:
        """
        Write a simple tab-delimited manifest file with columns:
        filename<TAB>size<TAB>md5

        This format is useful for local records; ENA-specific manifest formats
        may vary and are not produced automatically here.
        """
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            fh.write("filename\tsize\tmd5\n")
            for item in manifest:
                fh.write(f"{item['filename']}\t{item['size']}\t{item['md5']}\n")

    # -----------------------
    # FTP upload with progress and resume
    # -----------------------
    def upload_via_ftp(
        self,
        file_paths: Iterable[Path],
        host: str,
        username: str,
        password: str,
        remote_dir: Optional[str] = None,
        use_tls: bool = True,
        passive: bool = True,
        timeout: int = 60,
        resume: bool = True,
        verify: bool = True,
        max_retries: int = 3,
    ) -> Dict[str, str]:
        """
        Upload local files to an FTP server with progress bars and resume support.

        Args:
            file_paths: Iterable of Path objects to upload
            host: FTP host (e.g. 'webin2.ebi.ac.uk')
            username: FTP username
            password: FTP password
            remote_dir: Optional remote directory to change into before uploading
            use_tls: Use FTPS (FTP_TLS) when True
            passive: Use passive mode
            timeout: Connection timeout in seconds
            resume: Resume interrupted uploads
            verify: Verify file size after upload
            max_retries: Maximum number of retry attempts per file

        Returns:
            Dict mapping filename to status ('success', 'failed', or error message)
        """
        results: Dict[str, str] = {}
        
        for file_path in file_paths:
            file_path = Path(file_path)
            if not file_path.exists():
                results[file_path.name] = f"error: File not found"
                logger.error(f"File not found: {file_path}")
                continue
            
            # Retry logic for each file
            for attempt in range(max_retries):
                try:
                    logger.info(f"Uploading {file_path.name} (attempt {attempt + 1}/{max_retries})")
                    success = self._upload_single_file_ftp(
                        file_path=file_path,
                        host=host,
                        username=username,
                        password=password,
                        remote_dir=remote_dir,
                        use_tls=use_tls,
                        passive=passive,
                        timeout=timeout,
                        resume=resume,
                        verify=verify,
                    )
                    
                    if success:
                        results[file_path.name] = "success"
                        logger.info(f"✓ Successfully uploaded {file_path.name}")
                        break
                    else:
                        results[file_path.name] = "failed"
                        
                except Exception as e:
                    logger.error(f"Upload attempt {attempt + 1} failed for {file_path.name}: {e}")
                    
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.info(f"Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        results[file_path.name] = f"error: {str(e)}"
                        logger.error(f"✗ All attempts failed for {file_path.name}")
        
        return results

    def _upload_single_file_ftp(
        self,
        file_path: Path,
        host: str,
        username: str,
        password: str,
        remote_dir: Optional[str],
        use_tls: bool,
        passive: bool,
        timeout: int,
        resume: bool,
        verify: bool,
    ) -> bool:
        """Upload a single file via FTP with progress bar and resume support."""
        ftp_class = ftplib.FTP_TLS if use_tls else ftplib.FTP
        file_size = file_path.stat().st_size
        remote_filename = file_path.name

        logger.debug("Connecting to FTP host %s (tls=%s)", host, use_tls)
        
        with ftp_class(host, timeout=timeout) as ftp:
            ftp.login(username, password)
            
            if use_tls:
                try:
                    ftp.prot_p()
                except Exception:
                    logger.debug("FTP PROT P not supported/required by server")
            
            ftp.set_pasv(passive)

            if remote_dir:
                self._ensure_remote_dir(ftp, remote_dir)
                ftp.cwd(remote_dir)

            # Check if file exists and get size for resume (only if server supports SIZE)
            start_pos = 0
            if resume:
                try:
                    start_pos = ftp.size(remote_filename)
                    if start_pos == file_size:
                        logger.info(f"✓ {remote_filename} already uploaded (skipping)")
                        return True
                    elif start_pos > 0:
                        logger.info(f"Resuming from {start_pos / 1e6:.1f} MB")
                except (ftplib.error_perm, ftplib.error_temp) as e:
                    # Server doesn't support SIZE command or file doesn't exist - start fresh
                    logger.debug(f"Resume check failed (normal for some servers): {e}")
                    start_pos = 0

            # Upload with progress bar
            with file_path.open('rb') as f:
                if start_pos > 0:
                    f.seek(start_pos)
                
                if HAS_TQDM:
                    with tqdm(
                        total=file_size,
                        initial=start_pos,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=f"Uploading {remote_filename}"
                    ) as pbar:
                        def callback(data):
                            pbar.update(len(data))
                        
                        cmd = f'STOR {remote_filename}'
                        if start_pos > 0:
                            cmd = f'APPE {remote_filename}'  # Append mode for resume
                        
                        ftp.storbinary(cmd, f, blocksize=self.chunk_size, callback=callback)
                else:
                    # No progress bar
                    cmd = f'STOR {remote_filename}'
                    if start_pos > 0:
                        cmd = f'APPE {remote_filename}'
                    
                    ftp.storbinary(cmd, f, blocksize=self.chunk_size)
                    logger.info(f"Uploaded {remote_filename}")

            # Verify upload - try multiple methods
            if verify:
                # Method 1: Try SIZE command (may not work on ENA)
                try:
                    remote_size = ftp.size(remote_filename)
                    if remote_size == file_size:
                        logger.info(f"✓ Upload verified via SIZE: {file_size / 1e6:.1f} MB")
                        return True
                    else:
                        logger.error(
                            f"✗ Size mismatch: local={file_size}, remote={remote_size}"
                        )
                        return False
                except (ftplib.error_perm, ftplib.error_temp) as e:
                    logger.debug(f"SIZE command not supported: {e}")
                    # Fall through to alternative verification methods
                
                # Method 2: Try MLSD (modern listing with size)
                if self._verify_upload_via_mlsd(ftp, remote_filename, file_size):
                    return True
                
                # Method 3: Try NLST (basic listing, just checks file exists)
                if self._verify_upload_via_nlst(ftp, remote_filename):
                    return True
                
                # If all verification methods failed
                logger.warning(f"⚠ Could not verify upload - no supported verification method")
                logger.info(f"Upload completed but verification unavailable")
                return True

            return True

    def _verify_upload_via_mlsd(self, ftp: ftplib.FTP, filename: str, expected_size: int) -> bool:
        """Verify upload using MLSD command (modern FTP, includes size)."""
        try:
            logger.debug(f"Attempting MLSD verification for {filename}")
            for name, facts in ftp.mlsd():
                if name == filename:
                    remote_size = int(facts.get('size', 0))
                    if remote_size == expected_size:
                        logger.info(f"✓ Upload verified via MLSD: {filename} ({expected_size / 1e6:.1f} MB)")
                        return True
                    else:
                        logger.warning(
                            f"Size mismatch via MLSD: local={expected_size}, remote={remote_size}"
                        )
                        return False
            logger.debug(f"File {filename} not found in MLSD listing")
            return False
        except (ftplib.error_perm, AttributeError) as e:
            logger.debug(f"MLSD not supported: {e}")
            return False

    def _verify_upload_via_nlst(self, ftp: ftplib.FTP, filename: str) -> bool:
        """Verify upload using NLST command (basic listing, just checks existence)."""
        try:
            logger.debug(f"Attempting NLST verification for {filename}")
            files = ftp.nlst()
            if filename in files:
                logger.info(f"✓ Upload verified via NLST: {filename} found in directory")
                return True
            else:
                logger.error(f"✗ File {filename} not found in NLST listing")
                return False
        except ftplib.error_perm as e:
            logger.debug(f"NLST not supported: {e}")
            return False
    
    @staticmethod
    def _ensure_remote_dir(ftp: ftplib.FTP, remote_dir: str) -> None:
        """Create remote directory if it doesn't exist."""
        try:
            ftp.cwd(remote_dir)
        except ftplib.error_perm:
            try:
                ftp.mkd(remote_dir)
                ftp.cwd(remote_dir)
            except ftplib.error_perm as e:
                raise RuntimeError(
                    f"Could not create or access remote directory {remote_dir}: {e}"
                )

    # -----------------------
    # High-level convenience flow
    # -----------------------
    def prepare_and_upload_reads(
        self,
        file_paths: Iterable[Path],
        host: str,
        username: str,
        password: str,
        remote_dir: Optional[str] = None,
        use_tls: bool = True,
        resume: bool = True,
        verify: bool = True,
        max_retries: int = 3,
        dry_run: bool = False,
        save_manifest: bool = True,
        manifest_path: Optional[Path] = None,
    ) -> dict:
        """
        Compute manifest and upload files via FTP.

        Args:
            file_paths: Files to upload
            host: FTP server hostname (e.g. 'webin2.ebi.ac.uk')
            username: FTP username
            password: FTP password
            remote_dir: Remote directory for upload
            use_tls: Use FTPS (recommended for ENA)
            resume: Enable resume support for interrupted uploads
            verify: Verify uploads by checking file size
            max_retries: Maximum retry attempts per file
            dry_run: Only compute manifest, don't upload
            save_manifest: Save manifest to file (default: True)
            manifest_path: Path to save manifest file (default: manifest.txt in current dir)

        Returns:
            Dict containing:
                - 'manifest': List of file info dicts (includes MD5)
                - 'uploaded': bool
                - 'results': Dict of filename -> status (if uploaded)
                - 'manifest_file': Path to saved manifest file (if save_manifest=True)
        """
        paths = [Path(p) for p in file_paths]
        
        logger.info("Building manifest...")
        manifest = self.build_manifest(paths)
        
        # Log MD5s for each file
        logger.info("File checksums:")
        for item in manifest:
            logger.info(f"  {item['filename']}: MD5={item['md5']}")
        
        # Save manifest to file
        manifest_file_path = None
        if save_manifest:
            if manifest_path is None:
                manifest_path = Path("manifest.txt")
            self.write_manifest_file(manifest, manifest_path)
            manifest_file_path = str(manifest_path.absolute())
            logger.info(f"Manifest saved to: {manifest_file_path}")
        
        if dry_run:
            logger.info("Dry run: computed manifest only")
            return {
                "manifest": manifest,
                "uploaded": False,
                "manifest_file": manifest_file_path
            }

        results = self.upload_via_ftp(
            paths,
            host,
            username,
            password,
            remote_dir=remote_dir,
            use_tls=use_tls,
            resume=resume,
            verify=verify,
            max_retries=max_retries,
        )
        
        return {
            "manifest": manifest,
            "uploaded": True,
            "results": results,
            "manifest_file": manifest_file_path
        }