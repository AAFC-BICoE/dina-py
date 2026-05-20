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
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Dict

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
    def compute_md5(
        path: Path,
        chunk_size: int = 16 * 1024 * 1024,
        cancel_event=None,
        progress_callback=None,
        use_srun: bool = False,
    ) -> str:
        """Return MD5 hex digest for `path`.

        Delegates to the system ``md5sum`` binary when available — this is a
        C process that avoids Python loop overhead and the GIL entirely, and
        is typically 2–4× faster than the pure-Python fallback for large files.

        On HPC systems with login-node I/O limits, set ``use_srun=True`` to
        run ``md5sum`` on a compute node via SLURM ``srun`` instead.

        Args:
            path:              Path to the file.
            chunk_size:        Read chunk size in bytes (used by Python fallback only).
            cancel_event:      Optional ``threading.Event`` for cancellation (Python fallback only).
            progress_callback: Optional ``(bytes_done, total_bytes)`` callback (Python fallback only).
            use_srun:          Wrap ``md5sum`` with ``srun --ntasks=1`` to run on a compute node.
        """
        path = Path(path)

        # --- Fast path: native md5sum binary --------------------------------
        md5sum_bin = shutil.which("md5sum")
        if md5sum_bin:
            cmd = (["srun", "--ntasks=1", md5sum_bin, str(path)]
                   if use_srun else [md5sum_bin, str(path)])
            try:
                out = subprocess.check_output(cmd, text=True)
                # md5sum output: "<hash>  <filename>"
                return out.split()[0]
            except subprocess.CalledProcessError as e:
                logger.warning("md5sum failed (%s), falling back to Python hashlib", e)

        # --- Fallback: Python hashlib ---------------------------------------
        h = hashlib.md5(usedforsecurity=False)
        file_size = path.stat().st_size
        bytes_done = 0

        pbar = (
            tqdm(
                total=file_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=f"MD5 {path.name}",
            )
            if HAS_TQDM and file_size > 10 * 1024 * 1024
            else None
        )
        try:
            with path.open("rb") as fh:
                for chunk in iter(lambda: fh.read(chunk_size), b""):
                    if cancel_event is not None and cancel_event.is_set():
                        raise InterruptedError("MD5 computation cancelled")
                    h.update(chunk)
                    bytes_done += len(chunk)
                    if pbar is not None:
                        pbar.update(len(chunk))
                    if progress_callback is not None:
                        progress_callback(bytes_done, file_size)
        finally:
            if pbar is not None:
                pbar.close()

        return h.hexdigest()

    @staticmethod
    def build_manifest(file_paths: Iterable[Path], max_workers: int = 4) -> List[dict]:
        """
        Build a manifest list with filename, size and md5 for each path.

        MD5s are computed in parallel (``max_workers`` threads) which gives a
        meaningful speedup on network storage (e.g. GPFS) where concurrent
        reads saturate available bandwidth better than sequential reads.

        Returns a list of dicts (in original order):
            [{'filename': 'f1.fastq.gz', 'size': 12345, 'md5': '...'}, ...]
        """
        paths = [Path(p) for p in file_paths]
        for p in paths:
            if not p.exists():
                raise FileNotFoundError(f"File not found: {p}")

        def _process(p: Path) -> dict:
            logger.info(f"Processing {p.name}...")
            return {
                "filename": p.name,
                "size": p.stat().st_size,
                "md5": ReadUploader.compute_md5(p),
            }

        # Submit all files; collect results preserving original order.
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_process, p): i for i, p in enumerate(paths)}
            results: List[dict] = [None] * len(paths)  # type: ignore[list-item]
            for future in as_completed(futures):
                results[futures[future]] = future.result()

        return results

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
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
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
                        progress_callback=progress_callback,
                    )
                    
                    if success:
                        results[file_path.name] = "success"
                        logger.info(f"Successfully uploaded {file_path.name}")
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
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> bool:
        """Upload a single file via FTP with progress bar and resume support."""
        file_size = file_path.stat().st_size
        remote_filename = file_path.name

        logger.debug("Connecting to FTP host %s (tls=%s)", host, use_tls)
        
        # Try TLS connection, fall back to plain FTP if server doesn't support it
        try:
            ftp_class = ftplib.FTP_TLS if use_tls else ftplib.FTP
            ftp = ftp_class(host, timeout=timeout)
        except Exception as e:
            if use_tls:
                logger.warning(f"FTP TLS failed ({e}), retrying without TLS")
                return self._upload_single_file_ftp(
                    file_path=file_path,
                    host=host,
                    username=username,
                    password=password,
                    remote_dir=remote_dir,
                    use_tls=False,  # Retry without TLS
                    passive=passive,
                    timeout=timeout,
                    resume=resume,
                    verify=verify,
                    progress_callback=progress_callback,
                )
            else:
                raise
        
        try:
            ftp.login(username, password)
        except Exception as e:
            ftp.close()
            if use_tls:
                logger.warning(f"FTP TLS login failed ({e}), retrying without TLS")
                return self._upload_single_file_ftp(
                    file_path=file_path,
                    host=host,
                    username=username,
                    password=password,
                    remote_dir=remote_dir,
                    use_tls=False,  # Retry without TLS
                    passive=passive,
                    timeout=timeout,
                    resume=resume,
                    verify=verify,
                    progress_callback=progress_callback,
                )
            else:
                raise
        
        with ftp:
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
                        logger.info(f"{remote_filename} already uploaded (skipping)")
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

                bytes_sent = start_pos
                cmd = f'APPE {remote_filename}' if start_pos > 0 else f'STOR {remote_filename}'

                pbar = (
                    tqdm(
                        total=file_size,
                        initial=start_pos,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=f"Uploading {remote_filename}",
                    )
                    if HAS_TQDM
                    else None
                )

                def _chunk_cb(data):
                    nonlocal bytes_sent
                    bytes_sent += len(data)
                    if pbar is not None:
                        pbar.update(len(data))
                    if progress_callback is not None:
                        progress_callback(remote_filename, bytes_sent, file_size)

                try:
                    ftp.storbinary(cmd, f, blocksize=self.chunk_size, callback=_chunk_cb)
                finally:
                    if pbar is not None:
                        pbar.close()

                if pbar is None:
                    logger.info(f"Uploaded {remote_filename}")

            # Verify upload - try multiple methods
            if verify:
                # Method 1: Try SIZE command (may not work on ENA)
                try:
                    remote_size = ftp.size(remote_filename)
                    if remote_size == file_size:
                        logger.info(f"Upload verified via SIZE: {file_size / 1e6:.1f} MB")
                        return True
                    else:
                        logger.error(
                            f"Size mismatch: local={file_size}, remote={remote_size}"
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
                        logger.info(f"Upload verified via MLSD: {filename} ({expected_size / 1e6:.1f} MB)")
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
                logger.info(f"Upload verified via NLST: {filename} found in directory")
                return True
            else:
                logger.error(f"File {filename} not found in NLST listing")
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

    # -----------------------
    # FTP remote-file listing
    # -----------------------
    def list_remote_files(
        self,
        host: str,
        username: str,
        password: str,
        remote_dir: Optional[str] = None,
        use_tls: bool = True,
        passive: bool = True,
        timeout: int = 30,
    ) -> Dict[str, int]:
        """List files present on the FTP server and return their sizes.

        Useful for verifying that sequence files have already been uploaded
        before attempting a Run submission.

        Args:
            host:       FTP server hostname (e.g. ``"webin2.ebi.ac.uk"``).
            username:   Webin username.
            password:   Webin password.
            remote_dir: Optional remote directory to ``cwd`` into before listing.
            use_tls:    Use FTPS (recommended for ENA Webin).
            passive:    Use passive mode.
            timeout:    Connection timeout in seconds.

        Returns:
            ``{filename: size_in_bytes}`` dict for every file visible in the
            remote directory.  Directories are excluded.  Returns an empty dict
            if the connection fails or the directory is empty.
        """
        ftp_class = ftplib.FTP_TLS if use_tls else ftplib.FTP
        result: Dict[str, int] = {}

        def _do_list(ftp_conn) -> Dict[str, int]:
            """Run the MLSD→NLST listing on an already-logged-in connection."""
            listing: Dict[str, int] = {}
            try:
                for name, facts in ftp_conn.mlsd():
                    if facts.get("type", "file") == "file":
                        listing[name] = int(facts.get("size", 0))
                logger.debug("Listed %d remote files via MLSD", len(listing))
            except Exception:
                logger.debug("MLSD not supported, falling back to NLST")
                try:
                    for name in ftp_conn.nlst():
                        listing[name] = 0
                except Exception as exc:
                    logger.warning("NLST failed: %s", exc)
            return listing

        try:
            with ftp_class(host, timeout=timeout) as ftp:
                ftp.login(username, password)

                if use_tls:
                    # Request encrypted data channel; ignore if not supported.
                    try:
                        ftp.prot_p()
                    except Exception:
                        logger.debug("PROT P not supported, trying PROT C")
                        try:
                            ftp.prot_c()
                        except Exception:
                            logger.debug("PROT C also not supported, proceeding")

                ftp.set_pasv(passive)

                if remote_dir:
                    try:
                        ftp.cwd(remote_dir)
                    except ftplib.error_perm as exc:
                        logger.warning("Could not cwd to %s: %s", remote_dir, exc)
                        return {}

                result = _do_list(ftp)

        except Exception as exc:
            if use_tls:
                # TLS not supported by server (e.g. AUTH TLS → 504 on test servers);
                # retry transparently with plain FTP.
                logger.warning("FTP TLS failed (%s), retrying without TLS", exc)
                try:
                    with ftplib.FTP(host, timeout=timeout) as ftp:
                        ftp.login(username, password)
                        ftp.set_pasv(passive)
                        if remote_dir:
                            try:
                                ftp.cwd(remote_dir)
                            except ftplib.error_perm as exc2:
                                logger.warning("Could not cwd to %s: %s", remote_dir, exc2)
                                return {}
                        result = _do_list(ftp)
                except Exception as exc2:
                    logger.error("FTP listing failed (plain fallback): %s", exc2)
            else:
                logger.error("FTP listing failed: %s", exc)

        except Exception as exc:
            logger.error("FTP listing failed: %s", exc)

        return result

    def check_files_on_ftp(
        self,
        file_paths: Iterable[Path],
        host: str,
        username: str,
        password: str,
        remote_dir: Optional[str] = None,
        use_tls: bool = True,
    ) -> Dict[str, bool]:
        """Check which local files are already present on the FTP server.

        Args:
            file_paths: Local :class:`~pathlib.Path` objects to check.
            host:       FTP server hostname.
            username:   Webin username.
            password:   Webin password.
            remote_dir: Optional remote directory to check within.
            use_tls:    Use FTPS.

        Returns:
            ``{filename: True/False}`` — ``True`` when the file exists on the server.
        """
        remote = self.list_remote_files(host, username, password, remote_dir, use_tls)
        return {Path(p).name: Path(p).name in remote for p in file_paths}
