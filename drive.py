"""
Low-level RClone wrapper for subprocess operations.
Handles all cloud operations via rclone subprocess pipes.
"""

import subprocess
import os
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
        """Safely expand user home directory paths."""
        return os.path.expanduser(path)
    
    def _run_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[str, str, int]:
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
                timeout=300
            )
            
            if result.returncode != 0 and capture_output:
                raise RCloneDriveError(
                    f"RClone command failed with code {result.returncode}: {result.stderr}"
                )
            
            return result.stdout, result.stderr, result.returncode
            
        except subprocess.TimeoutExpired as e:
            raise RCloneDriveError(f"RClone command timed out: {e}")
        except FileNotFoundError:
            raise RCloneDriveError("RClone not found. Please install rclone.")
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
            import json
            data = json.loads(stdout)
            return {
                "total": str(data.get("Quota", "N/A")),
                "used": str(data.get("Used", "N/A")),
                "free": str(data.get("Free", "N/A"))
            }
        except Exception as e:
            raise RCloneDriveError(f"Failed to parse storage info: {e}")
    
    def list_files(self, remote_path: str = "") -> List[str]:
        """
        List files in remote directory.
        
        Args:
            remote_path: Path in remote (relative to remote root)
            
        Returns:
            List of file names
            
        Raises:
            RCloneDriveError: If operation fails
        """
        full_path = f"{self.remote_name.rstrip(':')}/{remote_path}".rstrip('/')
        cmd = ["rclone", "lsf", full_path]
        stdout, _, _ = self._run_command(cmd)
        return [line.strip() for line in stdout.split('\n') if line.strip()]
    
    def mkdir(self, remote_path: str) -> None:
        """
        Create directory in remote.
        
        Args:
            remote_path: Path to create
            
        Raises:
            RCloneDriveError: If operation fails
        """
        full_path = f"{self.remote_name.rstrip(':')}/{remote_path}".rstrip('/')
        cmd = ["rclone", "mkdir", full_path]
        self._run_command(cmd)
    
    def copy(self, local_path: str, remote_path: str) -> subprocess.Popen:
        """
        Copy file/directory to remote with progress tracking.
        Returns subprocess for real-time output reading.
        
        Args:
            local_path: Local file or directory path
            remote_path: Destination in remote
            
        Returns:
            Popen object for streaming output
            
        Raises:
            RCloneDriveError: If paths are invalid
        """
        # Expand local path
        local_path = self._expand_path(local_path)
        
        # Validate input type safety
        if not os.path.exists(local_path):
            raise RCloneDriveError(f"Local path does not exist: {local_path}")
        
        # Build destination
        full_remote_path = f"{self.remote_name.rstrip(':')}/{remote_path}".rstrip('/')
        
        # Build copy command with progress
        cmd = [
            "rclone", "copy",
            local_path,
            full_remote_path,
            "-P",
            "--stats-one-line"
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            return process
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
        full_path = f"{self.remote_name.rstrip(':')}/{remote_path}".rstrip('/')
        cmd = ["rclone", "delete", full_path]
        self._run_command(cmd)
    
    def validate_remote(self) -> bool:
        """
        Validate that remote is configured and accessible.
        
        Returns:
            True if remote is valid, False otherwise
        """
        try:
            self.about()
            return True
        except RCloneDriveError:
            return False
