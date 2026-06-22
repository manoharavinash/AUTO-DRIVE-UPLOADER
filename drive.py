"""
Low-level RClone wrapper for subprocess operations.
Handles all cloud operations via rclone subprocess pipes.
"""

import subprocess
import os
import json
from typing import Optional, Dict, List, Tuple


class RCloneDriveError(Exception):
    """Custom exception for RClone operations."""
    pass


class RCloneDrive:
    """Wrapper for RClone cloud operations using subprocess pipes."""

    REMOTE_NAME = "google auto photo:"

    def __init__(self):
        """Initialize RClone drive wrapper."""
        self.remote_name = self.REMOTE_NAME

    @staticmethod
    def _expand_path(path: str) -> str:
        """Safely expand user home directory paths (supports ~ on Termux/Linux)."""
        return os.path.expanduser(path)

    def _build_remote_path(self, path: str = "") -> str:
        """Build full remote path from relative path."""
        base = self.remote_name.rstrip(":")
        if path:
            return f"{base}/{path.lstrip('/')}"
        return f"{base}/"

    def _run_command(
        self, cmd: List[str], capture_output: bool = True
    ) -> Tuple[str, str, int]:
        """
        Execute rclone command via subprocess.

        Args:
            cmd: List of command arguments (including 'rclone')
            capture_output: Whether to capture stdout/stderr

        Returns:
            Tuple of (stdout, stderr, returncode)

        Raises:
            RCloneDriveError: If command fails
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=300,
            )

            if result.returncode != 0 and capture_output:
                raise RCloneDriveError(
                    f"RClone command failed (code {result.returncode}): {result.stderr.strip()}"
                )

            return result.stdout, result.stderr, result.returncode

        except subprocess.TimeoutExpired as e:
            raise RCloneDriveError(f"RClone command timed out: {e}")
        except FileNotFoundError:
            raise RCloneDriveError(
                "RClone not found. Please run: bash install.sh"
            )
        except RCloneDriveError:
            raise
        except Exception as e:
            raise RCloneDriveError(f"Subprocess error: {e}")

    def about(self) -> Dict[str, str]:
        """
        Get storage information about the remote.

        Returns:
            Dictionary with quota and usage info

        Raises:
            RCloneDriveError: If operation fails
        """
        cmd = ["rclone", "about", self.remote_name, "--json"]
        stdout, _, _ = self._run_command(cmd)

        try:
            data = json.loads(stdout)

            def fmt_bytes(n: int) -> str:
                """Format bytes into human-readable string."""
                if n is None:
                    return "N/A"
                for unit in ("B", "KB", "MB", "GB", "TB"):
                    if n < 1024:
                        return f"{n:.2f} {unit}"
                    n /= 1024
                return f"{n:.2f} PB"

            return {
                "total": fmt_bytes(data.get("total")),
                "used": fmt_bytes(data.get("used")),
                "free": fmt_bytes(data.get("free")),
            }
        except (json.JSONDecodeError, TypeError) as e:
            raise RCloneDriveError(f"Failed to parse storage info: {e}")

    def list_files(self, remote_path: str = "") -> List[str]:
        """
        List files in remote directory.

        Args:
            remote_path: Path in remote (relative to remote root)

        Returns:
            List of file/folder names

        Raises:
            RCloneDriveError: If operation fails
        """
        full_path = self._build_remote_path(remote_path)
        cmd = ["rclone", "lsf", full_path]
        stdout, _, _ = self._run_command(cmd)
        return [line.strip() for line in stdout.splitlines() if line.strip()]

    def mkdir(self, remote_path: str) -> None:
        """
        Create directory in remote.

        Args:
            remote_path: Path to create

        Raises:
            RCloneDriveError: If operation fails
        """
        full_path = self._build_remote_path(remote_path)
        cmd = ["rclone", "mkdir", full_path]
        self._run_command(cmd)

    def copy(self, local_path: str, remote_path: str) -> subprocess.Popen:
        """
        Copy file/directory to remote with progress tracking.
        Returns subprocess Popen for real-time output reading.

        Args:
            local_path: Local file or directory path
            remote_path: Destination folder in remote

        Returns:
            Popen object for streaming output

        Raises:
            RCloneDriveError: If paths are invalid or copy cannot start
        """
        # Expand and validate local path
        local_path = self._expand_path(local_path.strip())

        if not os.path.exists(local_path):
            raise RCloneDriveError(f"Local path does not exist: {local_path}")

        full_remote_path = self._build_remote_path(remote_path)

        cmd = [
            "rclone", "copy",
            local_path,
            full_remote_path,
            "--progress",
            "--stats", "1s",
            "--stats-one-line",
        ]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,   # merge stderr → stdout for easier parsing
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            return process
        except FileNotFoundError:
            raise RCloneDriveError("RClone not found. Please run: bash install.sh")
        except Exception as e:
            raise RCloneDriveError(f"Failed to start copy operation: {e}")

    def delete(self, remote_path: str) -> None:
        """
        Delete file/directory from remote.

        Args:
            remote_path: Path to delete

        Raises:
            RCloneDriveError: If operation fails
        """
        full_path = self._build_remote_path(remote_path)
        cmd = ["rclone", "deletefile", full_path]
        try:
            self._run_command(cmd)
        except RCloneDriveError:
            # Fallback: try delete (works for dirs too)
            cmd = ["rclone", "delete", full_path]
            self._run_command(cmd)

    def validate_remote(self) -> bool:
        """
        Validate that remote is configured and accessible.

        Returns:
            True if remote is valid, False otherwise
        """
        try:
            cmd = ["rclone", "listremotes"]
            stdout, _, _ = self._run_command(cmd)
            return self.remote_name in stdout
        except RCloneDriveError:
            return False
