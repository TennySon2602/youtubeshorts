"""
GTA VI Master Automation Pipeline for YouTube Shorts
End-to-End Orchestrator:
1. Topic Selection (GTA VI Mysteries, Lore, Map & Mechanics)
2. Speech Synthesis & Word-by-Word Subtitles (Edge TTS)
3. Intelligent Gameplay Clipping & Formatting (FFmpeg)
4. Final Video Composite
5. Autonomous YouTube Shorts Upload (YouTube Data API v3)
"""

import os
import sys
import time
import asyncio
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

from gta6_lore_engine import get_gta6_topic
from gta6_voice_and_subs import generate_gta6_speech_and_timing
from gta6_clipper import build_gta6_scene_clips

def render_gta6_final_short(cards_video: Path, audio_path: Path, ass_path: Path, duration: float, out_video: Path):
    """
    Composites video stream, audio stream, and burns synchronized word-by-word subtitles.
    """
    print(f"[GTA6 Compiler] Compositing final video ({duration:.2f}s) to {out_video.name}...")
    ass_clean = str(ass_path).replace("\\", "/").replace(":", "\\:")

    filter_complex = f"[0:v]ass='{ass_clean}'[outv]"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(cards_video),
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{duration:.2f}",
        str(out_video)
    ]
    subprocess.run(cmd, check=True)
    print(f"🎉 GTA VI FINAL SHORT VIDEO READY: {out_video} ({out_video.stat().st_size // 1024 // 1024}MB)")

def main():
    print("==================================================")
    print("🔥 GTA VI GAMEPLAY & LORE BREAKDOWN SHORTS BOT")
    print("==================================================")

    # 1. Topic Selection
    topic_id = os.environ.get("TOPIC_ID")
    query = os.environ.get("TOPIC_QUERY") or os.environ.get("TOPIC_SEARCH")
    
    topic = get_gta6_topic(topic_id=topic_id, query=query)
    print(f"[Topic] ID: {topic['id']}")
    print(f"[Topic] Title: {topic['title']}")
    print(f"[Topic] Scenes: {len(topic['scenes'])} explanation sentences")

    # 2. Narration Audio & Word-by-Word Subtitles
    mp3_file = OUTPUT_DIR / f"gta6_{topic['id']}_narration.mp3"
    ass_file = OUTPUT_DIR / f"gta6_{topic['id']}_words.ass"
    print(f"[Voiceover] Generating documentary-style narration with Edge TTS...")
    scene_durations, total_duration = asyncio.run(
        generate_gta6_speech_and_timing(topic, mp3_file, ass_file)
    )
    print(f"[Voiceover] Generated speech audio ({total_duration:.2f}s across {len(scene_durations)} scenes)")

    # 3. Gameplay Clipping from 1080p GTA VI Footage
    stitched_video = OUTPUT_DIR / f"gta6_{topic['id']}_clips.mp4"
    build_gta6_scene_clips(topic, scene_durations, stitched_video)

    # 4. Final Composite
    final_video = OUTPUT_DIR / f"gta6_{topic['id']}_final_short.mp4"
    render_gta6_final_short(
        cards_video=stitched_video,
        audio_path=mp3_file,
        ass_path=ass_file,
        duration=total_duration,
        out_video=final_video
    )

    # 5. YouTube Upload via Data API v3
    if os.environ.get("SKIP_UPLOAD") == "1":
        print("\n[Upload] SKIP_UPLOAD=1 detected. Skipping YouTube upload.")
    else:
        privacy = os.environ.get("UPLOAD_PRIVACY", "public")
        print(f"\n[Upload] Publishing GTA VI Short to YouTube (privacy='{privacy}')...")
        
        try:
            from youtube_uploader import upload_video
            upload_video(
                file_path=str(final_video),
                title=topic["title"],
                description=topic["description"],
                tags=topic["tags"],
                privacy_status=privacy
            )
            print("🚀 Successfully uploaded to YouTube channel!")
        except Exception as e:
            print(f"[Upload Warning] YouTube upload failed: {e}")
            print("If running in CI, ensure secret YOUTUBE_TOKEN_JSON is set.")

    print("\n==================================================")
    print("✨ GTA VI SHORT GENERATION FINISHED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    main()
