"""
Snickerly-Style AI Video Editor for Streamer Highlights
Emulates @NotSnickerly editing aesthetics:
1. 9:16 Vertical Dual Split or Dynamic Pan & Scan
2. Minecraft Drinking / Eating SFX on consumption moments
3. Vine Boom + Punch-in zoom on shock/awkward moments
4. Grayscale/Desaturation filter + Lo-Fi Wholesome BGM on sweet/emotional moments
5. Kinetic Pop Subtitles (Word-by-word bold ASS karaoke)
6. Streamer watermark/credit banner
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

def build_snickerly_ass_subtitles(dialogue_events: list, ass_path: Path, hook_title: str = "", streamer_name: str = "", duration: float = 30.0):
    """
    Builds mobile-first Snickerly style ASS subtitles:
    - Extra bold font, bright yellow/white, heavy black outline
    - 2-4 words per line, centered in lower third
    - Includes top hook banner and bottom creator attribution via pure libass
    """
    ass_header = """[Script Info]
Title: Snickerly Streamer Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SnickerlyWord,Impact,82,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,105,105,2,0,1,8,2,2,40,40,480,1
Style: SnickerlyPunch,Impact,92,&H000055FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,115,115,3,0,1,9,4,2,40,40,480,1
Style: HookHeader,Arial,60,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,7,3,8,40,40,160,1
Style: CreditTag,Arial,40,&H0000FFCC,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,2,1,40,40,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    def fmt(t):
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = t % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    lines = [ass_header]
    
    # 1. Top Hook Banner across entire video
    if hook_title:
        lines.append(f"Dialogue: 0,0:00:00.00,{fmt(duration)},HookHeader,,0,0,0,,{hook_title.upper()}\n")

    # 2. Bottom Credit attribution
    if streamer_name:
        lines.append(f"Dialogue: 0,0:00:00.00,{fmt(duration)},CreditTag,,0,0,0,,CLIP VIA @{streamer_name.upper()}\n")

    # 3. Synchronized Dialogues
    for d in dialogue_events:
        start_t = d["start"]
        end_t = d["end"]
        text = d["text"].upper()
        style = "SnickerlyPunch" if d.get("punch") else "SnickerlyWord"
        lines.append(f"Dialogue: 1,{fmt(start_t)},{fmt(end_t)},{style},,0,0,0,,{text}\n")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"✅ Generated Snickerly ASS Subtitles: {ass_path.name}")

def render_snickerly_video(
    source_video: str,
    output_path: str,
    streamer_name: str,
    hook_title: str,
    events: list = None,
    dialogues: list = None,
    layout_mode: str = "dynamic_reframe"
):
    """
    Renders the complete Snickerly Short:
    - events: List of special SFX/Visual cues:
      {"type": "drink", "time": 3.5}
      {"type": "eat", "time": 8.0}
      {"type": "vine_boom", "time": 12.0, "zoom": True}
      {"type": "wholesome", "start": 16.0, "end": 22.0}
    """
    src = Path(source_video)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    events = events or []
    dialogues = dialogues or []

    # 1. Inspect source video dimensions and duration
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration:stream=width,height",
        "-of", "json", str(src)
    ]
    probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
    probe_data = json.loads(probe_res.stdout)
    duration = min(float(probe_data["format"]["duration"]), 18.0) # Cap test at 18s for speedy rendering
    width = int(probe_data["streams"][0]["width"])
    height = int(probe_data["streams"][0]["height"])

    # Create temporary ASS file
    ass_file = out.parent / f"{out.stem}_snickerly.ass"
    build_snickerly_ass_subtitles(
        dialogue_events=dialogues,
        ass_path=ass_file,
        hook_title=hook_title,
        streamer_name=streamer_name,
        duration=duration
    )

    print(f"[Snickerly Engine] Source: {src.name} ({width}x{height}, {duration:.2f}s)")
    print(f"[Snickerly Engine] Layout: {layout_mode} | Streamer: {streamer_name}")

    # Build audio inputs and delays
    audio_inputs = ["-i", str(src)]
    amix_filters = ["[0:a]volume=1.0[main_a]"]
    mix_sources = ["[main_a]"]
    input_idx = 1

    # Track filter chains for video
    # Base 9:16 vertical crop: scale 1920x1080 to height 1920 (width 3413) then crop center 1080x1920
    video_filters = []
    video_filters.append("[0:v]scale=-1:1920,crop=1080:1920:(in_w-1080)/2:0,setsar=1[v_base]")
    curr_v = "[v_base]"

    # Apply Wholesome grayscale filter if requested
    for ev in events:
        if ev.get("type") == "wholesome":
            w_start = ev.get("start", 0)
            w_end = ev.get("end", duration)
            video_filters.append(
                f"{curr_v}hue=s=if(between(t\\,{w_start}\\,{w_end})\\,0.1\\,1.0)[v_hue]"
            )
            curr_v = "[v_hue]"
            # Add wholesome lo-fi music ducked
            if WHOLESOME_BGM.exists():
                audio_inputs.extend(["-i", str(WHOLESOME_BGM)])
                delay_ms = int(w_start * 1000)
                dur = w_end - w_start
                amix_filters.append(
                    f"[{input_idx}:a]atrim=0:{dur},adelay={delay_ms}|{delay_ms},volume=0.35[a_wholesome]"
                )
                mix_sources.append("[a_wholesome]")
                input_idx += 1

        elif ev.get("type") == "drink":
            t = ev.get("time", 0)
            if MINECRAFT_DRINK.exists():
                audio_inputs.extend(["-i", str(MINECRAFT_DRINK)])
                delay_ms = int(t * 1000)
                amix_filters.append(
                    f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},volume=1.2[a_drink]"
                )
                mix_sources.append("[a_drink]")
                input_idx += 1

        elif ev.get("type") == "eat":
            t = ev.get("time", 0)
            if MINECRAFT_EAT.exists():
                audio_inputs.extend(["-i", str(MINECRAFT_EAT)])
                delay_ms = int(t * 1000)
                amix_filters.append(
                    f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},volume=1.2[a_eat]"
                )
                mix_sources.append("[a_eat]")
                input_idx += 1

        elif ev.get("type") == "vine_boom":
            t = ev.get("time", 0)
            if VINE_BOOM.exists():
                audio_inputs.extend(["-i", str(VINE_BOOM)])
                delay_ms = int(t * 1000)
                amix_filters.append(
                    f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},volume=1.5[a_boom]"
                )
                mix_sources.append("[a_boom]")
                input_idx += 1

            # Punch-in zoom for 1.0 second on Vine Boom
            if ev.get("zoom", True):
                z_start = t
                z_end = min(duration, t + 1.2)
                video_filters.append(
                    f"{curr_v}scale=w=1080:h=1920:eval=frame,crop=w='if(between(t\\,{z_start}\\,{z_end})\\,900\\,1080)':h='if(between(t\\,{z_start}\\,{z_end})\\,1600\\,1920)':x='(in_w-out_w)/2':y='(in_h-out_h)/2',scale=1080:1920[v_punch]"
                )
                curr_v = "[v_punch]"

    # Subtitles burn-in + Top Banner text + Bottom Credit via libass
    ass_escaped = str(ass_file).replace("\\", "/").replace(":", "\\:")
    video_filters.append(f"{curr_v}ass='{ass_escaped}'[v_final]")

    # Audio mix
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
        "-crf", "18",
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

if __name__ == "__main__":
    # Test execution with GTA trailer footage
    test_src = Path("assets/gtavi/source_gta6_trailer.mp4")
    if test_src.exists():
        test_out = Path("stream_clipper/output/snickerly_test_demo.mp4")
        test_events = [
            {"type": "drink", "time": 2.0},
            {"type": "vine_boom", "time": 6.5, "zoom": True},
            {"type": "wholesome", "start": 9.0, "end": 13.0},
            {"type": "eat", "time": 14.5}
        ]
        test_dialogues = [
            {"start": 0.5, "end": 2.2, "text": "BRO HE REALLY DRANK THAT 💀", "punch": False},
            {"start": 2.5, "end": 6.0, "text": "WAIT WHAT DID HE SAY?", "punch": False},
            {"start": 6.5, "end": 8.5, "text": "HE DID NOT JUST DO THAT 😭", "punch": True},
            {"start": 9.0, "end": 13.0, "text": "OKAY THIS IS ACTUALLY WHOLESOME ❤️", "punch": False},
            {"start": 13.5, "end": 17.0, "text": "WAIT FOR THE ENDING BROOO", "punch": True}
        ]
        render_snickerly_video(
            source_video=str(test_src),
            output_path=str(test_out),
            streamer_name="KaiCenat",
            hook_title="KAI CENAT REACTS TO GTA 6 💀",
            events=test_events,
            dialogues=test_dialogues
        )
    else:
        print("Source video not found for test.")
