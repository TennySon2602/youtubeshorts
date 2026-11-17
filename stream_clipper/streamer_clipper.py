"""
Stream Clipper & Multi-Platform Publisher (Snickerly Style)
Monitors, downloads, automatically edits, and publishes streamer clips.
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = BASE_DIR / "config" / "streamers_30.json"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

from snickerly_editor import render_snickerly_video

def load_streamers():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("streamers", [])
    return []

def download_clip_with_ytdlp(clip_url: str, out_filename: str = "temp_stream_clip.mp4") -> Path:
    """Downloads a clip from Twitch, Kick, or YouTube via yt-dlp"""
    out_path = OUTPUT_DIR / out_filename
    if out_path.exists():
        out_path.unlink()

    print(f"\n[Clipper] Downloading clip from: {clip_url}...")
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", str(out_path),
        clip_url
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not out_path.exists():
        print(f"❌ yt-dlp error: {res.stderr[-300:]}")
        raise RuntimeError("Failed to download clip with yt-dlp.")

    print(f"✅ Downloaded clip: {out_path.name} ({out_path.stat().st_size // 1024 // 1024}MB)")
    return out_path

def auto_detect_snickerly_events(transcript_words: list = None, duration: float = 30.0) -> tuple:
    """
    Analyzes spoken keywords to place Snickerly triggers:
    - Minecraft drink: 'drink', 'water', 'thirsty', 'sip', 'gulp'
    - Minecraft eat: 'eat', 'burger', 'food', 'snack', 'bite', 'hungry'
    - Vine boom + zoom: 'bro', 'wait', 'what', 'huh', 'hell nah', 'deadass', 'pause'
    - Wholesome: 'love you', 'appreciate', 'thank you', 'wholesome', 'proud'
    """
    events = []
    dialogues = []

    if transcript_words:
        # Keyword-based event generation
        for w in transcript_words:
            word_str = w.get("word", "").lower().strip(".,!?:;")
            start = w.get("start", 0.0)
            end = w.get("end", start + 0.5)

            if any(k in word_str for k in ["water", "drink", "sip", "thirsty"]):
                events.append({"type": "drink", "time": start})
            elif any(k in word_str for k in ["eat", "food", "burger", "bite", "chew"]):
                events.append({"type": "eat", "time": start})
            elif any(k in word_str for k in ["what", "bro", "huh", "pause", "hell", "nah"]):
                events.append({"type": "vine_boom", "time": start, "zoom": True})
            elif any(k in word_str for k in ["love", "wholesome", "proud", "thank"]):
                events.append({"type": "wholesome", "start": start, "end": min(duration, start + 4.0)})

            dialogues.append({
                "start": start,
                "end": end,
                "text": word_str.upper(),
                "punch": any(k in word_str for k in ["what", "nah", "bro", "skull", "crazy"])
            })
    else:
        # Default algorithmic rhythm if no transcript provided (e.g. 1st half hook, middle boom, outro)
        events = [
            {"type": "drink", "time": 2.5},
            {"type": "vine_boom", "time": min(duration * 0.45, 7.0), "zoom": True},
            {"type": "wholesome", "start": min(duration * 0.65, 11.0), "end": min(duration * 0.85, 15.0)},
            {"type": "eat", "time": min(duration * 0.9, 16.0)}
        ]
        # 1-word-at-a-time kinetic subtitles matching real-time speech cadence
        raw_words = [
            ("BRO", 0.5, 0.85, True),
            ("REALLY", 0.85, 1.25, False),
            ("JUST", 1.25, 1.60, False),
            ("PULLED", 1.60, 2.00, False),
            ("UP", 2.00, 2.30, False),
            ("TO", 2.30, 2.55, False),
            ("GTA", 2.55, 3.10, True),
            ("6!", 3.10, 3.60, True),
            ("WAIT...", 4.20, 4.70, True),
            ("WHAT", 4.70, 5.15, True),
            ("DID", 5.15, 5.50, False),
            ("HE", 5.50, 5.80, False),
            ("JUST", 5.80, 6.20, False),
            ("DO?", 6.20, 6.75, True),
            ("NO", 7.20, 7.65, True),
            ("WAY!", 7.65, 8.20, True),
            ("LOOK", 8.40, 8.85, False),
            ("AT", 8.85, 9.15, False),
            ("THIS...", 9.15, 9.75, False),
            ("ACTUALLY", 10.00, 10.60, False),
            ("SO", 10.60, 11.00, False),
            ("WHOLESOME!", 11.00, 12.20, True),
            ("WAIT", 12.80, 13.30, False),
            ("FOR", 13.30, 13.65, False),
            ("THE", 13.65, 13.95, False),
            ("ENDING!", 13.95, 14.80, True),
        ]
        dialogues = [
            {"start": s, "end": e, "text": w, "punch": p}
            for (w, s, e, p) in raw_words if e <= duration
        ]

    return events, dialogues

def process_and_publish_clip(
    source_file: str,
    streamer_id: str,
    hook_title: str,
    publish_now: bool = False
) -> str:
    """
    Takes raw stream clip -> Edits with Snickerly aesthetics -> Publishes multi-platform
    """
    streamers = load_streamers()
    streamer_info = next((s for s in streamers if s["id"] == streamer_id), {
        "name": streamer_id.title(),
        "id": streamer_id
    })

    streamer_name = streamer_info["name"]
    out_video = OUTPUT_DIR / f"snickerly_{streamer_id}_{Path(source_file).stem}_final.mp4"

    events, dialogues = auto_detect_snickerly_events()

    print(f"\n" + "=" * 60)
    print(f"🎬 EDITING SNICKERLY SHORT: {streamer_name}")
    print(f"Hook: {hook_title}")
    print("=" * 60)

    rendered_video = render_snickerly_video(
        source_video=source_file,
        output_path=str(out_video),
        streamer_name=streamer_name,
        hook_title=hook_title,
        events=events,
        dialogues=dialogues
    )

    if publish_now and os.environ.get("SKIP_UPLOAD") != "1":
        print(f"\n🚀 Đang tự động xuất bản lên các nền tảng...")
        tags = ["GTA6", "GTAVI", streamer_name.replace(" ", ""), "Snickerly", "Gaming", "Shorts", "Reels"]
        desc = f"{hook_title}\n\nCredit: @{streamer_name}\nEditing inspired by Snickerly.\n\n" + " ".join([f"#{t}" for t in tags])

        # 1. Meta (Facebook Reels & Instagram Reels)
        try:
            from meta_uploader import upload_all_meta_reels
            print("[Upload 1/2] Meta Publishing (FB & IG Reels)...")
            res_meta = upload_all_meta_reels(rendered_video, hook_title, desc, tags)
            print(f"✅ Meta Result: {res_meta}")
        except Exception as e:
            print(f"⚠️ Meta upload error: {e}")

        # 2. YouTube Shorts
        try:
            from youtube_uploader import upload_video
            print("[Upload 2/2] YouTube Shorts Publishing...")
            upload_video(rendered_video, hook_title, desc, tags, privacy_status="public")
            print("✅ YouTube Shorts Published!")
        except Exception as e:
            print(f"⚠️ YouTube upload error: {e}")

    return rendered_video

if __name__ == "__main__":
    test_src = "assets/gtavi/source_gta6_trailer.mp4"
    if Path(test_src).exists():
        process_and_publish_clip(
            source_file=test_src,
            streamer_id="ishowspeed",
            hook_title="SPEED FIRST TIME PLAYING GTA 6 💀",
            publish_now=False
        )
