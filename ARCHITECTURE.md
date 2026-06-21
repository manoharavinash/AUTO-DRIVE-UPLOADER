# AUTO DRIVE UPLOADER - Technical Architecture

## System Design Overview

```
┌─────────────────────────────────────────────────────┐
│         upload.py (Main Orchestrator)               │
│  • Interactive CLI menu system                      │
│  • User input handling & validation                 │
│  • Workflow coordination                            │
│  • UI rendering (Cyberpunk theme)                   │
└──────────────┬──────────────────────────────────────┘
               │
               ├─────────────────┬──────────────────┐
               │                 │                  │
    ┌──────────▼───────┐ ┌──────▼─────────┐ ┌─────▼──────────┐
    │   uploader.py    │ │   drive.py     │ │  RClone CLI    │
    │ (Progress Track) │ │  (Subprocess)  │ │  (External)    │
    │                  │ │                │ │                │
    │ • Regex parsing  │ │ • copy()       │ │ rclone copy    │
    │ • Rich progress  │ │ • list_files() │ │ rclone about   │
    │ • Speed/ETA      │ │ • mkdir()      │ │ rclone delete  │
    │ • Error display  │ │ • validate()   │ │ rclone lsf     │
    └──────────────────┘ └────────────────┘ └────────────────┘
```

## Data Flow Architecture

### Upload Workflow

```
User Input (file path)
    ↓
[upload.py] Validate input type (file vs dir)
    ↓
[upload.py] Prompt for destination
    ↓
[upload.py] Show confirmation with size/stats
    ↓
[drive.py] Execute rclone copy subprocess
    ↓
[uploader.py] Stream stdout in real-time
    ↓
[uploader.py] Parse stats with regex
    ↓
[uploader.py] Render progress bars
    ↓
[uploader.py] Display completion summary
```

## Module Dependencies

```
upload.py (Main)
    ├── imports: drive.RCloneDrive
    ├── imports: uploader.RCloneProgressTracker
    ├── imports: rich (UI library)
    └── subprocess.Popen (via drive.py)

drive.py (Backend)
    ├── imports: subprocess
    ├── imports: os
    └── imports: json

uploader.py (Progress)
    ├── imports: subprocess
    ├── imports: re
    ├── imports: rich
    └── imports: typing
```

## Security Architecture

### Path Safety
- All local paths expanded with `os.path.expanduser(path)`
- Tilde expansion: `~` → `/home/user` automatically
- Relative paths preserved and validated

### Type Checking
- File uploads reject directories with type mismatch error
- Directory uploads reject single files with type mismatch error
- Path existence verified before any operation

### Credential Management
- No credentials stored in code
- All auth handled by RClone config files
- OAuth tokens managed by RClone only

### Error Handling
- Try-catch blocks around all subprocess operations
- Custom exception class: `RCloneDriveError`
- User-friendly error messages instead of tracebacks

## Subprocess Architecture

### RClone Commands Used

```
rclone copy <src> <dst> -P --stats-one-line
    Purpose: Upload with progress tracking
    Output: Real-time stats one line at a time

rclone about <remote> --json
    Purpose: Get storage quota info
    Output: JSON with quota, used, free

rclone lsf <remote>
    Purpose: List files in directory
    Output: File names, one per line

rclone mkdir <remote>
    Purpose: Create directory
    Output: None

rclone delete <remote>
    Purpose: Delete file/directory
    Output: None
```

### Output Parsing Strategy

The `uploader.py` uses regex to extract real-time stats:

```python
# Pattern: "Transferred: 123.4 MB Elapsed: 2m45s Speed: 50 MB/s ETA: 1m23s"
STATS_PATTERN = re.compile(
    r'Transferred:\s+([\d.]+)\s*(\w+).*Elapsed:\s+([^,]+).*'
    r'Speed:\s+([\d.]+)\s*(\w+/s).*ETA:\s+(.+?)(?:\s+|$)'
)
```

This extracts:
- Transferred amount & unit
- Elapsed time
- Transfer speed & unit
- Estimated time remaining

## UI Design Specification

### Color Palette
- **Primary Accent**: `bright_cyan` (#00FFFF)
- **Status Success**: `green` (#00FF00)
- **Status Error**: `red` (#FF0000)
- **Status Warning**: `yellow` (#FFFF00)
- **Background**: Terminal default (black)

### Mandatory Watermark
Every dashboard view MUST render this header:
```
┌─────────────────────────────────────────┐
│  🛠️  DESIGNED BY MANOHAR AVINASH  🛠️  │
└─────────────────────────────────────────┘
```

This is implemented as:
```python
Panel(
    Align.center("[bold black]🛠️  DESIGNED BY MANOHAR AVINASH  🛠️[/]"),
    style="on bright_cyan text bold",
    box=None
)
```

### Table Grid System
- Uses `Table.grid()` for responsive layouts
- Padding: `(0, 2)` for horizontal spacing
- Borders only for content panels

## Performance Characteristics

### Memory Usage
- Baseline: ~50 MB Python process
- Per-file overhead: Minimal (only metadata stored)
- Streaming I/O: No buffering of file contents

### CPU Usage
- Idle: <1% CPU
- During upload: 2-5% CPU (mostly regex parsing)
- Progress rendering: <1% CPU

### Network
- Upload speed: Limited by RClone efficiency & network bandwidth
- Progress update frequency: Every ~100 KB transferred
- Supports files up to Google Drive limits (~5 TB)

## Termux-Specific Adaptations

### Environment Detection
```python
if [[ -d /data/data/com.termux ]]; then
    ENV="termux"
fi
```

### Path Handling
- Termux home: `/data/data/com.termux/files/home`
- Expanded via `os.path.expanduser()` automatically
- Storage access: Request permissions or use `/sdcard/`

### Package Management
- Termux uses `apt` (Debian-based)
- Python available as `python` or `python3`
- RClone available from Termux repo

## Error Recovery

### Command Failures
```python
try:
    result = subprocess.run(...)
except subprocess.TimeoutExpired:
    # Handle timeout
except FileNotFoundError:
    # Handle missing rclone
except Exception as e:
    # Handle generic errors
```

### User Interrupts
```python
try:
    while True:
        # main loop
except KeyboardInterrupt:
    console.print("[yellow]Interrupted[/yellow]")
```

### Type Mismatches
```python
if os.path.isdir(local_path) and upload_mode == "file":
    raise RCloneDriveError("Path is directory but file upload selected")
```

## Configuration Files

### install.sh
- Auto-detects Termux vs Linux
- Upgrades apt packages
- Installs Python, RClone, pip packages
- Guides RClone configuration

### start.sh
- Pre-flight validation checks
- Verifies Python, RClone, dependencies
- Checks RClone remote configuration
- Launches application

### .gitignore
- Excludes __pycache__, venv, .vscode
- Protects RClone config files
- Ignores log files and runtime artifacts

## Testing Recommendations

### Unit Tests
- Test path expansion: `os.path.expanduser()`
- Test regex parsing: STATS_PATTERN
- Test type validation: file vs directory

### Integration Tests
- Test RClone subprocess execution
- Test progress tracking with mock output
- Test error handling and recovery

### Manual Testing
- Test on Termux device/emulator
- Test on Linux VM
- Test with various file sizes (10MB, 1GB, 5GB)
- Test with special characters in paths
- Test interrupting with Ctrl+C

## Future Enhancements

- [ ] Drag-and-drop file upload
- [ ] Resume interrupted uploads
- [ ] Download files from Drive
- [ ] Batch upload multiple files
- [ ] Scheduled/automated uploads
- [ ] Upload history & logs
- [ ] Remote folder sync
- [ ] Encryption option
