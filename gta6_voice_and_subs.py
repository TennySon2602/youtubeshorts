"""
GTA VI Narration & Dynamic Word-by-Word Subtitle Generator
Uses Microsoft Edge TTS for high-retention narration and word-boundary synchronization.
"""

import json
import asyncio
from pathlib import Path
import edge_tts

VOICE = "en-US-ChristopherNeural"  # Deep, documentary-style voice
RATE = "+6%"
PITCH = "-2Hz"

def sec_to_ass(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"

async def generate_gta6_speech_and_timing(topic: dict, mp3_path: Path, ass_path: Path):
    """
    Synthesizes speech for all scenes and builds word-by-word synchronized ASS subtitles.
    """
    full_text = " ".join(topic["scenes"])
    communicate = edge_tts.Communicate(full_text, VOICE, rate=RATE, pitch=PITCH, boundary="WordBoundary")

    words = []
    with open(mp3_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({
                    "word": chunk["text"],
                    "start": chunk["offset"] / 10_000_000,
                    "end": (chunk["offset"] + chunk["duration"]) / 10_000_000
                })

    # Calculate exact duration per scene
    scene_durations = []
    word_idx = 0
    current_time = 0.0

    for scene_idx, scene in enumerate(topic["scenes"]):
        cleaned_words = [w.strip(".,!?:;\"'()[]") for w in scene.split() if w.strip(".,!?:;\"'()[]")]
        target_last_word = cleaned_words[-1].lower() if cleaned_words else ""
        
        found_end = current_time + 4.5
        while word_idx < len(words):
            cur_w = words[word_idx]["word"].lower().rstrip('.?!,;"')
            if cur_w == target_last_word:
                found_end = words[word_idx]["end"]
                word_idx += 1
                break
            word_idx += 1

        dur = max(found_end - current_time, 2.5)
        scene_durations.append(dur)
        current_time = found_end

    # Build ASS Subtitle File: Placed below the gameplay box (y ~ 1180)
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,65,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7.5,3.0,8,30,30,1180,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = []
    for w in words:
        clean_word = w["word"].upper().strip()
        dialogues.append(
            f"Dialogue: 0,{sec_to_ass(w['start'])},{sec_to_ass(w['end'])},Default,,0,0,0,,{clean_word}"
        )

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(dialogues))

    total_len = words[-1]["end"] + 0.5 if words else sum(scene_durations)
    return scene_durations, total_len

if __name__ == "__main__":
    from gta6_lore_engine import get_gta6_topic
    t = get_gta6_topic("lucia_ankle_monitor")
    mp3 = Path("output/test_speech.mp3")
    ass = Path("output/test_subs.ass")
    mp3.parent.mkdir(parents=True, exist_ok=True)
    durs, total = asyncio.run(generate_gta6_speech_and_timing(t, mp3, ass))
    print(f"Generated speech ({total:.2f}s), durations:", durs)
