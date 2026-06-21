 """
Interactive progress tracker for RClone uploads.
Parses real-time rclone output and renders progress bars.
"""

import re
import subprocess
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
