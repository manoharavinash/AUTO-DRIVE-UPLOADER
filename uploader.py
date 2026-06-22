 """
Interactive progress tracker for RClone uploads.
Parses real-time rclone output and renders progress bars.
"""

import re
import subprocess"""
Interactive progress tracker for RClone uploads.
Parses real-time rclone output and renders progress bars.
"""

import re
import subprocess
from typing import Optional, Tuple

from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    SpinnerColumn,
    TaskProgressColumn,
)
from rich.console import Console


class RCloneProgressTracker:
    """Track and display RClone upload progress in real-time."""

    # Matches lines like:
    # Transferred:   12.345 MiB / 100 MiB, 12%, 1.23 MiB/s, ETA 1m30s
    STATS_PATTERN = re.compile(
        r"Transferred:\s+[\d.]+\s*\S+\s*/\s*([\d.]+\s*\S+),\s*(\d+)%,\s*([\d.]+\s*\S+/s),\s*ETA\s+(\S+)"
    )

    # Fallback: one-line stats format
    # Transferred:   12 MiB   Elapsed time:  5s  Speed: 2.4 MiB/s  ETA: 1m
    STATS_PATTERN2 = re.compile(
        r"Transferred:\s+([\d.]+\s*\S+).*?Speed:\s+([\d.]+\s*\S+).*?ETA:\s+(\S+)",
        re.IGNORECASE,
    )

    # Percentage standalone
    PERCENT_PATTERN = re.compile(r"\b(\d{1,3})%")

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize progress tracker.

        Args:
            console: Optional Rich console for output
        """
        self.console = console or Console()
        self.transferred = "0 B"
        self.total = "?"
        self.speed = "0 B/s"
        self.eta = "Calculating..."
        self.last_pct = 0

    def _parse_line(self, line: str) -> Optional[Tuple[str, int, str, str]]:
        """
        Parse a rclone output line for progress stats.

        Returns:
            (total, percent, speed, eta) or None
        """
        m = self.STATS_PATTERN.search(line)
        if m:
            total, pct, speed, eta = m.group(1), int(m.group(2)), m.group(3), m.group(4)
            return total, pct, speed, eta

        # Try fallback pattern
        m2 = self.STATS_PATTERN2.search(line)
        pct_m = self.PERCENT_PATTERN.search(line)
        if m2:
            transferred = m2.group(1)
            speed = m2.group(2)
            eta = m2.group(3)
            pct = int(pct_m.group(1)) if pct_m else self.last_pct
            self.transferred = transferred
            return "?", pct, speed, eta

        return None

    def stream_progress(
        self, process: subprocess.Popen, task_name: str = "Uploading"
    ) -> bool:
        """
        Stream progress from rclone subprocess.

        Args:
            process: Popen object from drive.copy()
            task_name: Display name for the task

        Returns:
            True if successful, False if failed
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[cyan]{task.fields[speed]}[/cyan]"),
            TextColumn("ETA [yellow]{task.fields[eta]}[/yellow]"),
            console=self.console,
            transient=False,
        ) as progress:

            task_id = progress.add_task(
                f"[bright_cyan]{task_name}[/bright_cyan]",
                total=100,
                speed="--",
                eta="--",
            )

            try:
                for line in process.stdout:
                    line = line.rstrip()
                    if not line:
                        continue

                    parsed = self._parse_line(line)
                    if parsed:
                        total, pct, speed, eta = parsed
                        self.total = total
                        self.speed = speed
                        self.eta = eta
                        self.last_pct = pct
                        progress.update(
                            task_id,
                            completed=pct,
                            speed=speed,
                            eta=eta,
                        )

                    # Surface errors immediately
                    low = line.lower()
                    if "error" in low or "failed" in low:
                        self.console.print(f"[red]{line}[/red]")

                returncode = process.wait()

                if returncode == 0:
                    progress.update(task_id, completed=100, speed="Done", eta="0s")
                    self.console.print(
                        f"\n[bold green]✓ {task_name} completed successfully![/bold green]"
                    )
                    return True
                else:
                    self.console.print(f"\n[bold red]✗ {task_name} failed (exit {returncode})[/bold red]")
                    return False

            except KeyboardInterrupt:
                process.terminate()
                self.console.print("\n[yellow]⚠ Upload interrupted by user[/yellow]")
                return False
            except Exception as e:
                try:
                    process.terminate()
                except Exception:
                    pass
                self.console.print(f"\n[red]Progress tracking error: {e}[/red]")
                return False

    def display_transfer_summary(self, success: bool, filename: str = "") -> None:
        """
        Display summary of transfer operation.

        Args:
            success: Whether transfer was successful
            filename: Optional filename that was transferred
        """
        status = (
            "[bold green]✓  SUCCESS[/bold green]"
            if success
            else "[bold red]✗  FAILED[/bold red]"
        )

        self.console.print()
        self.console.rule("[bright_cyan]Transfer Summary[/bright_cyan]")
        if filename:
            self.console.print(f"  [cyan]File   :[/cyan] {filename}")
        self.console.print(f"  [cyan]Size   :[/cyan] {self.transferred}")
        self.console.print(f"  [cyan]Speed  :[/cyan] {self.speed}")
        self.console.print(f"  [cyan]Status :[/cyan] {status}")
        self.console.rule("[bright_cyan]─[/bright_cyan]")
        self.console.print()

from typing import Optional, Tuple
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.console import Console


class RCloneProgressTracker:
    """Track and display RClone upload progress in real-time."""
    
    # Regex patterns for parsing rclone output
    STATS_PATTERN = re.compile(
        r'Transferred:\s+([\d.]+)\s*(\w+).*Elapsed:\s+([^,]+).*Speed:\s+([\d.]+)\s*(\w+/s).*ETA:\s+(.+?)(?:\s+|$)'
    )
    
    TRANSFER_PATTERN = re.compile(
        r'Copying\s+(.+?)\s+to\s+(.+?).*?(\d+)%'
    )
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize progress tracker.
        
        Args:
            console: Optional Rich console for output
        """
        self.console = console or Console()
        self.total_size = 0
        self.transferred = 0
        self.speed = "0 MB/s"
        self.eta = "Calculating..."
    
    def _parse_stats_line(self, line: str) -> Optional[Tuple[str, str, str, str]]:
        """
        Parse rclone stats line.
        
        Args:
            line: Single line from rclone output
            
        Returns:
            Tuple of (transferred, elapsed, speed, eta) or None if no match
        """
        match = self.STATS_PATTERN.search(line)
        if match:
            return match.group(1, 3, 4, 6)
        return None
    
    def _convert_size(self, size_str: str, unit: str) -> float:
        """Convert size with unit to bytes."""
        units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
        return float(size_str) * units.get(unit, 1)
    
    def stream_progress(self, process: subprocess.Popen, task_name: str = "Uploading") -> bool:
        """
        Stream progress from rclone subprocess.
        
        Args:
            process: Subprocess Popen object from rclone copy
            task_name: Display name for the task
            
        Returns:
            True if successful, False if failed
        """
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            transient=True
        ) as progress:
            
            # Create task (we'll update manually as we parse output)
            task_id = progress.add_task(
                f"[cyan]{task_name}[/cyan]",
                total=100
            )
            
            last_percentage = 0
            
            try:
                while True:
                    # Read line from stdout
                    line = process.stdout.readline()
                    if not line:
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Log the raw line for debugging
                    # self.console.log(line, style="dim")
                    
                    # Try to parse stats
                    stats = self._parse_stats_line(line)
                    if stats:
                        transferred, elapsed, speed, eta = stats
                        self.transferred = transferred
                        self.speed = speed
                        self.eta = eta
                        
                        # Try to extract percentage if available in line
                        if '%' in line:
                            pct_match = re.search(r'(\d+)%', line)
                            if pct_match:
                                pct = int(pct_match.group(1))
                                if pct > last_percentage:
                                    progress.update(task_id, completed=pct)
                                    last_percentage = pct
                    
                    # Print any error messages
                    if "error" in line.lower():
                        self.console.print(f"[red]Error: {line}[/red]")
                
                # Wait for process to finish
                returncode = process.wait()
                
                if returncode == 0:
                    progress.update(task_id, completed=100)
                    self.console.print(f"[green]✓ {task_name} completed successfully[/green]")
                    return True
                else:
                    stderr = process.stderr.read()
                    self.console.print(f"[red]✗ {task_name} failed[/red]")
                    if stderr:
                        self.console.print(f"[red]{stderr}[/red]")
                    return False
                    
            except KeyboardInterrupt:
                process.terminate()
                self.console.print("[yellow]Upload interrupted by user[/yellow]")
                return False
            except Exception as e:
                process.terminate()
                self.console.print(f"[red]Progress tracking error: {e}[/red]")
                return False
    
    def display_transfer_summary(self, success: bool, filename: str = "") -> None:
        """
        Display summary of transfer operation.
        
        Args:
            success: Whether transfer was successful
            filename: Optional filename that was transferred
        """
        status = "[green]✓ Success[/green]" if success else "[red]✗ Failed[/red]"
        
        summary_lines = [
            f"Transfer: {filename}" if filename else "Transfer Complete",
            f"Size: {self.transferred}",
            f"Speed: {self.speed}",
            f"Status: {status}"
        ]
        
        self.console.print("\n[cyan]─" * 40 + "[/cyan]")
        for line in summary_lines:
            self.console.print(line)
        self.console.print("[cyan]─" * 40 + "[/cyan]\n")
