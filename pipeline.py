"""
Master Automation Pipeline for YouTube Shorts
Dark Curiosity & Science Facts Niche
Supports both Local Runs and Headless Cloud Execution (GitHub Actions)
"""

import os
import sys
import json
import asyncio
import random
import subprocess
import requests
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Curated high-retention topics pool (fallback if LLM API is unavailable)
TOPICS_POOL = [
    {
        "title": "Can Total Silence Actually Kill You? #Shorts",
        "script": (
            "What in the actual hell happens if you sit inside a room so quiet you can hear your own eyeballs moving? "
            "Inside Microsoft's anechoic chamber, background noise drops to minus twenty decibels, which is quieter than complete silence. "
            "Within two minutes, your ears start freaking out. "
            "Suddenly, your heartbeat sounds like a damn bass drum blasting inside your skull. "
            "You can literally hear your lungs wheezing and your blood rushing through your veins. "
            "Without any sound, your brain gets paranoid and starts hallucinating phantom noises just to screw with you. "
            "The longest anyone ever survived in total darkness here is forty-five minutes before losing their damn mind. "
            "Would you survive an hour for a million bucks, or would you cry like a baby? "
            "Drop a comment and follow, you coward."
        ),
        "tags": ["Shorts", "ScienceFacts", "DarkCuriosity", "AnechoicChamber", "Psychology", "DidYouKnow"],
        "description": "Inside the quietest room on Earth, silence is deadly. #Shorts #DarkCuriosity #Science #Minecraft"
    },
    {
        "title": "The Poison Lake That Turns Animals to Stone #Shorts",
        "script": (
            "Nature is terrifying, and Lake Natron in Tanzania is absolute proof. "
            "The water here reaches temperatures of one hundred and forty degrees Fahrenheit, with an alkalinity close to pure ammonia. "
            "The lake is loaded with sodium carbonate, the exact chemical ancient Egyptians used to mummify pharaohs. "
            "Any bird or bat that crashes into the toxic surface gets calcified and turned into actual petrified stone. "
            "Local photographers find dead flamingos washed ashore looking like creepy Halloween statues frozen in time. "
            "Swimming in this water will literally strip your skin right off your bones in minutes. "
            "Would you dare dip a toe in this death trap for ten grand? "
            "Tell me in the comments and subscribe for more dark science."
        ),
        "tags": ["Shorts", "ScienceFacts", "DarkCuriosity", "LakeNatron", "TerrifyingNature", "DidYouKnow"],
        "description": "This lake literally turns living creatures into stone. #Shorts #DarkCuriosity #Science #Nature"
    },
    {
        "title": "The Russian Sleep Experiment: What Actually Happened? #Shorts",
        "script": (
            "In nineteen forty-seven, researchers supposedly kept five prisoners awake for fifteen straight days using an experimental gas. "
            "By day five, the test subjects started screaming so hard their vocal cords literally tore apart. "
            "By day nine, the screaming stopped completely, replaced by eerie, dead silence. "
            "When soldiers finally broke into the sealed chamber, the horror was beyond comprehension. "
            "The prisoners had severely mutilated their own flesh, begging researchers not to turn the stimulant gas off. "
            "They claimed staying awake was the only thing holding back the monster inside their heads. "
            "While heavily debated as a legend, extreme sleep deprivation does cause severe psychosis within days. "
            "How long have you ever stayed awake before losing your mind? "
            "Subscribe if you actually enjoy sleep."
        ),
        "tags": ["Shorts", "ScienceFacts", "DarkCuriosity", "SleepDeprivation", "UrbanLegend", "Psychology"],
        "description": "What happens when the human mind never sleeps? #Shorts #DarkCuriosity #Psychology"
    }
]

def sec_to_ass(sec):
    hrs = int(sec // 3600)
    mins = int((sec % 3600) // 60)
    secs = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    return f"{hrs:01d}:{mins:02d}:{secs:02d}.{cs:02d}"

async def generate_speech_and_subs(script_text: str, mp3_path: Path, ass_path: Path):
    """
    Generate speech with Edge-TTS and word-by-word timestamps for ASS subtitles.
    """
    import edge_tts
    print(f"[TTS] Generating speech with Edge-TTS (en-US-ChristopherNeural)...")
    comm = edge_tts.Communicate(
        text=script_text,
        voice="en-US-ChristopherNeural",
        rate="+5%",
        pitch="-1Hz",
        boundary="WordBoundary"
    )
    
    words_data = []
    with open(mp3_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                offset_sec = chunk["offset"] / 10_000_000
                duration_sec = chunk["duration"] / 10_000_000
                word = chunk["text"].strip()
                if word:
                    words_data.append({
                        "start": offset_sec,
                        "end": offset_sec + duration_sec,
                        "word": word
                    })

    print(f"[TTS] Captured {len(words_data)} words with exact boundary timestamps.")

    # Smooth out tiny gaps between words so subtitle text doesn't flicker
    for i in range(len(words_data) - 1):
        gap = words_data[i+1]["start"] - words_data[i]["end"]
        if 0 < gap < 0.25:
            words_data[i]["end"] = words_data[i+1]["start"]

    # ASS Header: Arial Black, 70pt, Bright Yellow (&H0000FFFF), Thick Black Stroke (7.5px)
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,70,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7.5,3.0,8,30,30,890,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = []
    for w in words_data:
        dialogues.append(
            f"Dialogue: 0,{sec_to_ass(w['start'])},{sec_to_ass(w['end'])},Default,,0,0,0,,{w['word'].upper()}"
        )

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(dialogues))

    total_duration = words_data[-1]["end"] + 0.8 if words_data else 45.0
    print(f"[TTS] Subtitles saved to {ass_path}. Audio duration: {total_duration:.2f}s")
    return total_duration

def get_audio_duration(file_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def render_short_video(bg_video: Path, mp3_path: Path, ass_path: Path, duration: float, out_video: Path):
    """
    Renders 1080x1920 vertical video with centered card + 1-word-at-a-time ASS subtitles.
    """
    print(f"[FFmpeg] Rendering final video ({duration:.2f}s) to {out_video}...")
    
    # Path formatting for ASS filter across Windows / Linux
    ass_path_str = str(ass_path).replace("\\", "/").replace(":", "\\:")
    
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", str(bg_video),
        "-i", str(mp3_path),
        "-t", f"{duration:.2f}",
        "-filter_complex",
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,ass='{ass_path_str}'[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(out_video)
    ]
    
    subprocess.run(cmd, check=True)
    print(f"[FFmpeg] Finished rendering: {out_video}")

def main():
    print("==================================================")
    print("🚀 STARTING AUTOMATED VIRAL SHORTS PIPELINE")
    print("==================================================")
    
    # 1. Select Topic
    chosen_topic = random.choice(TOPICS_POOL)
    print(f"[Pipeline] Selected Topic: {chosen_topic['title']}")

    # 2. Generate Voice & Word-by-Word Subtitles
    mp3_file = OUTPUT_DIR / "daily_audio.mp3"
    ass_file = OUTPUT_DIR / "daily_subs.ass"
    out_video = OUTPUT_DIR / "daily_viral_short.mp4"
    
    duration = asyncio.run(generate_speech_and_subs(chosen_topic["script"], mp3_file, ass_file))

    # 3. Choose Background Gameplay Video
    bg_video = ASSETS_DIR / "bg_minecraft_60s.mp4"
    if not bg_video.exists():
        bg_video = ASSETS_DIR / "minecraft_parkour.mp4"
    
    if not bg_video.exists():
        raise FileNotFoundError(f"Missing background gameplay video in {ASSETS_DIR}")

    # 4. Render Final Video
    render_short_video(bg_video, mp3_file, ass_file, duration, out_video)

    # 5. Upload to YouTube
    privacy = os.environ.get("UPLOAD_PRIVACY", "public")
    print(f"[Pipeline] Uploading to YouTube with privacy='{privacy}'...")
    
    from youtube_uploader import upload_video
    upload_video(
        file_path=str(out_video),
        title=chosen_topic["title"],
        description=chosen_topic["description"],
        tags=chosen_topic["tags"],
        privacy_status=privacy
    )
    
    print("==================================================")
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    main()
