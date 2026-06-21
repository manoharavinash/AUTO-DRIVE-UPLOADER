# AUTO DRIVE UPLOADER

A Cyberpunk-themed CLI automation tool for uploading files to Google Drive via RClone. Designed for Termux and Linux environments with real-time progress tracking and an interactive menu system.

---

## 🎯 Features

- **Real-time Progress Tracking**: Live progress bars with speed and ETA
- **File & Directory Upload**: Upload single files or entire directory trees
- **Storage Management**: View quota, usage, and free space
- **Remote File Listing**: Browse uploaded files in Google Drive
- **Type-Safe Inputs**: Validates file vs. directory paths before operations
- **Termux Compatible**: Fully optimized for Android terminal environments
- **Cyberpunk UI**: Matrix-inspired interface with rich terminal styling

---

## 📋 Requirements

- **Python 3.7+**
- **RClone**: Cloud storage tool
- **Git**: For version control

### Optional (Installed via `install.sh`)
- `rich` (>=13.0.0): Terminal UI library
- `tqdm` (>=4.65.0): Progress bars

---

## 🚀 Installation

### Quick Setup (Automated)

```bash
git clone https://github.com/manoharavinash/AUTO-DRIVE-UPLOADER.git
cd AUTO-DRIVE-UPLOADER
bash install.sh
```

The `install.sh` script will:
1. Update package manager (`apt`)
2. Install Python and dependencies
3. Install RClone (if not already present)
4. Install Python packages from `requirements.txt`
5. Guide you to configure RClone

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

---

## ⚙️ RClone Configuration

After installation, configure your Google Drive remote:

```bash
rclone config
```

Follow the prompts to:
1. Create a new remote
2. Name it exactly: `google auto photo`
3. Select "Google Drive" as the type
4. Complete OAuth authentication

Verify configuration:
```bash
rclone listremotes
```

You should see: `google auto photo`

---

## 📁 Project Structure

```
AUTO-DRIVE-UPLOADER/
├── requirements.txt          # Python dependencies
├── install.sh               # Automated setup script
├── drive.py                 # Low-level RClone wrapper
├── uploader.py              # Progress tracker & parser
├── upload.py                # Main orchestrator & UI
└── README.md                # This file
```

### Module Breakdown

#### `drive.py` - RClone Wrapper
- Low-level subprocess interface to RClone
- Safe path handling with `os.path.expanduser()`
- Methods: `about()`, `list_files()`, `mkdir()`, `copy()`, `delete()`
- Custom exception handling: `RCloneDriveError`

#### `uploader.py` - Progress Tracker
- Real-time output parsing from RClone
- Regex patterns for stats extraction
- Rich progress bar rendering
- Speed and ETA calculation

#### `upload.py` - Main Orchestrator
- Interactive CLI menu system
- File/directory upload workflows
- Remote file browsing
- Settings and status display
- **Mandatory header watermark on every view**

---

## 🎮 Usage

Start the application:

```bash
python3 upload.py
```

### Main Menu Options

```
1. Upload File       - Upload a single file to Google Drive
2. Upload Directory  - Upload an entire directory tree
3. List Remote Files - Browse files in Google Drive
4. Settings          - View app settings and connection status
5. Exit              - Close the application
```

### Example Workflow

1. Launch: `python3 upload.py`
2. Select option `1` to upload a file
3. Enter local file path: `/home/user/documents/report.pdf`
4. Enter destination folder: `Reports` (or leave blank for root)
5. Confirm upload
6. Watch real-time progress with speed and ETA

---

## 🎨 UI Design

The application uses a **Cyberpunk/Matrix aesthetic** with:

- **Accent Color**: `bright_cyan` for structural elements
- **Header Panel**: Mandatory watermark appears on every dashboard:
  ```
  🛠️  DESIGNED BY MANOHAR AVINASH  🛠️
  ```
- **Table Grids**: Responsive layouts using `Table.grid()`
- **Real-time Bars**: Progress bars with transfer speed and remaining time

---

## 🔒 Security & Safety Features

- **Type Checking**: Validates file vs. directory paths before any operation
- **Path Safety**: All paths expanded with `os.path.expanduser()` for tilde (`~`) support
- **Error Handling**: Graceful error messages and validation feedback
- **No Credential Storage**: All auth handled by RClone config

---

## 🐛 Troubleshooting

### RClone Not Found
```bash
# Install RClone
apt install rclone

# Or use official script on Linux
curl https://rclone.org/install.sh | sudo bash
```

### Remote 'google auto photo' Not Configured
```bash
rclone config
# Create new remote with name: google auto photo
```

### Permission Denied on install.sh
```bash
chmod +x install.sh
bash install.sh
```

### Module Import Errors
```bash
pip install -r requirements.txt --force-reinstall
```

---

## 📊 Performance

- **Memory**: ~50 MB baseline
- **Upload Speed**: Limited by network (RClone's throughput)
- **Scalability**: Handles files up to Google Drive limits (~5 TB)
- **Real-time Updates**: Progress updates every ~100 KB

---

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows PEP 8 style guidelines
- Cyberpunk aesthetic is maintained
- Mandatory header watermark is preserved on all views
- Termux compatibility is tested

---

## 📄 License

MIT License - See LICENSE file for details

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