"""
AUTO DRIVE UPLOADER - Main Orchestrator
Interactive CLI for uploading files to Google Drive via RClone.
Cyberpunk/Matrix-inspired UI with real-time progress tracking.
""""""
AUTO DRIVE UPLOADER - Main Orchestrator
Interactive CLI for uploading files to Google Drive via RClone.
Cyberpunk/Matrix-inspired UI with real-time progress tracking.
"""

import os
import sys
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich.text import Text

from drive import RCloneDrive, RCloneDriveError
from uploader import RCloneProgressTracker


class AutoDriveUploader:
    """Main application orchestrator."""

    def __init__(self):
        """Initialize the uploader application."""
        self.console = Console()
        self.drive = RCloneDrive()
        self.progress_tracker = RCloneProgressTracker(self.console)
        self.is_running = True

    # ------------------------------------------------------------------ #
    # UI helpers
    # ------------------------------------------------------------------ #

    def render_header(self) -> Panel:
        """
        Render mandatory branding header panel.
        REQUIRED: Must appear on every dashboard view.

        Returns:
            Rich Panel with watermark
        """
        return Panel(
            Align.center("[bold black]🛠️  DESIGNED BY MANOHAR AVINASH  🛠️[/bold black]"),
            style="bold on bright_cyan",
            box=None,
        )

    def _pause(self) -> None:
        """Wait for user to press Enter before returning to menu."""
        try:
            self.console.print()
            input("  Press Enter to continue...")
        except (EOFError, KeyboardInterrupt):
            pass

    # ------------------------------------------------------------------ #
    # Dashboard
    # ------------------------------------------------------------------ #

    def render_dashboard(self) -> None:
        """Render main dashboard with header and menu."""
        self.console.clear()
        self.console.print(self.render_header())
        self.console.print(
            Align.center("[bold bright_cyan]AUTO DRIVE UPLOADER  v1.0[/bold bright_cyan]")
        )
        self.console.print()

        # Storage info
        try:
            info = self.drive.about()
            grid = Table.grid(padding=(0, 2))
            grid.add_column(style="cyan")
            grid.add_column()
            grid.add_row("Total :", info.get("total", "N/A"))
            grid.add_row("Used  :", info.get("used", "N/A"))
            grid.add_row("Free  :", info.get("free", "N/A"))
            self.console.print(
                Panel(grid, title="[bright_cyan]☁  Google Drive[/bright_cyan]",
                      border_style="bright_cyan")
            )
        except RCloneDriveError:
            self.console.print(
                Panel("[red]Storage info unavailable — check rclone config[/red]",
                      border_style="red")
            )

        self.console.print()

        # Menu
        menu = Table.grid(padding=(0, 2))
        menu.add_column(style="bold bright_cyan", width=3)
        menu.add_column()
        menu.add_row("1", "Upload File")
        menu.add_row("2", "Upload Directory")
        menu.add_row("3", "List Remote Files")
        menu.add_row("4", "Settings")
        menu.add_row("5", "Exit")

        self.console.print(
            Panel(menu, title="[bright_cyan]Main Menu[/bright_cyan]",
                  border_style="bright_cyan")
        )

    # ------------------------------------------------------------------ #
    # Upload File
    # ------------------------------------------------------------------ #

    def upload_file(self) -> None:
        """Interactive single-file upload workflow."""
        self.console.clear()
        self.console.print(self.render_header())
        self.console.print()
        self.console.print("[bold bright_cyan]▸ Upload File[/bold bright_cyan]\n")

        # --- get path ---
        local_path: str = ""
        while True:
            raw = Prompt.ask("  Local file path").strip()
            if not raw:
                continue
            local_path = os.path.expanduser(raw)

            if not os.path.exists(local_path):
                self.console.print("[red]  ✗ Path not found[/red]")
                continue
            if os.path.isdir(local_path):
                self.console.print(
                    "[red]  ✗ That is a directory — use option 2 to upload directories[/red]"
                )
                continue
            break

        # --- destination ---
        remote_path = Prompt.ask(
            "  Destination folder in Drive (blank = root)", default=""
        ).strip()

        # --- confirm ---
        size_mb = os.path.getsize(local_path) / (1024 ** 2)
        self.console.print()
        self.console.print(f"  [cyan]File :[/cyan] {os.path.basename(local_path)}")
        self.console.print(f"  [cyan]Size :[/cyan] {size_mb:.2f} MB")
        self.console.print(f"  [cyan]To   :[/cyan] {remote_path or '(root)'}")
        self.console.print()

        if not Confirm.ask("  [bright_cyan]Proceed with upload?[/bright_cyan]", default=True):
            self.console.print("[yellow]  Upload cancelled[/yellow]")
            self._pause()
            return

        # --- execute ---
        self.console.print()
        try:
            process = self.drive.copy(local_path, remote_path)
            success = self.progress_tracker.stream_progress(
                process, f"Uploading {os.path.basename(local_path)}"
            )
            self.progress_tracker.display_transfer_summary(
                success, os.path.basename(local_path)
            )
        except RCloneDriveError as e:
            self.console.print(f"[red]  ✗ Upload failed: {e}[/red]")

        self._pause()

    # ------------------------------------------------------------------ #
    # Upload Directory
    # ------------------------------------------------------------------ #

    def upload_directory(self) -> None:
        """Interactive directory upload workflow."""
        self.console.clear()
        self.console.print(self.render_header())
        self.console.print()
        self.console.print("[bold bright_cyan]▸ Upload Directory[/bold bright_cyan]\n")

        # --- get path ---
        local_path: str = ""
        while True:
            raw = Prompt.ask("  Local directory path").strip()
            if not raw:
                continue
            local_path = os.path.expanduser(raw)

            if not os.path.exists(local_path):
                self.console.print("[red]  ✗ Path not found[/red]")
                continue
            if not os.path.isdir(local_path):
                self.console.print(
                    "[red]  ✗ That is a file — use option 1 to upload a single file[/red]"
                )
                continue
            break

        # --- destination ---
        default_dest = os.path.basename(local_path.rstrip("/\\"))
        remote_path = Prompt.ask(
            "  Destination folder in Drive", default=default_dest
        ).strip()

        # --- stats ---
        file_count = 0
        total_bytes = 0
        for dirpath, _, filenames in os.walk(local_path):
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                try:
                    total_bytes += os.path.getsize(fp)
                    file_count += 1
                except OSError:
                    pass
        total_mb = total_bytes / (1024 ** 2)

        self.console.print()
        self.console.print(f"  [cyan]Directory :[/cyan] {os.path.basename(local_path)}")
        self.console.print(f"  [cyan]Files     :[/cyan] {file_count}")
        self.console.print(f"  [cyan]Total size:[/cyan] {total_mb:.2f} MB")
        self.console.print(f"  [cyan]To        :[/cyan] {remote_path}")
        self.console.print()

        if not Confirm.ask("  [bright_cyan]Proceed with upload?[/bright_cyan]", default=True):
            self.console.print("[yellow]  Upload cancelled[/yellow]")
            self._pause()
            return

        # --- execute ---
        self.console.print()
        try:
            process = self.drive.copy(local_path, remote_path)
            success = self.progress_tracker.stream_progress(
                process, f"Uploading {os.path.basename(local_path)}"
            )
            self.progress_tracker.display_transfer_summary(
                success, os.path.basename(local_path)
            )
        except RCloneDriveError as e:
            self.console.print(f"[red]  ✗ Upload failed: {e}[/red]")

        self._pause()

    # ------------------------------------------------------------------ #
    # List Remote Files
    # ------------------------------------------------------------------ #

    def list_remote_files(self) -> None:
        """Display files in a remote directory."""
        self.console.clear()
        self.console.print(self.render_header())
        self.console.print()
        self.console.print("[bold bright_cyan]▸ Remote Files[/bold bright_cyan]\n")

        remote_path = Prompt.ask(
            "  Remote folder path (blank = root)", default=""
        ).strip()

        self.console.print()
        try:
            files = self.drive.list_files(remote_path)
            if not files:
                self.console.print("[yellow]  (no files found)[/yellow]")
            else:
                tbl = Table(
                    title=f"[bright_cyan]{remote_path or '(root)'}[/bright_cyan]",
                    border_style="bright_cyan",
                )
                tbl.add_column("#", style="dim", width=4)
                tbl.add_column("Name", style="cyan")
                for i, name in enumerate(files, 1):
                    tbl.add_row(str(i), name)
                self.console.print(tbl)
        except RCloneDriveError as e:
            self.console.print(f"[red]  ✗ Failed to list files: {e}[/red]")

        self._pause()

    # ------------------------------------------------------------------ #
    # Settings
    # ------------------------------------------------------------------ #

    def show_settings(self) -> None:
        """Display settings and connection status."""
        self.console.clear()
        self.console.print(self.render_header())
        self.console.print()
        self.console.print("[bold bright_cyan]▸ Settings[/bold bright_cyan]\n")

        is_valid = self.drive.validate_remote()
        remote_status = (
            "[green]✓ Connected[/green]"
            if is_valid
            else "[red]✗ Not configured[/red]"
        )

        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="cyan", width=12)
        grid.add_column()
        grid.add_row("Remote :", self.drive.remote_name)
        grid.add_row("Status :", remote_status)
        grid.add_row("Version:", "1.0.0")

        self.console.print(
            Panel(grid, title="[bright_cyan]App Settings[/bright_cyan]",
                  border_style="bright_cyan")
        )

        if not is_valid:
            self.console.print()
            self.console.print(
                "[yellow]  ⚠  Remote not found.\n"
                "  Run:  rclone config\n"
                "  Name the remote exactly:  google auto photo[/yellow]"
            )

        self._pause()

    # ------------------------------------------------------------------ #
    # Menu routing & main loop
    # ------------------------------------------------------------------ #

    def handle_menu_choice(self, choice: str) -> None:
        """Route user selection to the correct handler."""
        choice = choice.strip()
        if choice == "1":
            self.upload_file()
        elif choice == "2":
            self.upload_directory()
        elif choice == "3":
            self.list_remote_files()
        elif choice == "4":
            self.show_settings()
        elif choice == "5":
            self.is_running = False
        else:
            self.console.print("[red]  Invalid choice — enter 1 to 5[/red]")
            self._pause()

    def run(self) -> None:
        """Main application loop."""
        try:
            while self.is_running:
                self.render_dashboard()
                choice = Prompt.ask("\n[bright_cyan]  Select option[/bright_cyan]")
                self.handle_menu_choice(choice)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]  Goodbye![/yellow]\n")
        except Exception as e:
            self.console.print(f"\n[red]  Fatal error: {e}[/red]\n")
            sys.exit(1)


def main() -> None:
    """Entry point."""
    app = AutoDriveUploader()
    app.run()


if __name__ == "__main__":
    main()


import os
import sys
from typing import Optional, List
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.prompt import Prompt, Confirm

from drive import RCloneDrive, RCloneDriveError
from uploader import RCloneProgressTracker


class AutoDriveUploader:
    """Main application orchestrator."""
    
    def __init__(self):
        """Initialize the uploader application."""
        self.console = Console()
        self.drive = RCloneDrive()
        self.progress_tracker = RCloneProgressTracker(self.console)
        self.is_running = True
    
    def render_header(self) -> Panel:
        """
        Render mandatory branding header panel.
        REQUIRED: Must appear on every dashboard view.
        
        Returns:
            Rich Panel with watermark
        """
        return Panel(
            Align.center("[bold black]🛠️  DESIGNED BY MANOHAR AVINASH  🛠️[/]"),
            style="bold on bright_cyan",
            box=None
        )
    
    def render_dashboard(self) -> None:
        """Render main dashboard with header."""
        self.console.clear()
        
        # Render mandatory header
        self.console.print(self.render_header())
        
        # Title
        title = Align.center("[bold bright_cyan]AUTO DRIVE UPLOADER[/bold bright_cyan]")
        self.console.print(title)
        self.console.print()
        
        # Get storage info
        try:
            info = self.drive.about()
            status_table = Table(title="[bright_cyan]Storage Status[/]", show_header=False)
            status_table.add_row("[cyan]Total Storage[/]", info.get("total", "N/A"))
            status_table.add_row("[cyan]Used Space[/]", info.get("used", "N/A"))
            status_table.add_row("[cyan]Free Space[/]", info.get("free", "N/A"))
            self.console.print(status_table)
        except RCloneDriveError as e:
            self.console.print(f"[red]✗ Storage info unavailable: {e}[/red]")
        
        self.console.print()
        
        # Menu options
        menu_table = Table.grid(padding=(0, 2))
        menu_table.add_row("[bright_cyan]1[/]", "Upload File")
        menu_table.add_row("[bright_cyan]2[/]", "Upload Directory")
        menu_table.add_row("[bright_cyan]3[/]", "List Remote Files")
        menu_table.add_row("[bright_cyan]4[/]", "Settings")
        menu_table.add_row("[bright_cyan]5[/]", "Exit")
        
        menu_panel = Panel(
            menu_table,
            title="[bright_cyan]Main Menu[/]",
            border_style="bright_cyan"
        )
        self.console.print(menu_panel)
    
    def upload_file(self) -> None:
        """Interactive file upload workflow."""
        self.console.clear()
        self.console.print(self.render_header())
        self.console.print()
        
        self.console.print("[bold bright_cyan]Upload File[/bold bright_cyan]\n")
        
        # Get local file path
        while True:
            local_path = Prompt.ask("Enter file path")
            local_path = os.path.expanduser(local_path)
            
            if not os.path.exists(local_path):
                self.console.print("[red]✗ File not found[/red]")
                continue
            
            if not os.path.isfile(local_path):
                self.console.print("[red]✗ Path is not a file (type mismatch)[/red]")
                continue
            
            break
        
        # Get remote destination
        remote_path = Prompt.ask(
            "Enter destination folder in Drive",
            default=""
        )
        
        # Confirm upload
        file_size = os.path.getsize(local_path) / (1024**2)  # Convert to MB
        self.console.print()
        self.console.print(f"[cyan]File:[/] {os.path.basename(local_path)}")
        self.console.print(f"[cyan]Size:[/] {file_size:.2f} MB")
        self.console.print(f"[cyan]Destination:[/] {remote_path or '(root)'}")
        self.console.print()
        
        if not Confirm.ask("[bright_cyan]Proceed with upload?[/]"):
            self.console.print("[yellow]Upload cancelled[/yellow]")
            return
        
        # Execute upload
        self.console.print()
        try:
            process = self.drive.copy(local_path, remote_path)
            success = self.progress_tracker.stream_progress(
                process,
                f"Uploading {os.path.basename(local_path)}"
            )
            
            if success:
                self.progress_tracker.display_transfer_summary(True, os.path.basename(local_path))
            else:
                self.progress_tracker.display_transfer_summary(False, os.path.basename(local_path))
                
        except RCloneDriveError as e:
            self.console.print(f"[red]✗ Upload failed: {e}[/red]")
        
        input("\n[cyan]Press Enter to continue...[/]")
    
    def upload_directory(self) -> None:
        """Interactive directory upload workflow."""
        self.console.clear()
        self.console.print(self.render_header())
        self.console.print()
        
        self.console.print("[bold bright_cyan]Upload Directory[/bold bright_cyan]\n")
        
        # Get local directory path
        while True:
            local_path = Prompt.ask("Enter directory path")
            local_path = os.path.expanduser(local_path)
            
            if not os.path.exists(local_path):
                self.console.print("[red]✗ Directory not found[/red]")
                continue
            
            if not os.path.isdir(local_path):
                self.console.print("[red]✗ Path is not a directory (type mismatch)[/red]")
                continue
            
            break
        
        # Get remote destination
        remote_path = Prompt.ask(
            "Enter destination folder in Drive",
            default=os.path.basename(local_path)
        )
        
        # Count files in directory
        file_count = sum([len(files) for _, _, files in os.walk(local_path)])
        total_size = sum([
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, _, filenames in os.walk(local_path)
            for filename in filenames
        ]) / (1024**2)  # Convert to MB
        
        self.console.print()
        self.console.print(f"[cyan]Directory:[/] {os.path.basename(local_path)}")
        self.console.print(f"[cyan]Files:[/] {file_count}")
        self.console.print(f"[cyan]Total Size:[/] {total_size:.2f} MB")
        self.console.print(f"[cyan]Destination:[/] {remote_path}")
        self.console.print()
        
        if not Confirm.ask("[bright_cyan]Proceed with upload?[/]"):
            self.console.print("[yellow]Upload cancelled[/yellow]")
            return
        
        # Execute upload
        self.console.print()
        try:
            process = self.drive.copy(local_path, remote_path)
            success = self.progress_tracker.stream_progress(
                process,
                f"Uploading {os.path.basename(local_path)}"
            )
            
            if success:
                self.progress_tracker.display_transfer_summary(True, os.path.basename(local_path))
            else:
                self.progress_tracker.display_transfer_summary(False, os.path.basename(local_path))
                
        except RCloneDriveError as e:
            self.console.print(f"[red]✗ Upload failed: {e}[/red]")
        
        input("\n[cyan]Press Enter to continue...[/]")
    
    def list_remote_files(self) -> None:
        """Display files in remote directory."""
        self.console.clear()
        self.console.print(self.render_header())
        self.console.print()
        
        self.console.print("[bold bright_cyan]Remote Files[/bold bright_cyan]\n")
        
        # Get remote path
        remote_path = Prompt.ask(
            "Enter remote folder path",
            default=""
        )
        
        try:
            files = self.drive.list_files(remote_path)
            
            if not files:
                self.console.print("[yellow]No files found[/yellow]")
            else:
                files_table = Table(title=f"[bright_cyan]{remote_path or '(root)'}[/]")
                files_table.add_column("Filename", style="cyan")
                
                for filename in files:
                    files_table.add_row(filename)
                
                self.console.print(files_table)
        except RCloneDriveError as e:
            self.console.print(f"[red]✗ Failed to list files: {e}[/red]")
        
        input("\n[cyan]Press Enter to continue...[/]")
    
    def show_settings(self) -> None:
        """Display settings menu."""
        self.console.clear()
        self.console.print(self.render_header())
        self.console.print()
        
        self.console.print("[bold bright_cyan]Settings[/bold bright_cyan]\n")
        
        # Check remote connection
        is_valid = self.drive.validate_remote()
        remote_status = "[green]✓ Connected[/]" if is_valid else "[red]✗ Not configured[/]"
        
        settings_table = Table.grid(padding=(0, 2))
        settings_table.add_row("[cyan]Remote:[/]", self.drive.remote_name)
        settings_table.add_row("[cyan]Status:[/]", remote_status)
        settings_table.add_row("[cyan]Version:[/]", "1.0.0")
        
        settings_panel = Panel(
            settings_table,
            title="[bright_cyan]Application Settings[/]",
            border_style="bright_cyan"
        )
        self.console.print(settings_panel)
        self.console.print()
        
        if not is_valid:
            self.console.print(
                "[yellow]⚠ Remote 'google auto photo:' not configured.\n"
                "Please set up RClone with: rclone config[/yellow]"
            )
        
        input("\n[cyan]Press Enter to continue...[/]")
    
    def handle_menu_choice(self, choice: str) -> None:
        """Handle user menu selection."""
        if choice == "1":
            self.upload_file()
        elif choice == "2":
            self.upload_directory()
        elif choice == "3":
            self.list_remote_files()
        elif choice == "4":
            self.show_settings()
        elif choice == "5":
            self.is_running = False
        else:
            self.console.print("[red]Invalid choice[/red]")
    
    def run(self) -> None:
        """Main application loop."""
        try:
            while self.is_running:
                self.render_dashboard()
                choice = Prompt.ask("[bright_cyan]Select option[/]")
                self.handle_menu_choice(choice)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Application interrupted[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Fatal error: {e}[/red]")
            sys.exit(1)


def main():
    """Entry point."""
    app = AutoDriveUploader()
    app.run()


if __name__ == "__main__":
    main()
