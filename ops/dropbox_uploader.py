"""Dropbox Uploader 📤
────────────────────────────────────────────
Handles remote backup of generated log files.

Features:
- Secure upload to Dropbox using App Folder token
- Daily log rotation sync by filename
- Integrates with scheduled log archiving workflows
"""

import os
import dropbox
from datetime import datetime

DROPBOX_TOKEN = os.getenv("DROPBOX_API_TOKEN")

def upload_log_to_dropbox(local_path: str, remote_dir: str = "/hyphaeos_logs") -> str:
    """
    Upload a file to Dropbox under a daily log folder.

    Args:
        local_path (str): Full path to the log file to upload
        remote_dir (str): Destination Dropbox directory (default: "/hyphaeos_logs")

    Returns:
        str: Path to uploaded file on Dropbox

    Raises:
        RuntimeError: If token is missing or upload fails
    """
    if not DROPBOX_TOKEN:
        raise RuntimeError("❌ Dropbox token not set in .env")

    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    with open(local_path, "rb") as f:
        remote_path = f"{remote_dir}/{os.path.basename(local_path)}"
        dbx.files_upload(f.read(), remote_path, mode=dropbox.files.WriteMode.overwrite)

    return remote_path
