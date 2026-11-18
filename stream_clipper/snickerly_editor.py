"""
Snickerly-Style AI Video Editor for Streamer Highlights
Emulates @NotSnickerly editing aesthetics:
1. 9:16 Vertical Dual Split (Top: Streamer Facecam, Bottom: GTA 6 Gameplay)
2. Retains 100% authentic original streamer mic audio & gameplay sound
3. Minecraft Drinking / Eating SFX on consumption moments
4. Vine Boom + Punch-in zoom on shock/awkward moments
5. Grayscale/Desaturation filter + Lo-Fi Wholesome BGM on sweet/emotional moments
6. Kinetic Pop Subtitles (1-word-at-a-time bold yellow Impact font, center positioned)
7. Clean presentation: NO top text banners, NO bottom credit watermarks
"""

import os
import sys
import json
import subprocess
from pathlib import Path

SFX_DIR = Path(__file__).parent / "assets" / "sfx"
VINE_BOOM = SFX_DIR / "sfx_vine_boom.mp3"
MINECRAFT_DRINK = SFX_DIR / "sfx_minecraft_drink.mp3"
MINECRAFT_EAT = SFX_DIR / "sfx_minecraft_eat.mp3"
MINECRAFT_BURP = SFX_DIR / "sfx_minecraft_burp.mp3"
WHOLESOME_BGM = SFX_DIR / "bgm_wholesome.mp3"
WHOOSH = SFX_DIR / "sfx_whoosh.mp3"

def build_snickerly_ass_subtitles(
    dialogue_events: list,
    ass_path: Path,
    margin_v: int = 850
):
    """
    Builds mobile-first Snickerly style ASS subtitles:
    - Pure 1-word-at-a-time kinetic pop subtitles in center
    - Extra bold Impact font (108pt), bright yellow (&H0000FFFF) with thick black outline (10px)
    - MarginV placed right at 850 (near center dividing line in 1080x1920)
    - Clean look: No top banners or bottom credits
    """
    ass_header = f"""[Script Info]
Title: Snickerly Streamer Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SnickerlyWord,Impact,108,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,105,105,2,0,1,10,2,2,40,40,{margin_v},1
Style: SnickerlyPunch,Impact,120,&H000055FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,118,118,3,0,1,12,3,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    def fmt(t):
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = t % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    lines = [ass_header]

    for d in dialogue_events:
        start_t = max(0.0, float(d["start"]))
        end_t = max(start_t + 0.1, float(d["end"]))
        raw_text = d["text"].upper().strip(".,!?:;\"'")
        if raw_text:
            style = "SnickerlyPunch" if d.get("punch") else "SnickerlyWord"
            lines.append(f"Dialogue: 1,{fmt(start_t)},{fmt(end_t)},{style},,0,0,0,,{raw_text}\n")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"✅ Generated 1-Word Kinetic ASS Subtitles: {ass_path.name} ({len(dialogue_events)} words)")

def render_snickerly_video(
    source_video: str,
    output_path: str,
    streamer_name: str,
    events: list = None,
    dialogues: list = None,
    layout_mode: str = "stacked_bottom_left"
):
    """
    Renders 9:16 Short with authentic facecam & audio:
    - layout_mode:
        - "stacked_bottom_left" (e.g. xQc): Facecam cropped from bottom-left (scaled to 1080x800), Gameplay bottom (1080x1120)
        - "stacked_top_left" (e.g. alanzoka): Facecam cropped from top-left, Gameplay bottom
        - "stacked_bottom_right": Facecam cropped from bottom-right, Gameplay bottom
        - "center_zoom": Center 9:16 crop for single-camera streams
    """
    src = Path(source_video)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    events = events or []
    dialogues = dialogues or []

    # Probe source video
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration:stream=width,height",
        "-of", "json", str(src)
    ]
    probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
    probe_data = json.loads(probe_res.stdout)
    duration = float(probe_data["format"]["duration"])
    width = int(probe_data["streams"][0]["width"])
    height = int(probe_data["streams"][0]["height"])

    print(f"[Snickerly Engine] Source: {src.name} ({width}x{height}, {duration:.2f}s)")
    print(f"[Snickerly Engine] Layout: {layout_mode} | Streamer: {streamer_name}")

    # Build ASS file
    ass_file = out.parent / f"{out.stem}_snickerly.ass"
    build_snickerly_ass_subtitles(
        dialogue_events=dialogues,
        ass_path=ass_file,
        margin_v=850
    )

    # Base Layout Filters
    # Top facecam (1080x800), Bottom gameplay (1080x1120) -> Stacked 1080x1920
    video_filters = []
    if layout_mode == "stacked_bottom_left":
        # Streamer facecam in bottom left (e.g. xQc)
        cam_w = int(width * 0.22)
        cam_h = int(height * 0.30)
        cam_x = 0
        cam_y = int(height * 0.48)
        game_w = int(width * 0.65)
        game_x = int(width * 0.25)
        video_filters.append(
            f"[0:v]crop={cam_w}:{cam_h}:{cam_x}:{cam_y},scale=1080:800:force_original_aspect_ratio=increase,crop=1080:800[cam];"
            f"[0:v]crop={game_w}:{height}:{game_x}:0,scale=1080:1120:force_original_aspect_ratio=increase,crop=1080:1120[game];"
            f"[cam][game]vstack[v_base]"
        )
    elif layout_mode == "stacked_top_left":
        # Streamer facecam in top left (e.g. alanzoka)
        cam_w = int(width * 0.25)
        cam_h = int(height * 0.30)
        cam_x = 0
        cam_y = 0
        game_w = int(width * 0.65)
        game_x = int(width * 0.25)
        video_filters.append(
            f"[0:v]crop={cam_w}:{cam_h}:{cam_x}:{cam_y},scale=1080:800:force_original_aspect_ratio=increase,crop=1080:800[cam];"
            f"[0:v]crop={game_w}:{height}:{game_x}:0,scale=1080:1120:force_original_aspect_ratio=increase,crop=1080:1120[game];"
            f"[cam][game]vstack[v_base]"
        )
    elif layout_mode == "stacked_bottom_right":
        cam_w = int(width * 0.25)
        cam_h = int(height * 0.30)
        cam_x = int(width * 0.75)
        cam_y = int(height * 0.70)
        game_w = int(width * 0.65)
        game_x = int(width * 0.10)
        video_filters.append(
            f"[0:v]crop={cam_w}:{cam_h}:{cam_x}:{cam_y},scale=1080:800:force_original_aspect_ratio=increase,crop=1080:800[cam];"
            f"[0:v]crop={game_w}:{height}:{game_x}:0,scale=1080:1120:force_original_aspect_ratio=increase,crop=1080:1120[game];"
            f"[cam][game]vstack[v_base]"
        )
    else:
        # Fallback center 9:16
        video_filters.append("[0:v]scale=-1:1920,crop=1080:1920:(in_w-1080)/2:0,setsar=1[v_base]")

    curr_v = "[v_base]"

    # Audio Mix setup
    audio_inputs = ["-i", str(src)]
    amix_filters = ["[0:a]volume=1.0[main_a]"]
    mix_sources = ["[main_a]"]
    input_idx = 1

    # Special Snickerly Visual & Audio FX
    for ev in events:
        ev_type = ev.get("type")
        if ev_type == "wholesome":
            w_start = ev.get("start", 0)
            w_end = ev.get("end", duration)
            video_filters.append(
                f"{curr_v}hue=s=if(between(t\\,{w_start}\\,{w_end})\\,0.1\\,1.0)[v_hue]"
            )
            curr_v = "[v_hue]"
            if WHOLESOME_BGM.exists():
                audio_inputs.extend(["-i", str(WHOLESOME_BGM)])
                delay_ms = int(w_start * 1000)
                dur = w_end - w_start
                amix_filters.append(
                    f"[{input_idx}:a]atrim=0:{dur},adelay={delay_ms}|{delay_ms},volume=0.35[a_wholesome]"
                )
                mix_sources.append("[a_wholesome]")
                input_idx += 1

        elif ev_type == "drink":
            t = ev.get("time", 0)
            if MINECRAFT_DRINK.exists():
                audio_inputs.extend(["-i", str(MINECRAFT_DRINK)])
                delay_ms = int(t * 1000)
                amix_filters.append(
                    f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},volume=1.2[a_drink]"
                )
                mix_sources.append("[a_drink]")
                input_idx += 1

        elif ev_type == "eat":
            t = ev.get("time", 0)
            if MINECRAFT_EAT.exists():
                audio_inputs.extend(["-i", str(MINECRAFT_EAT)])
                delay_ms = int(t * 1000)
                amix_filters.append(
                    f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},volume=1.2[a_eat]"
                )
                mix_sources.append("[a_eat]")
                input_idx += 1

        elif ev_type == "vine_boom":
            t = ev.get("time", 0)
            if VINE_BOOM.exists():
                audio_inputs.extend(["-i", str(VINE_BOOM)])
                delay_ms = int(t * 1000)
                amix_filters.append(
                    f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},volume=1.5[a_boom]"
                )
                mix_sources.append("[a_boom]")
                input_idx += 1

            if ev.get("zoom", True):
                z_start = t
                z_end = min(duration, t + 1.0)
                video_filters.append(
                    f"{curr_v}scale=w=1080:h=1920:eval=frame,crop=w='if(between(t\\,{z_start}\\,{z_end})\\,920\\,1080)':h='if(between(t\\,{z_start}\\,{z_end})\\,1635\\,1920)':x='(in_w-out_w)/2':y='(in_h-out_h)/2',scale=1080:1920[v_punch]"
                )
                curr_v = "[v_punch]"

    # Subtitles burn-in via libass
    ass_escaped = str(ass_file).replace("\\", "/").replace(":", "\\:")
    video_filters.append(f"{curr_v}ass='{ass_escaped}'[v_final]")

    # Audio final mix
    if len(mix_sources) > 1:
        amix_filters.append(f"{''.join(mix_sources)}amix=inputs={len(mix_sources)}:duration=first:dropout_transition=2[a_final]")
        final_a = "[a_final]"
    else:
        final_a = "[0:a]"

    filter_complex = ";".join(video_filters + amix_filters)

    cmd = [
        "ffmpeg", "-y",
        *audio_inputs,
        "-filter_complex", filter_complex,
        "-map", "[v_final]",
        "-map", final_a,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{duration:.2f}",
        str(out)
    ]

    print("\n[Snickerly Engine] Rendering video via FFmpeg...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ FFmpeg error: {res.stderr[-1000:]}")
        raise RuntimeError(f"FFmpeg failed: {res.stderr[-400:]}")

    file_size_mb = out.stat().st_size / (1024 * 1024)
    print(f"🎉 [Snickerly Engine] SUCCESS! Saved to: {out.name} ({file_size_mb:.2f}MB)")
    return str(out)
