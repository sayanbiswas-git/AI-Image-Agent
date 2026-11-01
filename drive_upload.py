import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import DRIVE_FOLDER_ID

# Permission to upload and modify files
SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_drive_service():
    creds = None
    # Check if we already logged in previously
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # If no valid credentials, pop open the browser to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("\n[Auth] Opening web browser to log into Google Drive...")
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the token so we don't have to log in again next time
        with open("token.json", "w") as token:
            token.write(creds.to_json())
            
    return build("drive", "v3", credentials=creds)

def upload_to_drive(local_path: str, filename: str) -> str:
    try:
        service = get_drive_service()

        file_metadata = {
            "name": filename,
            "parents": [DRIVE_FOLDER_ID]
        }

        media = MediaFileUpload(local_path, mimetype="image/jpeg", resumable=True)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
            supportsAllDrives=True
        ).execute()

        # Make link public so your Excel sheet links actually work
        try:
            service.permissions().create(
                fileId=file.get("id"),
                body={"type": "anyone", "role": "reader"},
                supportsAllDrives=True
            ).execute()
        except Exception:
            pass

        return file.get("webViewLink", "")
        
    except Exception as e:
        print(f"      [upload] Google Drive Error: {e}")
        return ""