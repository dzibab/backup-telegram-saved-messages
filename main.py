import os
import uuid
import asyncio
import shutil

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import InputMessagesFilterDocument
from smbprotocol.connection import Connection
from smbprotocol.session import Session
from smbprotocol.tree import TreeConnect
from smbprotocol.open import Open, CreateDisposition, FileAttributes, FileInformationClass

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Configuration
def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

API_ID = get_env('API_ID')
API_HASH = get_env('API_HASH')
SMB_SERVER = get_env('SMB_SERVER')
SMB_SHARE = get_env('SMB_SHARE')
SMB_USERNAME = get_env('SMB_USERNAME')
SMB_PASSWORD = get_env('SMB_PASSWORD')

TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp_files')
os.makedirs(TEMP_DIR, exist_ok=True)

def cleanup_temp_dir() -> None:
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

async def download_telegram_files() -> None:
    client = TelegramClient('session_name', API_ID, API_HASH)
    await client.start()
    async for message in client.iter_messages('me', filter=InputMessagesFilterDocument()):
        if message.file:
            filename = message.file.name or f"file_{message.id}"
            file_path = os.path.join(TEMP_DIR, filename)
            await message.download_media(file_path)
            print(f"Downloaded: {file_path}")
    await client.disconnect()

def smb_file_exists(tree: TreeConnect, remote_file_path: str) -> bool:
    try:
        with Open(tree, remote_file_path, CreateDisposition.FILE_OPEN, FileAttributes.FILE_ATTRIBUTE_NORMAL) as remote_file:
            remote_file.query_info(FileInformationClass.FILE_STANDARD_INFORMATION)
        return True
    except Exception:
        return False

def upload_to_smb() -> None:
    connection = Connection(uuid.uuid4(), SMB_SERVER, 445)
    connection.connect()
    session = Session(connection, SMB_USERNAME, SMB_PASSWORD)
    session.connect()
    tree = TreeConnect(session, fr"\\{SMB_SERVER}\{SMB_SHARE}")
    tree.connect()
    for file_name in os.listdir(TEMP_DIR):
        local_file_path = os.path.join(TEMP_DIR, file_name)
        remote_file_path = file_name  # relative to share root
        if smb_file_exists(tree, remote_file_path):
            print(f"Skipping (already exists): {remote_file_path}")
            continue
        try:
            with Open(tree, remote_file_path, CreateDisposition.FILE_OVERWRITE_IF) as remote_file:
                with open(local_file_path, 'rb') as local_file:
                    remote_file.write(local_file.read())
                print(f"Uploaded: {remote_file_path}")
        except Exception as e:
            print(f"Error uploading {file_name}: {e}")

def main() -> None:
    cleanup_temp_dir()
    asyncio.run(download_telegram_files())
    upload_to_smb()

if __name__ == "__main__":
    main()
