"""
Twitter (X) Video Uploader & Publisher
Uses Twitter v1.1 Chunked Media Upload and Twitter v2 API for Tweet Publishing.
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from requests_oauthlib import OAuth1

# Load .env locally if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                val = v.strip().strip("\"'")
                if val:
                    os.environ.setdefault(k.strip(), val)

API_KEY = os.environ.get("TWITTER_API_KEY", "").strip()
API_SECRET = os.environ.get("TWITTER_API_SECRET", "").strip()
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "").strip()
ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "").strip()

UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
TWEET_URL = "https://api.twitter.com/2/tweets"

def get_oauth():
    if not (API_KEY and API_SECRET and ACCESS_TOKEN and ACCESS_TOKEN_SECRET):
        raise ValueError("Missing Twitter (X) credentials in environment or .env")
    return OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

def upload_twitter_video(file_path: str, caption: str, tags: list = None) -> dict:
    """
    Uploads a video to Twitter (X) using Chunked Media Upload protocol and publishes a Tweet.
    """
    oauth = get_oauth()
    video_path = Path(file_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {file_path}")

    file_size = video_path.stat().st_size
    print(f"\n[Twitter/X] Starting video upload for '{video_path.name}' ({file_size // 1024 // 1024}MB)...")

    # Step 1: INIT
    init_data = {
        "command": "INIT",
        "total_bytes": str(file_size),
        "media_type": "video/mp4",
        "media_category": "tweet_video"
    }
    init_res = requests.post(UPLOAD_URL, data=init_data, auth=oauth, timeout=30)
    if init_res.status_code not in (200, 201, 202):
        raise RuntimeError(f"Twitter INIT failed ({init_res.status_code}): {init_res.text}")

    media_id = init_res.json()["media_id_string"]
    print(f"[Twitter/X] Upload session initialized. Media ID: {media_id}")

    # Step 2: APPEND chunks (4MB per chunk)
    chunk_size = 4 * 1024 * 1024
    segment_index = 0
    with open(video_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            print(f"  [Twitter/X] Uploading chunk {segment_index} ({len(chunk) // 1024} KB)...")
            append_data = {
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": str(segment_index)
            }
            append_files = {"media": chunk}
            append_res = requests.post(
                UPLOAD_URL, data=append_data, files=append_files, auth=oauth, timeout=60
            )
            if append_res.status_code not in (200, 201, 202, 204):
                raise RuntimeError(f"Twitter APPEND chunk {segment_index} failed: {append_res.text}")
            segment_index += 1

    print(f"[Twitter/X] All chunks uploaded. Finalizing...")

    # Step 3: FINALIZE
    fin_data = {"command": "FINALIZE", "media_id": media_id}
    fin_res = requests.post(UPLOAD_URL, data=fin_data, auth=oauth, timeout=30)
    if fin_res.status_code not in (200, 201, 202):
        raise RuntimeError(f"Twitter FINALIZE failed: {fin_res.text}")

    fin_json = fin_res.json()
    processing_info = fin_json.get("processing_info")

    # Step 4: STATUS polling (if video needs async processing)
    if processing_info:
        state = processing_info.get("state")
        while state not in ("succeeded", "failed"):
            wait_sec = processing_info.get("check_after_secs", 5)
            print(f"  [Twitter/X] Processing video (state: {state}), waiting {wait_sec}s...")
            time.sleep(wait_sec)

            status_res = requests.get(
                UPLOAD_URL, params={"command": "STATUS", "media_id": media_id}, auth=oauth, timeout=30
            )
            if status_res.status_code != 200:
                raise RuntimeError(f"Twitter STATUS check failed: {status_res.text}")

            status_json = status_res.json()
            processing_info = status_json.get("processing_info", {})
            state = processing_info.get("state", "succeeded")

        if state == "failed":
            raise RuntimeError(f"Twitter video processing failed: {processing_info}")

    print(f"✅ [Twitter/X] Video media ready: {media_id}")

    # Step 5: Publish Tweet via Twitter API v2
    tags_str = " ".join([f"#{t.strip('#')}" for t in (tags or ["GTA6", "GTAVI", "RockstarGames"])])
    # Keep tweet text within 280 character limit
    tweet_text = f"{caption}\n\n{tags_str}".strip()
    if len(tweet_text) > 275:
        tweet_text = tweet_text[:270] + "..."

    tweet_payload = {
        "text": tweet_text,
        "media": {"media_ids": [media_id]}
    }

    tweet_res = requests.post(
        TWEET_URL,
        json=tweet_payload,
        headers={"Content-Type": "application/json"},
        auth=oauth,
        timeout=30
    )

    if tweet_res.status_code not in (200, 201):
        raise RuntimeError(f"Failed to publish Tweet ({tweet_res.status_code}): {tweet_res.text}")

    tweet_data = tweet_res.json().get("data", {})
    tweet_id = tweet_data.get("id")
    tweet_url = f"https://x.com/i/web/status/{tweet_id}"
    print(f"🎉 [Twitter/X] SUCCESSFULLY PUBLISHED! Tweet ID: {tweet_id}")
    print(f"🔗 [Twitter/X] Tweet URL: {tweet_url}")

    return {
        "success": True,
        "tweet_id": tweet_id,
        "url": tweet_url
    }

if __name__ == "__main__":
    test_video = Path("output/gta6_lucia_ankle_monitor_final_short.mp4")
    if test_video.exists():
        upload_twitter_video(
            file_path=str(test_video),
            caption="GTA 6 - The Secret Detail Behind Lucia's Ankle Monitor Revealed!",
            tags=["GTA6", "GTAVI", "RockstarGames", "Gaming"]
        )
    else:
        print(f"Test video not found: {test_video}")
