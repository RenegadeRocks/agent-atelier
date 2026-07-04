import json
import os
import uuid
from mcp.server.fastmcp import FastMCP
from mcp import types

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.cloud import storage

from app.agents import config

server = FastMCP("drive_mcp_server")

def get_credentials():
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set in environment.")
    return service_account.Credentials.from_service_account_file(
        creds_path,
        scopes=['https://www.googleapis.com/auth/drive.file']
    )

def get_gcs_credentials():
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set in environment.")
    return service_account.Credentials.from_service_account_file(
        creds_path,
        scopes=['https://www.googleapis.com/auth/devstorage.read_write']
    )

@server.tool()
def drive_handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name != "drive":
        raise ValueError(f"Unknown tool: {name}")

    action = arguments.get("action")
    if action != "upload":
        raise ValueError(f"Unknown action: {action}")

    file_path = arguments.get("file_id")
    if not file_path or not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")

    filename = os.path.basename(file_path)
    
    if getattr(config, "USE_GCS_FOR_VISUALS", False):
        print(f"[MCP drive] Uploading {filename} to GCS bucket {config.GCS_BUCKET_NAME}...")
        creds = get_gcs_credentials()
        storage_client = storage.Client(credentials=creds, project=creds.project_id)
        bucket = storage_client.bucket(config.GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        
        blob.upload_from_filename(file_path, content_type="image/jpeg")
        
        # GCS public URL pattern
        public_url = f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/{filename}"
        
        output = {
            "file_id": filename,
            "drive_url": public_url,
            "byte_url": public_url,
            "mime_type": "image/jpeg",
            "bytes": os.path.getsize(file_path)
        }
        return [types.TextContent(type="text", text=json.dumps(output))]

    else:
        print(f"[MCP drive] Uploading {filename} to Drive folder {config.DRIVE_FOLDER_ID}...")
        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': filename,
            'parents': [config.DRIVE_FOLDER_ID]
        }
        media = MediaFileUpload(file_path, mimetype='image/jpeg', resumable=True)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, webContentLink, size, mimeType'
        ).execute()

        output = {
            "file_id": file.get('id'),
            "drive_url": file.get('webViewLink'),
            "byte_url": file.get('webContentLink'),
            "mime_type": file.get('mimeType'),
            "bytes": int(file.get('size', 0))
        }

        return [types.TextContent(type="text", text=json.dumps(output))]

if __name__ == "__main__":
    server.run()
