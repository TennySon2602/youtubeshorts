"""
GTA VI Intelligent Gameplay Clipper & Formatter
Extracts timestamped gameplay segments from official 1080p GTA VI footage
and renders them in cinematic 9:16 vertical short format.
"""

import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = BASE_DIR / "assets"
GTAVI_DIR = ASSETS_DIR / "gtavi"
OUTPUT_DIR = BASE_DIR / "output"
SOURCE_VIDEO = GTAVI_DIR / "source_gta6_trailer.mp4"
FONTS_DIR = ASSETS_DIR / "fonts"

YOUTUBE_SOURCE_URL = "https://www.youtube.com/watch?v=QdBZY2fkU-0"
FALLBACK_DIRECT_URL = "https://raw.githubusercontent.com/TennySon2602/youtubeshorts/main/assets/gtavi/source_gta6_trailer.mp4"

def ensure_source_footage() -> Path:
    """
    Ensures official 1080p Rockstar GTA VI footage is available:
    1. First checks local assets/gtavi/source_gta6_trailer.mp4 (tracked in Git for instant CI execution).
    2. Falls back to direct repository mirror via HTTP (bypassing YouTube anti-bot entirely).
    3. Falls back to yt-dlp as final resort.
    """
    GTAVI_DIR.mkdir(parents=True, exist_ok=True)
    if SOURCE_VIDEO.exists() and SOURCE_VIDEO.stat().st_size > 10_000_000:
        print(f"[GTA6 Clipper] Using local GTA VI footage: {SOURCE_VIDEO} ({SOURCE_VIDEO.stat().st_size // 1024 // 1024}MB)")
        return SOURCE_VIDEO

    # 2. Try direct mirror download (avoids YouTube datacenter bot detection on CI)
    import urllib.request
    try:
        print(f"[GTA6 Clipper] Local footage missing. Downloading from direct mirror: {FALLBACK_DIRECT_URL}...")
        headers = {"User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(FALLBACK_DIRECT_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=90) as resp, open(SOURCE_VIDEO, "wb") as out_f:
            while True:
                chunk = resp.read(1024 * 512)
                if not chunk:
                    break
                out_f.write(chunk)
        if SOURCE_VIDEO.exists() and SOURCE_VIDEO.stat().st_size > 10_000_000:
            print(f"[GTA6 Clipper] Downloaded source video from mirror ({SOURCE_VIDEO.stat().st_size // 1024 // 1024}MB)")
            return SOURCE_VIDEO
    except Exception as e:
        print(f"[GTA6 Clipper] Direct mirror download warning: {e}")
        if SOURCE_VIDEO.exists():
            SOURCE_VIDEO.unlink()

    # 3. Last resort: yt-dlp with android client
    print(f"[GTA6 Clipper] Attempting download via yt-dlp...")
    cmd = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=android,web",
        "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
        "--output", str(SOURCE_VIDEO),
        YOUTUBE_SOURCE_URL
    ]
    subprocess.run(cmd, check=True)
    print(f"[GTA6 Clipper] Downloaded source video via yt-dlp: {SOURCE_VIDEO} ({SOURCE_VIDEO.stat().st_size // 1024 // 1024}MB)")
    return SOURCE_VIDEO

def clip_scene_segment(source_path: Path, start_sec: float, duration: float, out_path: Path, hook_header: str = "GTA VI DEEP LORE"):
    """
    Renders a single scene segment into vertical 1080x1920:
    - Ambient blurred gameplay background (1080x1920, boxblur=25:5)
    - Center uncropped 16:9 gameplay footage (1020x574) with glowing 4px cyan border
    - Top hook banner
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Clean text for FFmpeg drawtext
    clean_hook = hook_header.replace("'", "").replace(":", "-").upper()
    
    # Font path for banner
    font_file = FONTS_DIR / "segoeuib.ttf"
    if not font_file.exists():
        font_file = FONTS_DIR / "arialbd.ttf"
    font_clean = str(font_file).replace("\\", "/").replace(":", "\\:") if font_file.exists() else "Arial"

    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        f"[0:v]scale=1020:574,drawbox=x=0:y=0:w=iw:h=ih:color=0x00FFCC:t=4[fg];"
        f"[bg][fg]overlay=30:520[v_composed];"
        # Top banner background bar
        f"[v_composed]drawbox=x=40:y=240:w=1000:h=130:color=0x0F172A@0.9:t=fill,"
        f"drawbox=x=40:y=240:w=1000:h=130:color=0x00FFCC:t=3,"
        # Top tag: GTA VI • EXCLUSIVE BREAKDOWN
        f"drawtext=fontfile='{font_clean}':text='GTA VI  *  EXCLUSIVE LORE BREAKDOWN':fontcolor=0x00FFCC:fontsize=26:x=(w-text_w)/2:y=265,"
        # Main hook headline
        f"drawtext=fontfile='{font_clean}':text='{clean_hook}':fontcolor=0xFFFFFF:fontsize=40:x=(w-text_w)/2:y=310[outv]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start_sec:.2f}",
        "-t", f"{duration:.2f}",
        "-i", str(source_path),
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-an",
        str(out_path)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def build_gta6_scene_clips(topic: dict, scene_durations: list, out_video: Path) -> Path:
    """
    Slices and stitches all gameplay scene clips matching the durations of the audio.
    """
    source_path = ensure_source_footage()
    clips = topic.get("clip_timestamps", [])
    hook_header = topic.get("hook_header", "GTA VI STORY BREAKDOWN")

    concat_txt = OUTPUT_DIR / f"{topic['id']}_concat.txt"
    lines = []

    print(f"[GTA6 Clipper] Slicing {len(scene_durations)} scenes from GTA VI gameplay...")
    for idx, dur in enumerate(scene_durations):
        # Pick timestamp range
        if idx < len(clips):
            start_ts = clips[idx][0]
        else:
            start_ts = (idx * 12.0) % 75.0

        seg_file = OUTPUT_DIR / f"{topic['id']}_seg_{idx}.mp4"
        print(f"  🎬 Scene {idx+1}/{len(scene_durations)}: timestamp={start_ts:.1f}s, duration={dur:.2f}s -> {seg_file.name}")
        clip_scene_segment(
            source_path=source_path,
            start_sec=start_ts,
            duration=dur,
            out_path=seg_file,
            hook_header=hook_header
        )
        lines.append(f"file '{seg_file.as_posix()}'")

    with open(concat_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Concat all segments with monotonic PTS
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        str(out_video)
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[GTA6 Clipper] All gameplay clips successfully stitched to {out_video}")
    return out_video

if __name__ == "__main__":
    from gta6_lore_engine import get_gta6_topic
    t = get_gta6_topic("lucia_ankle_monitor")
    durations = [4.5, 5.0, 4.8]
    out = OUTPUT_DIR / "test_gta6_stitched.mp4"
    build_gta6_scene_clips(t, durations, out)
    print("Test finished successfully:", out)
