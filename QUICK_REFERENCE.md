# AUTO DRIVE UPLOADER - Quick Reference

## One-Minute Setup

```bash
git clone https://github.com/manoharavinash/AUTO-DRIVE-UPLOADER.git
cd AUTO-DRIVE-UPLOADER
bash install.sh
rclone config          # Create remote named "google auto photo"
bash start.sh          # Launch application
```

## File Reference

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `requirements.txt` | Python dependencies | `rich`, `tqdm` |
| `install.sh` | Automated setup | Auto-detects Termux/Linux |
| `start.sh` | Pre-flight checks | Validates env & launches |
| `drive.py` | RClone wrapper | `RCloneDrive` class |
| `uploader.py` | Progress tracking | `RCloneProgressTracker` class |
| `upload.py` | Main UI & orchestration | `AutoDriveUploader` class |

## Key Methods

### RCloneDrive
```python
drive.about()              # Get storage info
drive.list_files(path)     # List remote files
drive.mkdir(path)          # Create folder
drive.copy(local, remote)  # Upload (returns Popen)
drive.delete(path)         # Delete remote file
drive.validate_remote()    # Check connection
```

### RCloneProgressTracker
```python
tracker.stream_progress(process, name)    # Display progress
tracker.display_transfer_summary(success) # Show summary
```

### AutoDriveUploader
```python
app.render_header()        # Show watermark banner
app.render_dashboard()     # Show main menu
app.upload_file()          # File upload workflow
app.upload_directory()     # Directory upload workflow
app.list_remote_files()    # Browse Drive
app.show_settings()        # View configuration
app.run()                  # Main event loop
```

## Command Reference

### RClone Direct Usage
```bash
# Configure remote
rclone config

# Upload file
rclone copy ~/file.pdf "google auto photo:/Folder" -P --stats-one-line

# List files
rclone lsf "google auto photo:"

# Check quota
rclone about "google auto photo:" --json

# Delete file
rclone delete "google auto photo:/file.pdf"
```

### Application Launch
```bash
# Normal start
python3 upload.py

# With validation
bash start.sh

# With installation
bash install.sh
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "RClone not found" | Run `bash install.sh` |
| "Remote not configured" | Run `rclone config` |
| "Permission denied" | Run `chmod +x install.sh` |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Upload fails" | Check internet & RClone auth |

## Important Notes

⚠️ **MANDATORY WATERMARK**: Every dashboard view displays:
```
🛠️  DESIGNED BY MANOHAR AVINASH  🛠️
```

🎨 **COLOR SCHEME**: Bright cyan (`bright_cyan`) accent color

📱 **TERMUX READY**: Fully compatible with Android terminal

🔐 **SAFE PATHS**: All `~` expanded automatically

✅ **TYPE SAFE**: File/directory validation before operations

## Configuration Files

### RClone Config Location
- **Linux/Termux**: `~/.config/rclone/rclone.conf`
- **Windows**: `%APPDATA%\rclone\rclone.conf`

### Python Virtual Environment (Optional)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Performance Tips

- Keep files under 5GB for optimal performance
- Use WiFi for large uploads
- Close other apps to free memory
- RClone handles multiple files efficiently

## Contact & Support

- **Author**: Manohar Avinash
- **Repository**: https://github.com/manoharavinash/AUTO-DRIVE-UPLOADER
- **Issues**: Use GitHub Issues for bug reports
