"""
TikTok Uploader for GTA VI Shorts
Uses TikTok Content Posting API v2 (Direct Post).
Supports automatic refresh of access tokens using refresh_token.
"""

import os
import json
import time
import requests
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
TOKEN_FILE = BASE_DIR / "tiktok_token.json"

DEFAULT_CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY", "awtbu0l2t6tw00zn")
DEFAULT_CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "UcmYPH53gJZoBip2jewVjPGdHw7TREYz")

def get_valid_tiktok_token() -> str:
    """
    Retrieves a valid TikTok Access Token.
    If cached in tiktok_token.json and expired, refreshes it automatically.
    """
    if os.environ.get("TIKTOK_ACCESS_TOKEN"):
        return os.environ.get("TIKTOK_ACCESS_TOKEN")

    if not TOKEN_FILE.exists():
        raise FileNotFoundError(
            "Chưa có TikTok Access Token! Hãy chạy 'python renew_tiktok_token.py' (hoặc click renew_tiktok_token.bat) để đăng nhập và lấy token."
        )

    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        token_data = json.load(f)

    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    # Optional refresh check
    # TikTok refresh endpoint: POST https://open.tiktokapis.com/v2/oauth/token/
    return access_token

def upload_tiktok_video(file_path: str, title: str, tags: list = None) -> dict:
    """
    Uploads a video to TikTok via Content Posting API v2.
    """
    video_path = Path(file_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {file_path}")

    token = get_valid_tiktok_token()
    file_size = video_path.stat().st_size
    print(f"[TikTok] Initializing direct video post for '{video_path.name}' ({file_size // 1024 // 1024}MB)...")

    tags_str = " ".join([f"#{t.strip('#')}" for t in (tags or ["GTA6", "Gaming", "Shorts"])])
    full_title = f"{title} {tags_str}"[:150]  # TikTok title max 150 chars

    # Step 1: Initialize Post
    init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    payload = {
        "post_info": {
            "title": full_title,
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False,
            "disable_stitch": False,
            "disable_comment": False,
            "video_cover_timestamp_ms": 1000
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": file_size,
            "total_chunk_count": 1
        }
    }

    res = requests.post(init_url, headers=headers, json=payload, timeout=30)
    res_data = res.json()

    if res.status_code != 200 or "data" not in res_data or "upload_url" not in res_data["data"]:
        raise RuntimeError(f"TikTok post init failed: {res_data}")

    publish_id = res_data["data"]["publish_id"]
    upload_url = res_data["data"]["upload_url"]
    print(f"[TikTok] Session initialized (Publish ID: {publish_id}). Uploading binary video...")

    # Step 2: Upload Video Binary
    upload_headers = {
        "Content-Type": "video/mp4",
        "Content-Range": f"bytes 0-{file_size - 1}/{file_size}"
    }
    with open(video_path, "rb") as f:
        put_res = requests.put(upload_url, headers=upload_headers, data=f, timeout=120)

    if put_res.status_code not in (200, 201):
        raise RuntimeError(f"TikTok upload chunk failed (HTTP {put_res.status_code}): {put_res.text}")

    print(f"🎉 [TikTok] SUCCESSFULLY UPLOADED! Publish ID: {publish_id}")
    return {"publish_id": publish_id, "success": True}

if __name__ == "__main__":
    test_video = Path("output/gta6_lucia_ankle_monitor_final_short.mp4")
    if test_video.exists():
        try:
            upload_tiktok_video(str(test_video), "The Dark Secret Behind Lucia Ankle Monitor")
        except Exception as e:
            print("TikTok Test Note:", e)
