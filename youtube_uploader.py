import os
import sys
import json
import time
import http.client
import httplib2
import random
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Scopes required for uploading to YouTube
SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly']
CLIENT_SECRETS_FILE = Path(__file__).parent / "client_secrets.json"
TOKEN_FILE = Path(__file__).parent / "token.json"

RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error, IOError, http.client.NotConnected,
    http.client.IncompleteRead, http.client.ImproperConnectionState,
    http.client.CannotSendRequest, http.client.CannotSendHeader,
    http.client.ResponseNotReady, http.client.BadStatusLine
)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

def get_authenticated_service():
    """
    Get authenticated YouTube service.
    Works locally (with browser flow & token.json)
    and in headless Cloud/GitHub Actions (via YOUTUBE_TOKEN_JSON env var).
    """
    creds = None
    
    # 1. Check if YOUTUBE_TOKEN_JSON env var is set (for GitHub Actions / Cloud)
    env_token = os.environ.get("YOUTUBE_TOKEN_JSON")
    if env_token:
        try:
            token_data = json.loads(env_token)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            print("[OAuth] Loaded credentials from YOUTUBE_TOKEN_JSON environment variable.")
        except Exception as e:
            print(f"[OAuth] Warning: Failed to load from YOUTUBE_TOKEN_JSON: {e}")
            creds = None

    # 2. Check local token.json
    if not creds and TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            print(f"[OAuth] Loaded credentials from {TOKEN_FILE}")
        except Exception as e:
            print(f"[OAuth] Warning: Failed to load token.json: {e}")
            creds = None

    # 3. Refresh or authenticate
    if creds and creds.expired and creds.refresh_token:
        print("[OAuth] Access token expired, refreshing with refresh_token...")
        try:
            creds.refresh(Request())
            # Save refreshed token
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
            print("[OAuth] Token refreshed and saved.")
        except Exception as e:
            print(f"[OAuth] Error refreshing token: {e}")
            creds = None

    # 4. If still no valid credentials, run interactive browser flow (Local only)
    if not creds or not creds.valid:
        if not CLIENT_SECRETS_FILE.exists():
            raise FileNotFoundError(f"Missing {CLIENT_SECRETS_FILE}. Please place client_secrets.json in project root.")
        
        print("[OAuth] Initiating interactive browser login flow...", flush=True)
        print("[OAuth] A browser window should open automatically. If not, follow the terminal URL.", flush=True)
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), SCOPES)
        creds = flow.run_local_server(
            port=0, 
            open_browser=True,
            access_type='offline',
            prompt='consent',
            authorization_prompt_message='\n[OAuth URL] Vui lòng truy cập liên kết sau để cấp quyền:\n{url}\n'
        )
        
        # Save credentials for future headless runs
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print(f"[OAuth] Success! Credentials saved to {TOKEN_FILE}")

    return build('youtube', 'v3', credentials=creds)

def upload_video(
    file_path: str,
    title: str,
    description: str,
    tags: list = None,
    category_id: str = "28", # 28 = Science & Technology
    privacy_status: str = "public" # public, unlisted, private
):
    """
    Upload a video to YouTube with resumable chunked upload.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Video file not found: {file_path}")

    youtube = get_authenticated_service()

    if tags is None:
        tags = ["Shorts", "Science", "DarkCuriosity", "DidYouKnow", "Facts"]

    body = {
        'snippet': {
            'title': title[:100], # Max 100 chars
            'description': description[:5000],
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }

    print(f"\n[Upload] Preparing to upload: {file_path.name}")
    print(f"[Upload] Title: {title}")
    print(f"[Upload] Privacy: {privacy_status}")

    media = MediaFileUpload(
        str(file_path),
        chunksize=1024 * 1024 * 4, # 4MB chunks
        resumable=True,
        mimetype="video/*"
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    retry = 0
    max_retries = 10

    print("[Upload] Uploading chunks...")
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"[Upload] Progress: {int(status.progress() * 100)}%")
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                print(f"[Upload] Retriable HTTP {e.resp.status} error: {e}")
                retry += 1
                if retry > max_retries:
                    raise
                time.sleep(random.random() * (2 ** retry))
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            print(f"[Upload] Retriable network error: {e}")
            retry += 1
            if retry > max_retries:
                raise
            time.sleep(random.random() * (2 ** retry))

    video_id = response.get('id')
    short_url = f"https://youtube.com/shorts/{video_id}"
    print("\n========================================")
    print(">>> UPLOAD COMPLETED SUCCESSFULLY! <<<")
    print(f"Video ID: {video_id}")
    print(f"Shorts URL: {short_url}")
    print("========================================\n")
    return response

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube Video Uploader")
    parser.add_argument("--auth", action="store_true", help="Perform initial authentication only")
    parser.add_argument("--file", type=str, help="Video file path to upload")
    parser.add_argument("--title", type=str, default="Can Silence Actually Kill You? #Shorts", help="Video title")
    parser.add_argument("--desc", type=str, default="The truth about what happens to your mind in pure silence... #Shorts #DarkCuriosity #Science", help="Video description")
    parser.add_argument("--privacy", type=str, default="unlisted", choices=["public", "unlisted", "private"], help="Privacy status")
    
    args = parser.parse_args()

    if args.auth:
        print("[Auth] Authorizing YouTube account...")
        service = get_authenticated_service()
        # Test call to verify
        channels_response = service.channels().list(mine=True, part='snippet').execute()
        items = channels_response.get('items', [])
        if items:
            channel_name = items[0]['snippet']['title']
            print(f"[Auth] Successfully connected to YouTube Channel: '{channel_name}'!")
        else:
            print("[Auth] Successfully authenticated, but no channel found for this account.")
        sys.exit(0)

    if args.file:
        upload_video(
            file_path=args.file,
            title=args.title,
            description=args.desc,
            privacy_status=args.privacy
        )
    else:
        print("Usage:")
        print("  python youtube_uploader.py --auth")
        print("  python youtube_uploader.py --file <path_to_video> --privacy <public|unlisted|private>")
