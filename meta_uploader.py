"""
Meta Uploader for Facebook Reels & Instagram Reels
Uses Meta Graph API v21.0 with official Resumable Reels Protocol.
"""

import os
import time
import requests
from pathlib import Path

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

# Defaults from environment or project config
DEFAULT_FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "1489998967525792")
DEFAULT_INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "17841457367667463")
DEFAULT_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")

GRAPH_API_VERSION = "v21.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

def upload_facebook_reel(file_path: str, caption: str, page_id: str = None, access_token: str = None) -> dict:
    """
    Publishes a vertical video as a Facebook Reel to the specified Page.
    """
    page_id = page_id or DEFAULT_FB_PAGE_ID
    token = access_token or DEFAULT_ACCESS_TOKEN
    video_path = Path(file_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {file_path}")

    file_size = video_path.stat().st_size
    print(f"[Facebook Reels] Starting upload for '{video_path.name}' ({file_size // 1024 // 1024}MB) to Page {page_id}...")

    # Phase 1: Initialize upload session
    init_url = f"{GRAPH_BASE}/{page_id}/video_reels"
    init_res = requests.post(
        init_url,
        params={"upload_phase": "start", "access_token": token},
        timeout=30
    )
    init_data = init_res.json()
    if init_res.status_code != 200 or "upload_url" not in init_data:
        raise RuntimeError(f"Failed to initialize FB Reel session: {init_data}")

    video_id = init_data["video_id"]
    upload_url = init_data["upload_url"]
    print(f"[Facebook Reels] Session created (Video ID: {video_id}). Uploading binary data...")

    # Phase 2: Upload binary data
    headers = {
        "Authorization": f"OAuth {token}",
        "offset": "0",
        "file_size": str(file_size),
        "Content-Type": "application/octet-stream"
    }
    with open(video_path, "rb") as f:
        upload_res = requests.post(upload_url, headers=headers, data=f, timeout=120)

    if upload_res.status_code != 200:
        raise RuntimeError(f"Failed to upload FB Reel bytes: {upload_res.text}")

    print(f"[Facebook Reels] Video binary uploaded. Finalizing publish...")

    # Phase 3: Finalize and Publish
    finish_res = requests.post(
        init_url,
        params={
            "upload_phase": "finish",
            "access_token": token,
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": caption
        },
        timeout=30
    )
    finish_data = finish_res.json()
    if finish_res.status_code != 200 or not finish_data.get("success"):
        raise RuntimeError(f"Failed to finalize FB Reel: {finish_data}")

    print(f"🎉 [Facebook Reels] SUCCESSFULLY PUBLISHED! Video ID: {video_id}")
    return {"video_id": video_id, "success": True}

def upload_instagram_reel(file_path: str, caption: str, ig_user_id: str = None, access_token: str = None) -> dict:
    """
    Publishes a vertical video as an Instagram Reel using the Resumable Protocol.
    """
    ig_user_id = ig_user_id or DEFAULT_INSTAGRAM_ACCOUNT_ID
    token = access_token or DEFAULT_ACCESS_TOKEN
    video_path = Path(file_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {file_path}")

    file_size = video_path.stat().st_size
    print(f"[Instagram Reels] Starting upload for '{video_path.name}' ({file_size // 1024 // 1024}MB) to IG ID {ig_user_id}...")

    # Step 1: Initialize Resumable Media Container
    media_url = f"{GRAPH_BASE}/{ig_user_id}/media"
    init_res = requests.post(
        media_url,
        params={
            "media_type": "REELS",
            "upload_type": "resumable",
            "caption": caption,
            "access_token": token
        },
        timeout=30
    )
    init_data = init_res.json()
    if init_res.status_code != 200 or "uri" not in init_data:
        raise RuntimeError(f"Failed to initialize IG Reel container: {init_data}")

    container_id = init_data["id"]
    upload_uri = init_data["uri"]
    print(f"[Instagram Reels] Container created ({container_id}). Uploading bytes...")

    # Step 2: Upload bytes to rupload
    headers = {
        "Authorization": f"OAuth {token}",
        "offset": "0",
        "file_size": str(file_size)
    }
    with open(video_path, "rb") as f:
        upload_res = requests.post(upload_uri, headers=headers, data=f, timeout=120)

    if upload_res.status_code != 200:
        raise RuntimeError(f"Failed to upload IG Reel bytes: {upload_res.text}")

    print(f"[Instagram Reels] Bytes uploaded. Waiting for Instagram processing...")

    # Step 3: Poll status until FINISHED
    status_url = f"{GRAPH_BASE}/{container_id}"
    ready = False
    for attempt in range(15):
        time.sleep(5)
        status_res = requests.get(status_url, params={"fields": "status_code", "access_token": token}, timeout=30)
        status_data = status_res.json()
        code = status_data.get("status_code")
        print(f"  [Instagram Reels] Processing status: {code} (Check {attempt+1}/15)...")

        if code == "FINISHED":
            ready = True
            break
        elif code == "ERROR":
            raise RuntimeError(f"Instagram processing error: {status_data}")

    if not ready:
        raise TimeoutError("Timed out waiting for Instagram Reel processing.")

    # Step 4: Publish Media Container
    publish_url = f"{GRAPH_BASE}/{ig_user_id}/media_publish"
    pub_res = requests.post(
        publish_url,
        params={"creation_id": container_id, "access_token": token},
        timeout=30
    )
    pub_data = pub_res.json()
    if pub_res.status_code != 200 or "id" not in pub_data:
        raise RuntimeError(f"Failed to publish IG Reel: {pub_data}")

    post_id = pub_data["id"]
    print(f"🎉 [Instagram Reels] SUCCESSFULLY PUBLISHED! Post ID: {post_id}")
    return {"id": post_id, "success": True}

def upload_all_meta_reels(file_path: str, title: str, description: str, tags: list = None) -> dict:
    """
    Convenience function to publish simultaneously to Facebook Reels and Instagram Reels.
    """
    tags_str = " ".join([f"#{t.strip('#')}" for t in (tags or ["GTA6", "Gaming", "Shorts", "Reels"])])
    full_caption = f"{title}\n\n{description}\n\n{tags_str}"

    results = {}
    try:
        results["facebook"] = upload_facebook_reel(file_path, full_caption)
    except Exception as e:
        print(f"⚠️ [Facebook Reels Error] {e}")
        results["facebook"] = {"error": str(e)}

    try:
        results["instagram"] = upload_instagram_reel(file_path, full_caption)
    except Exception as e:
        print(f"⚠️ [Instagram Reels Error] {e}")
        results["instagram"] = {"error": str(e)}

    return results

if __name__ == "__main__":
    import sys
    test_video = Path("output/gta6_lucia_ankle_monitor_final_short.mp4")
    if test_video.exists():
        print("Testing Meta Uploader...")
        upload_all_meta_reels(str(test_video), "GTA VI Secret Revealed", "Check out this crazy detail in GTA 6!", ["GTA6", "Reels"])
    else:
        print(f"Test video not found: {test_video}")
