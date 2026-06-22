# AUTO DRIVE UPLOADER

A Cyberpunk-themed CLI automation tool for uploading files to Google Drive via RClone.  
Designed for **Termux (Android)** and **Linux** environments with real-time progress tracking and an interactive menu system.

---

## 🎯 Features

- **Real-time Progress Tracking** — Live progress bars with speed, percentage, and ETA
- **File & Directory Upload** — Upload single files or entire directory trees
- **Storage Management** — View quota, used space, and free space (human-readable: GB/MB)
- **Remote File Listing** — Browse uploaded files in Google Drive with numbered index
- **Type-Safe Inputs** — Validates file vs. directory before any operation; clear error messages
- **Path Safety** — All `~` paths auto-expanded via `os.path.expanduser()`
- **Termux Compatible** — Fully optimized for Android terminal; auto-detects `python` vs `python3`
- **Cyberpunk UI** — Matrix-inspired interface with `bright_cyan` Rich terminal styling
- **Graceful Error Handling** — Custom `RCloneDriveError` with user-friendly messages
- **Keyboard Interrupt Safe** — Ctrl+C cancels cleanly without crashing

---

## 📋 Requirements

- **Python 3.7+**
- **RClone** — Cloud storage CLI tool
- **Git** — For cloning the repository
- **rich** (>=13.0.0) — Terminal UI library *(installed automatically)*

---

## 🚀 Installation

### Quick Setup (Automated — Recommended)

```bash
git clone https://github.com/manoharavinash/AUTO-DRIVE-UPLOADER.git
cd AUTO-DRIVE-UPLOADER
bash install.sh
```

The `install.sh` script will automatically:
1. Detect your environment (Termux or Linux)
2. Update the package manager (`apt`)
3. Install Python, git, and curl
4. Install RClone (if not already present)
5. Install Python packages from `requirements.txt`
6. Guide you to configure the RClone remote

### Manual Setup

```bash
# 1. Install system dependencies
apt update && apt upgrade -y
apt install -y python3 python3-pip rclone git curl

# 2. Install Python packages
pip install -r requirements.txt

# 3. Configure RClone
rclone config
```

> **Termux note:** Use `python` instead of `python3` if `python3` is not found.  
> The scripts detect this automatically.

---

## ⚙️ RClone Configuration

After installation, configure your Google Drive remote:

```bash
rclone config
```

Follow the prompts to:
1. Choose `n` → New remote
2. Name it **exactly**: `google auto photo`
3. Select **Google Drive** as the type
4. Complete OAuth authentication in your browser

Verify the remote is set up:
```bash
rclone listremotes
# Expected output: google auto photo:
```

---

## 📁 Project Structure

```
AUTO-DRIVE-UPLOADER/
├── requirements.txt     # Python dependencies (rich only)
├── install.sh           # Automated setup (Termux + Linux)
├── start.sh             # Pre-flight checks + app launcher
├── drive.py             # Low-level RClone subprocess wrapper
├── uploader.py          # Real-time progress tracker & parser
├── upload.py            # Main orchestrator & Cyberpunk UI
└── README.md            # This file
```

### Module Breakdown

#### `drive.py` — RClone Wrapper
- Low-level subprocess interface to RClone
- `_build_remote_path()` — clean, consistent path construction (no slash bugs)
- `about()` — returns human-readable storage sizes (GB/MB/KB, not raw bytes)
- `copy()` — uses `--progress --stats 1s --stats-one-line` for reliable stream output
- `validate_remote()` — uses `rclone listremotes` (lightweight, always works)
- `delete()` — tries `deletefile` first, falls back to `delete` for directories
- Custom exception: `RCloneDriveError`

#### `uploader.py` — Progress Tracker
- Dual regex patterns — handles both rclone output formats automatically
- `stderr` merged into `stdout` — no output is lost
- Rich progress bar: spinner + bar + percentage + speed + ETA
- Clean transfer summary after each upload
- Safe Ctrl+C handling — terminates subprocess gracefully

#### `upload.py` — Main Orchestrator
- Interactive CLI menu (options 1–5)
- All user input `.strip()`ped to prevent whitespace path errors
- `_pause()` helper — correctly uses `input()` without printing raw Rich markup
- File/directory type mismatch errors shown clearly before any network call
- Mandatory watermark header on every screen

---

## 🎮 Usage

### Launch

```bash
bash start.sh
# or
python3 upload.py
# or (Termux)
python upload.py
```

### Main Menu

```
┌─────────────────────────────┐
│  1  Upload File             │
│  2  Upload Directory        │
│  3  List Remote Files       │
│  4  Settings                │
│  5  Exit                    │
└─────────────────────────────┘
```

### Example: Upload a File

```
Select option: 1
Local file path: ~/documents/report.pdf
Destination folder in Drive: Reports

  File : report.pdf
  Size : 2.45 MB
  To   : Reports

Proceed with upload? [Y/n]: Y

⠸ Uploading report.pdf ████████░░  78%  1.2 MB/s  ETA 3s
✓ Uploading report.pdf completed successfully!

  Transfer Summary
  File   : report.pdf
  Size   : 2.45 MB
  Speed  : 1.2 MB/s
  Status : ✓  SUCCESS
```

### Example: Upload a Directory

```
Select option: 2
Local directory path: ~/photos/vacation
Destination folder in Drive: vacation

  Directory  : vacation
  Files      : 47
  Total size : 312.80 MB
  To         : vacation

Proceed with upload? [Y/n]: Y
```

---

## 🎨 UI Design

The application uses a **Cyberpunk/Matrix aesthetic**:

| Element | Style |
|---|---|
| Accent color | `bright_cyan` |
| Success | `bold green` |
| Error | `bold red` |
| Warning | `yellow` |
| Progress bar | `bright_cyan` with spinner |

**Mandatory watermark** — appears on every screen:
```
🛠️  DESIGNED BY MANOHAR AVINASH  🛠️
```

---

## 🔒 Security & Safety

- **Type checking** — file upload rejects directories; directory upload rejects files
- **Path safety** — `os.path.expanduser()` on all user-supplied paths
- **No credentials in code** — all auth handled by RClone config files
- **Subprocess timeout** — 300s max per command; prevents hangs
- **Error isolation** — `RCloneDriveError` wraps all subprocess failures cleanly

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `RClone not found` | `bash install.sh` |
| `Remote not configured` | `rclone config` → name it `google auto photo` |
| `Permission denied on install.sh` | `chmod +x install.sh && bash install.sh` |
| `Module not found: rich` | `pip install rich` |
| `python3: command not found` (Termux) | Use `python upload.py` instead |
| Upload fails silently | Check internet; run `rclone about "google auto photo:"` to test auth |
| Storage shows N/A | Re-authenticate: `rclone config reconnect "google auto photo:"` |

---

## 📊 Performance

- **Memory** — ~50 MB baseline Python process
- **CPU** — <1% idle, 2–5% during upload (regex parsing)
- **Upload speed** — limited by network bandwidth and RClone efficiency
- **Max file size** — up to Google Drive limits (~5 TB)
- **Progress refresh** — every 1 second (configurable via `--stats` flag)

---

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- Type hints on all functions
- Cyberpunk aesthetic is maintained (`bright_cyan` accent)
- Mandatory watermark preserved on all views
- Tested on both Termux and Linux
- `os.path.expanduser()` used for all user paths

---

## 📄 License

MIT License — see LICENSE file for details.

---

## 👨‍💻 Author

**Manohar Avinash**

- GitHub: [@manoharavinash](https://github.com/manoharavinash)
- Design Philosophy: Cyberpunk/Matrix-inspired automation tools

---

## 🔗 References

- [RClone Documentation](https://rclone.org/)
- [Rich Library Documentation](https://rich.readthedocs.io/)
- [Python subprocess module](https://docs.python.org/3/library/subprocess.html)

---

*Version 1.0.0 — Updated June 2026*
