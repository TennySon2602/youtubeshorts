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

def render_gta6_final_short(cards_video: Path, audio_path: Path, ass_path: Path, duration: float, out_video: Path, sfx_name: str = "sfx_hook_boom.mp3"):
    """
    Composites video stream, multi-layer audio stream (Speech + BGM + SFX), and burns synchronized word-by-word subtitles.
    """
    print(f"[GTA6 Compiler] Compositing final video ({duration:.2f}s) to {out_video.name}...")
    ass_clean = str(ass_path).replace("\\", "/").replace(":", "\\:")

    bgm_file = ASSETS_DIR / "gtavi" / "gta6_bgm_suspense.mp3"
    sfx_file = ASSETS_DIR / "gtavi" / sfx_name
    if not sfx_file.exists():
        sfx_file = ASSETS_DIR / "gtavi" / "sfx_hook_boom.mp3"

    input_args = [
        "-i", str(cards_video),   # [0:v]
        "-i", str(audio_path)     # [1:a] Speech
    ]

    filter_complex_parts = [
        f"[0:v]ass='{ass_clean}'[outv]"
    ]

    audio_mix_inputs = ["[speech]"]
    filter_complex_parts.append("[1:a]volume=1.0[speech]")

    next_idx = 2
    if bgm_file.exists():
        input_args.extend(["-stream_loop", "-1", "-i", str(bgm_file)])
        filter_complex_parts.append(
            f"[{next_idx}:a]volume=0.18,afade=t=in:ss=0:d=1.5,afade=t=out:st={max(duration-2.5, 1.0):.2f}:d=2.0[bgm]"
        )
        audio_mix_inputs.append("[bgm]")
        next_idx += 1

    if sfx_file.exists():
        input_args.extend(["-i", str(sfx_file)])
        filter_complex_parts.append(
            f"[{next_idx}:a]volume=0.85[sfx]"
        )
        audio_mix_inputs.append("[sfx]")
        next_idx += 1

    if len(audio_mix_inputs) > 1:
        mix_inputs_str = "".join(audio_mix_inputs)
        filter_complex_parts.append(
            f"{mix_inputs_str}amix=inputs={len(audio_mix_inputs)}:duration=first:normalize=0[mixed_a];"
            f"[mixed_a]loudnorm=I=-14:LRA=7:tp=-1[outa]"
        )
        a_map = "[outa]"
    else:
        a_map = "1:a:0"

    cmd = [
        "ffmpeg", "-y",
        *input_args,
        "-filter_complex", ";".join(filter_complex_parts),
        "-map", "[outv]",
        "-map", a_map,
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
    sfx_name = topic.get("hook_sfx", "sfx_hook_boom.mp3")
    render_gta6_final_short(
        cards_video=stitched_video,
        audio_path=mp3_file,
        ass_path=ass_file,
        duration=total_duration,
        out_video=final_video,
        sfx_name=sfx_name
    )

    # 5. Multi-Platform Autonomous Publishing
    if os.environ.get("SKIP_UPLOAD") == "1":
        print("\n[Upload] SKIP_UPLOAD=1 detected. Skipping all platform uploads.")
    else:
        # A. YouTube Shorts Upload
        privacy = os.environ.get("UPLOAD_PRIVACY", "public")
        print(f"\n[Upload 1/3] Publishing to YouTube Shorts (privacy='{privacy}')...")
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
            print(f"[YouTube Warning] Upload failed: {e}")

        # B. Meta Upload (Facebook Reels & Instagram Reels)
        print(f"\n[Upload 2/3] Publishing to Facebook Reels & Instagram Reels...")
        try:
            from meta_uploader import upload_all_meta_reels
            meta_res = upload_all_meta_reels(
                file_path=str(final_video),
                title=topic["title"],
                description=topic["description"],
                tags=topic["tags"]
            )
            print(f"🚀 Meta Upload Results: {meta_res}")
        except Exception as e:
            print(f"[Meta Warning] Upload failed: {e}")

        # C. TikTok Upload
        print(f"\n[Upload 3/3] Publishing to TikTok...")
        try:
            from tiktok_uploader import upload_tiktok_video
            tiktok_res = upload_tiktok_video(
                file_path=str(final_video),
                title=topic["title"],
                tags=topic["tags"]
            )
            print(f"🚀 TikTok Upload Result: {tiktok_res}")
        except Exception as e:
            print(f"[TikTok Warning] Upload skipped or failed: {e}")

    print("\n==================================================")
    print("✨ GTA VI SHORT GENERATION FINISHED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    main()
