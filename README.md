# Backup Telegram Saved Messages

This project is responsible for:

1. Backing up all files from your Telegram saved messages.
2. Downloading files to a local temporary directory.
3. Connecting to an SMB share and uploading all files there if they do not already exist in the SMB directory.

## Features
- Automatically fetches files from Telegram saved messages.
- Ensures files are only uploaded to the SMB share if they are not already present.

## Requirements
- Python 3.8+
- `telethon` library for interacting with Telegram.
- `smbprotocol` library for SMB operations.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the script:
   ```bash
   python main.py
   ```

## Environment Variables

Secrets and configuration are loaded from a `.env` file in the project root. Example:

```
API_ID=your_api_id
API_HASH=your_api_hash
SMB_SERVER=your_smb_server
SMB_SHARE=your_smb_share
SMB_USERNAME=your_username
SMB_PASSWORD=your_password
```

Make sure to create a `.env` file with your credentials before running the script.