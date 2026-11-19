"""
StreamClipper Autonomous Multi-Platform Pipeline
Integrates alokbaraii/streamclipper engine with multi-platform auto-publishing:
- Live Twitch GTA Streamer Discovery (>= 30,000 viewers)
- StreamClipper Story-first Highlight Extraction & Audio Peak Analysis
- 9:16 Vertical Video Render (streamer-split-9x16 preset, kinetic bold-pop subtitles, punch-in zooms)
- Autonomous Multi-Platform Publishing:
    * YouTube Shorts (Category 20: Gaming, Public)
    * Facebook Reels (Page ID: 1489998967525792 'GTA Clips')
    * Instagram Reels (Account ID: 17841457367667463 '@gta_viclips67')
"""

import os
import sys
import json
import time
import argparse
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

load_dotenv(BASE_DIR / ".env")

# Meta & YouTube Credentials
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "1489998967525792")
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "17841457367667463")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")

PROCESSED_CLIPS_FILE = BASE_DIR / "stream_clipper" / "config" / "processed_clips.json"
WORK_DIR = BASE_DIR / "work_streamclipper"
WORK_DIR.mkdir(parents=True, exist_ok=True)

TWITCH_HEADERS = {"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}

def load_processed_clips() -> set:
    if PROCESSED_CLIPS_FILE.exists():
        try:
            with open(PROCESSED_CLIPS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()

def mark_clip_processed(clip_id: str):
    clips = load_processed_clips()
    clips.add(clip_id)
    PROCESSED_CLIPS_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(PROCESSED_CLIPS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(clips), f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save processed clips: {e}")

def search_live_gta_streamers(min_viewers: int = 30000) -> list:
    """Queries Twitch GQL for top live streamers in GTA 6 or GTA 5"""
    streamers = []
    for game_name in ["Grand Theft Auto VI", "Grand Theft Auto V"]:
        query = f"""
        query {{
          game(name: "{game_name}") {{
            name
            streams(first: 30) {{
              edges {{
                node {{
                  id
                  title
                  viewersCount
                  broadcaster {{
                    id
                    login
                    displayName
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        try:
            resp = requests.post(
                "https://gql.twitch.tv/gql",
                headers=TWITCH_HEADERS,
                json={"query": query},
                timeout=10
            )
            data = resp.json()
            game_node = data.get("data", {}).get("game")
            if not game_node or not game_node.get("streams"):
                continue
            for edge in game_node["streams"]["edges"]:
                n = edge["node"]
                vc = n.get("viewersCount", 0)
                b = n.get("broadcaster", {})
                if vc >= min_viewers and b.get("login"):
                    streamers.append({
                        "game": game_node.get("name"),
                        "login": b.get("login"),
                        "displayName": b.get("displayName"),
                        "viewersCount": vc,
                        "title": n.get("title", "")
                    })
        except Exception as e:
            print(f"⚠️ Error querying {game_name}: {e}")

    streamers.sort(key=lambda x: x["viewersCount"], reverse=True)
    return streamers

def get_streamer_source(login: str) -> dict:
    """
    Finds the best source for a streamer:
    1. Check for live stream VOD on Twitch
    2. Fallback to top recent clip
    """
    # 1. Check latest VOD
    query_vod = f"""
    query {{
      user(login: "{login}") {{
        displayName
        videos(first: 1, type: ARCHIVE) {{
          edges {{
            node {{
              id
              title
              lengthSeconds
            }}
          }}
        }}
      }}
    }}
    """
    try:
        resp = requests.post("https://gql.twitch.tv/gql", headers=TWITCH_HEADERS, json={"query": query_vod}, timeout=10)
        videos = resp.json().get("data", {}).get("user", {}).get("videos", {}).get("edges", [])
        if videos:
            node = videos[0]["node"]
            vod_id = node.get("id")
            length_sec = node.get("lengthSeconds", 0)
            if length_sec > 60:
                return {
                    "type": "vod",
                    "id": f"vod_{vod_id}",
                    "url": f"https://www.twitch.tv/videos/{vod_id}",
                    "title": node.get("title", f"{login} GTA Stream")
                }
    except Exception as e:
        print(f"⚠️ Error checking VOD for {login}: {e}")

    # 2. Check recent clips
    query_clip = f"""
    query {{
      user(login: "{login}") {{
        displayName
        clips(first: 3, criteria: {{ filter: LAST_DAY }}) {{
          edges {{
            node {{
              id
              slug
              title
              viewCount
              durationSeconds
              url
            }}
          }}
        }}
      }}
    }}
    """
    try:
        resp = requests.post("https://gql.twitch.tv/gql", headers=TWITCH_HEADERS, json={"query": query_clip}, timeout=10)
        clips = resp.json().get("data", {}).get("user", {}).get("clips", {}).get("edges", [])
        if clips:
            node = clips[0]["node"]
            return {
                "type": "clip",
                "id": node.get("slug") or node.get("id"),
                "url": node.get("url"),
                "title": node.get("title", f"{login} GTA Clip")
            }
    except Exception as e:
        print(f"⚠️ Error checking clips for {login}: {e}")

    return {
        "type": "channel",
        "id": f"channel_{login}",
        "url": f"https://www.twitch.tv/{login}",
        "title": f"{login} Live Stream"
    }

def run_streamclipper_on_source(source_url: str, out_dir: Path, max_clips: int = 1) -> list:
    """
    Executes StreamClipper engine on the source URL:
    Renders 1080x1920 Shorts using 'streamer-split-9x16' preset and bold-pop captions.
    Returns list of rendered clip dicts with {mp4, title, hook, tags, score}.
    """
    print(f"\n🎬 Running StreamClipper Engine on: {source_url}...")
    cmd = [
        "streamclipper",
        "clip-stream",
        "--url", source_url,
        "--out", str(out_dir),
        "--preset", "streamer-split-9x16",
        "--caption-style", "bold-pop",
        "--zoom", "medium",
        "--device", "cpu",
        "--whisper-model", "tiny",
        "--max-clips", str(max_clips),
        "--render",
        "--no-draft",
        "--overwrite"
    ]

    res = subprocess.run(cmd, text=True, capture_output=True)
    print(res.stdout)
    if res.returncode != 0:
        print(f"⚠️ StreamClipper stderr: {res.stderr[-300:]}")

    # Inspect rendered outputs in out_dir
    rendered_clips = []
    clips_json_path = out_dir / "clips.json"
    if clips_json_path.exists():
        try:
            with open(clips_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for c in data.get("clips", []):
                    mp4_name = c.get("mp4") or "clip.mp4"
                    mp4_path = out_dir / mp4_name
                    if mp4_path.exists():
                        rendered_clips.append({
                            "mp4": str(mp4_path),
                            "title": c.get("title") or "Stream Clip",
                            "hook_headline": c.get("hook_headline") or "WATCH THIS!",
                            "category": c.get("category", "gaming"),
                            "hashtags": c.get("hashtags", ["#GTA6", "#Shorts", "#Gaming"]),
                            "score": c.get("score", 0),
                            "raw": c
                        })
        except Exception as e:
            print(f"⚠️ Error reading clips.json: {e}")

    return rendered_clips

def publish_clip_multiplatform(
    mp4_path: str,
    streamer_name: str,
    title: str,
    hook_headline: str,
    hashtags: list,
    publish: bool = True
):
    """
    Publishes a rendered clip across YouTube Shorts, Facebook Reels, and Instagram Reels.
    """
    if not publish or os.environ.get("SKIP_UPLOAD") == "1":
        print("⏭️ Upload skipped (--publish is False or SKIP_UPLOAD=1).")
        return

    clean_streamer = streamer_name.replace(" ", "").replace("_", "")
    hook_clean = hook_headline.replace("\n", " ").strip()
    yt_title = f"{streamer_name} Plays GTA 6 - {hook_clean}! 💀 #Shorts"[:95]
    tags = ["GTA6", "GTAVI", clean_streamer, "Gaming", "Shorts", "Reels", "StreamClipper"]
    tags_line = " ".join([f"#{t}" if not t.startswith("#") else t for t in hashtags or tags])
    desc = f"{title}\n\nStreamer: @{streamer_name}\nGame: Grand Theft Auto VI\nEdited with StreamClipper AI.\n\n{tags_line}"

    # 1. Publish to Facebook Reels
    try:
        from meta_uploader import upload_facebook_reel
        print("\n🚀 [Facebook Reels] Uploading...")
        res_fb = upload_facebook_reel(
            file_path=mp4_path,
            caption=f"{yt_title}\n\n{desc}",
            page_id=FB_PAGE_ID,
            access_token=FB_PAGE_ACCESS_TOKEN
        )
        print(f"✅ Facebook Reels Published: {res_fb}")
    except Exception as e:
        print(f"⚠️ Facebook Reels Error: {e}")

    # 2. Publish to Instagram Reels
    try:
        from meta_uploader import upload_instagram_reel
        print("\n🚀 [Instagram Reels] Uploading...")
        res_ig = upload_instagram_reel(
            file_path=mp4_path,
            caption=f"{yt_title}\n\n{tags_line}",
            instagram_account_id=INSTAGRAM_ACCOUNT_ID,
            access_token=FB_PAGE_ACCESS_TOKEN
        )
        print(f"✅ Instagram Reels Published: {res_ig}")
    except Exception as e:
        print(f"⚠️ Instagram Reels Error: {e}")

    # 3. Publish to YouTube Shorts
    try:
        from youtube_uploader import upload_video
        print("\n🚀 [YouTube Shorts] Uploading...")
        yt_res = upload_video(
            file_path=mp4_path,
            title=yt_title,
            description=desc,
            tags=tags,
            category_id="20",
            privacy_status="public"
        )
        vid_id = yt_res.get("id") if isinstance(yt_res, dict) else yt_res
        print(f"✅ YouTube Shorts Published: https://youtube.com/shorts/{vid_id}")
    except Exception as e:
        err = str(e)
        if "uploadLimitExceeded" in err:
            print("⚠️ [YouTube Notice] Channel daily upload limit reached (uploadLimitExceeded). Hạn ngạch sẽ hồi phục sau 24h.")
        else:
            print(f"⚠️ YouTube Shorts Error: {e}")

def run_single_cycle(args, processed_history: set):
    """Runs a single discovery, clipping, and auto-publishing cycle"""
    if args.url:
        print(f"\n🎯 Direct URL mode: {args.url}")
        target_name = "Streamer"
        clips = run_streamclipper_on_source(args.url, WORK_DIR, max_clips=args.max_clips)
        for c in clips:
            clip_key = f"{args.url}_{Path(c['mp4']).name}"
            if clip_key not in processed_history:
                publish_clip_multiplatform(
                    mp4_path=c["mp4"],
                    streamer_name=target_name,
                    title=c["title"],
                    hook_headline=c["hook_headline"],
                    hashtags=c["hashtags"],
                    publish=args.publish
                )
                mark_clip_processed(clip_key)
                processed_history.add(clip_key)
        return

    if args.auto_discover:
        print(f"\n🔍 Searching for live GTA streamers with >= {args.min_viewers:,} viewers...")
        streamers = search_live_gta_streamers(min_viewers=args.min_viewers)
        if not streamers:
            print(f"❌ No live GTA streamers found with >= {args.min_viewers:,} viewers.")
            return

        print(f"✨ Found {len(streamers)} streamers with >= {args.min_viewers:,} viewers:")
        for s in streamers:
            print(f"   - {s['displayName']} (@{s['login']}): {s['viewersCount']:,} viewers [{s['game']}]")

        processed_count = 0
        for s in streamers:
            if processed_count >= args.max_streamers:
                print(f"\n🎉 Reached limit of {args.max_streamers} streamers for this cycle.")
                break

            print(f"\nChecking source for {s['displayName']} (@{s['login']})...")
            source_info = get_streamer_source(s['login'])
            source_key = source_info.get("id") or source_info.get("url")

            if source_key in processed_history:
                print(f"   Source {source_key} already processed previously. Skipping.")
                continue

            print(f"🎯 Target Source [{source_info['type']}]: {source_info['title']} ({source_info['url']})")
            streamer_work_dir = WORK_DIR / s['login']
            streamer_work_dir.mkdir(parents=True, exist_ok=True)

            clips = run_streamclipper_on_source(source_info['url'], streamer_work_dir, max_clips=1)
            if not clips:
                print(f"   No rendered clips produced for {s['login']}.")
                continue

            for c in clips:
                publish_clip_multiplatform(
                    mp4_path=c["mp4"],
                    streamer_name=s['displayName'],
                    title=c["title"],
                    hook_headline=c["hook_headline"],
                    hashtags=c["hashtags"],
                    publish=args.publish
                )

            mark_clip_processed(source_key)
            processed_history.add(source_key)
            processed_count += 1

        print(f"\n🏁 Cycle complete. Processed {processed_count} streamers.")

    else:
        streamer_login = args.streamer.strip()
        print(f"\nTargeting specific streamer @{streamer_login}...")
        source_info = get_streamer_source(streamer_login)
        streamer_work_dir = WORK_DIR / streamer_login
        streamer_work_dir.mkdir(parents=True, exist_ok=True)

        clips = run_streamclipper_on_source(source_info['url'], streamer_work_dir, max_clips=args.max_clips)
        for c in clips:
            publish_clip_multiplatform(
                mp4_path=c["mp4"],
                streamer_name=streamer_login.upper(),
                title=c["title"],
                hook_headline=c["hook_headline"],
                hashtags=c["hashtags"],
                publish=args.publish
            )
            mark_clip_processed(f"{source_info['id']}_{Path(c['mp4']).name}")

def main():
    parser = argparse.ArgumentParser(description="StreamClipper Autonomous Multi-Platform Pipeline")
    parser.add_argument("--auto-discover", action="store_true", help="Auto-discover live GTA streamers >= min-viewers")
    parser.add_argument("--min-viewers", type=int, default=30000, help="Minimum viewers threshold (default 30000)")
    parser.add_argument("--max-streamers", type=int, default=3, help="Max distinct streamers to process per run (default 3)")
    parser.add_argument("--streamer", type=str, default="kaicenat", help="Target specific streamer login")
    parser.add_argument("--url", type=str, default=None, help="Direct video, stream, or VOD URL to clip")
    parser.add_argument("--max-clips", type=int, default=1, help="Max clips per streamer (default 1)")
    parser.add_argument("--publish", action="store_true", help="Publish automatically to FB Reels, IG Reels & YouTube")
    parser.add_argument("--loop", action="store_true", help="Run 24/7 in a continuous loop")
    parser.add_argument("--interval", type=int, default=900, help="Interval between runs in loop mode (default: 900s = 15m)")
    args = parser.parse_args()

    processed_history = load_processed_clips()

    if args.loop:
        print(f"\n🔄 STARTING STREAMCLIPPER 24/7 AUTONOMOUS PIPELINE (Interval: {args.interval}s / {args.interval//60} mins)...")
        print("Press Ctrl+C to terminate.")
        while True:
            try:
                run_single_cycle(args, processed_history)
            except Exception as e:
                print(f"⚠️ Unexpected error in loop: {e}")
            print(f"\n⏳ Sleeping for {args.interval} seconds until next cycle ({time.strftime('%H:%M:%S')})...\n")
            time.sleep(args.interval)
    else:
        run_single_cycle(args, processed_history)

if __name__ == "__main__":
    main()
