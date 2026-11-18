"""
Stream Clipper & Multi-Platform Publisher (Snickerly Style)
Monitors, downloads, automatically edits, and publishes authentic streamer clips.
Features:
- Live Twitch discovery for GTA streamers with >= 30,000 concurrent viewers
- Direct authentic clip ingestion via Twitch & yt-dlp
- Real-time 1-word-at-a-time yellow kinetic subtitles powered by Faster-Whisper
- Preserves streamer facecam & authentic audio voice/screams/reactions
- Snickerly audio & visual SFX (Vine Boom + zoom, Minecraft drink/eat, wholesome piano)
- Autonomous publishing to Facebook Reels & Instagram Reels
"""

import os
import sys
import json
import argparse
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).parent.resolve()
ROOT_DIR = BASE_DIR.parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv(ROOT_DIR / ".env")

CONFIG_FILE = BASE_DIR / "config" / "streamers_30.json"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

from snickerly_editor import render_snickerly_video

TWITCH_HEADERS = {"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}

def search_live_gta_streamers(min_viewers: int = 30000) -> list:
    """Queries Twitch GQL for streamers currently live in GTA VI or GTA V with >= min_viewers"""
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
    # Sort descending by viewer count
    streamers.sort(key=lambda x: x["viewersCount"], reverse=True)
    return streamers

def get_streamer_clips(login: str, limit: int = 5) -> list:
    """Fetches recent viral clips for a streamer from Twitch GQL"""
    for time_filter in ["LAST_DAY", "LAST_WEEK", "ALL_TIME"]:
        query = f"""
        query {{
          user(login: "{login}") {{
            displayName
            clips(first: {limit}, criteria: {{ filter: {time_filter} }}) {{
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
            resp = requests.post(
                "https://gql.twitch.tv/gql",
                headers=TWITCH_HEADERS,
                json={"query": query},
                timeout=10
            )
            data = resp.json().get("data", {}).get("user", {})
            if not data or not data.get("clips"):
                continue
            edges = data["clips"].get("edges", [])
            clips = []
            for edge in edges:
                n = edge["node"]
                clips.append({
                    "id": n.get("id"),
                    "slug": n.get("slug"),
                    "title": n.get("title"),
                    "viewCount": n.get("viewCount", 0),
                    "duration": n.get("durationSeconds", 30),
                    "url": n.get("url")
                })
            if clips:
                return clips
        except Exception as e:
            print(f"⚠️ Error querying clips for {login}: {e}")
    return []

def download_clip_with_ytdlp(clip_url: str, out_filename: str = "temp_stream_clip.mp4") -> Path:
    """Downloads authentic clip in highest available quality using yt-dlp"""
    out_path = OUTPUT_DIR / out_filename
    if out_path.exists():
        out_path.unlink()

    print(f"\n[Clipper] Downloading clip from: {clip_url}...")
    cmd = [
        "yt-dlp",
        "--force-overwrites",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", str(out_path),
        clip_url
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not out_path.exists():
        print(f"❌ yt-dlp error: {res.stderr[-300:]}")
        raise RuntimeError("Failed to download clip with yt-dlp.")

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"✅ Downloaded clip: {out_path.name} ({size_mb:.2f}MB)")
    return out_path

def transcribe_clip_words(audio_video_path: Path) -> list:
    """
    Transcribes audio using Faster-Whisper to extract exact 1-word timestamps
    Returns list of dicts: [{"word": "BRO", "start": 1.2, "end": 1.5, "punch": True}, ...]
    """
    try:
        from faster_whisper import WhisperModel
        print(f"🎙️ Transcribing speech with Faster-Whisper (tiny model)...")
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, info = model.transcribe(str(audio_video_path), word_timestamps=True)
        print(f"   Detected language: {info.language} (prob: {info.language_probability:.2f})")
        
        words = []
        for segment in segments:
            for w in segment.words:
                clean_w = w.word.strip().upper()
                if clean_w:
                    is_punch = any(k in clean_w for k in ["WHAT", "BRO", "NO", "WAIT", "HUH", "HELL", "DAMN", "SHIT", "FUCK", "CRAZY"])
                    words.append({
                        "text": clean_w,
                        "start": w.start,
                        "end": w.end,
                        "punch": is_punch
                    })
        print(f"✅ Transcribed {len(words)} words with real-time timestamps.")
        return words
    except Exception as e:
        print(f"⚠️ Faster-Whisper transcription failed, fallback to rhythmic timing: {e}")
        # Fallback rhythmic words
        fallback = [
            ("BRO", 0.5, 0.9, True),
            ("JUST", 0.9, 1.3, False),
            ("WATCH", 1.3, 1.7, False),
            ("THIS", 1.7, 2.1, False),
            ("MOMENT", 2.1, 2.7, True),
            ("IN", 2.7, 3.0, False),
            ("GTA", 3.0, 3.5, True),
            ("6!", 3.5, 4.0, True),
            ("WAIT", 4.2, 4.7, False),
            ("WHAT?", 4.7, 5.3, True),
            ("LOOK", 5.5, 6.0, False),
            ("AT", 6.0, 6.3, False),
            ("HIM!", 6.3, 7.0, True),
        ]
        return [{"text": w, "start": s, "end": e, "punch": p} for (w, s, e, p) in fallback]

def detect_snickerly_cues(words: list, duration: float) -> list:
    """
    Generates Snickerly SFX cues based on spoken words and time milestones
    """
    events = []
    boom_times = []

    for w in words:
        txt = w["text"].lower()
        t = w["start"]
        if any(k in txt for k in ["water", "drink", "sip", "thirsty"]):
            events.append({"type": "drink", "time": t})
        elif any(k in txt for k in ["eat", "food", "burger", "bite", "chew"]):
            events.append({"type": "eat", "time": t})
        elif any(k in txt for k in ["what", "bro", "huh", "pause", "no", "hell", "fuck", "damn"]):
            # Avoid placing vine booms too close together (at least 3.0s apart)
            if not any(abs(t - bt) < 3.0 for bt in boom_times):
                events.append({"type": "vine_boom", "time": t, "zoom": True})
                boom_times.append(t)
        elif any(k in txt for k in ["love", "wholesome", "proud", "thank", "gg"]):
            events.append({"type": "wholesome", "start": t, "end": min(duration, t + 4.0)})

    # Ensure at least one vine boom if none triggered
    if not boom_times and duration > 5.0:
        default_boom = min(duration * 0.45, 6.0)
        events.append({"type": "vine_boom", "time": default_boom, "zoom": True})

    return events

def get_streamer_layout(streamer_login: str) -> str:
    """Returns the facecam layout configuration for a streamer"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            streamers = json.load(f).get("streamers", [])
            for s in streamers:
                if s.get("id") == streamer_login or s.get("channel") == streamer_login:
                    return s.get("facecam_layout", "stacked_bottom_left")
    # Default layout
    if streamer_login.lower() in ["xqc", "kaicenat"]:
        return "stacked_bottom_left"
    elif streamer_login.lower() in ["alanzoka", "djmariio", "trymacs"]:
        return "stacked_top_left"
    elif streamer_login.lower() in ["montanablack88"]:
        return "stacked_bottom_right"
    return "stacked_bottom_left"

def process_and_publish_stream_clip(
    clip_url: str,
    streamer_name: str,
    streamer_login: str,
    clip_title: str,
    publish: bool = True
) -> str:
    """Complete pipeline: Download -> Transcribe -> Snickerly Edit -> Publish"""
    print(f"\n============================================================")
    print(f"🎬 PROCESSING CLIP: {streamer_name} (@{streamer_login})")
    print(f"Title: {clip_title}")
    print(f"URL: {clip_url}")
    print(f"============================================================")

    # 1. Download
    raw_filename = f"raw_{streamer_login}_{Path(clip_url).stem}.mp4"
    raw_path = download_clip_with_ytdlp(clip_url, raw_filename)

    # 2. Transcribe real-time 1-word subtitles
    words = transcribe_clip_words(raw_path)

    # 3. Probe duration
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(raw_path)]
    probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
    duration = float(json.loads(probe_res.stdout)["format"]["duration"])

    # 4. Generate Snickerly cues
    events = detect_snickerly_cues(words, duration)

    # 5. Determine layout
    layout = get_streamer_layout(streamer_login)

    # 6. Render
    out_video = OUTPUT_DIR / f"snickerly_{streamer_login}_{Path(raw_path).stem}_rendered.mp4"
    rendered_file = render_snickerly_video(
        source_video=str(raw_path),
        output_path=str(out_video),
        streamer_name=streamer_name,
        events=events,
        dialogues=words,
        layout_mode=layout
    )

    # 7. Publish to Meta Reels (Facebook & Instagram)
    if publish and os.environ.get("SKIP_UPLOAD") != "1":
        hook_title = f"{streamer_name} Plays GTA 6 - Funniest Reaction! 💀"
        tags = ["GTA6", "GTAVI", streamer_name.replace(" ", ""), "Gaming", "Snickerly", "Reels", "Shorts"]
        desc = f"{clip_title}\n\nStreamer: @{streamer_name}\nGame: Grand Theft Auto VI\nEdited with Snickerly aesthetics.\n\n" + " ".join([f"#{t}" for t in tags])

        try:
            from meta_uploader import upload_all_meta_reels
            print("\n🚀 Publishing live to Meta (Facebook & Instagram Reels)...")
            res_meta = upload_all_meta_reels(rendered_file, hook_title, desc, tags)
            print(f"✅ Meta Publication Success: {res_meta}")
        except Exception as e:
            print(f"⚠️ Meta publication error: {e}")

    return rendered_file

def run_cli():
    parser = argparse.ArgumentParser(description="Snickerly 24/7 Autonomous Stream Clipper")
    parser.add_argument("--auto-discover", action="store_true", help="Auto-discover live GTA streamers >= 30k viewers")
    parser.add_argument("--min-viewers", type=int, default=30000, help="Minimum viewers threshold (default 30000)")
    parser.add_argument("--streamer", type=str, default="xqc", help="Target streamer login")
    parser.add_argument("--publish", action="store_true", help="Publish to Meta Reels")
    args = parser.parse_args()

    if args.auto_discover:
        print(f"🔍 Searching for live GTA streamers with >= {args.min_viewers:,} viewers...")
        live_streamers = search_live_gta_streamers(min_viewers=args.min_viewers)
        if not live_streamers:
            print(f"❌ No live GTA streamers found with >= {args.min_viewers:,} viewers. Exiting.")
            return

        print(f"✨ Found {len(live_streamers)} streamers with >= {args.min_viewers:,} viewers:")
        for s in live_streamers:
            print(f"   - {s['displayName']} (@{s['login']}): {s['viewersCount']:,} viewers [{s['game']}]")

        # Pick top streamer with available clips
        for target in live_streamers:
            print(f"\nChecking clips for {target['displayName']} (@{target['login']})...")
            clips = get_streamer_clips(target['login'], limit=3)
            if clips:
                chosen_clip = clips[0]
                print(f"🎯 Selected viral clip: '{chosen_clip['title']}' ({chosen_clip['url']})")
                process_and_publish_stream_clip(
                    clip_url=chosen_clip['url'],
                    streamer_name=target['displayName'],
                    streamer_login=target['login'],
                    clip_title=chosen_clip['title'],
                    publish=args.publish
                )
                return
        print("⚠️ No clips found for any live streamer.")
    else:
        # Target specific streamer
        login = args.streamer
        print(f"Fetching clips for streamer @{login}...")
        clips = get_streamer_clips(login, limit=3)
        if not clips:
            print(f"❌ No clips found for @{login}")
            return
        c = clips[0]
        process_and_publish_stream_clip(
            clip_url=c['url'],
            streamer_name=login.upper(),
            streamer_login=login,
            clip_title=c['title'],
            publish=args.publish
        )

if __name__ == "__main__":
    run_cli()
