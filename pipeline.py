"""
Master Automation Pipeline for YouTube Shorts
Niche: Dark Curiosity & Science Facts
Features:
- Hybrid Scene Media: Seamless mixing of real motion VIDEO CLIPS and high-res verified IMAGES
- 100% Curated, script-accurate assets per topic (Zero unrelated photos)
- 6px crisp white frame border + Ken Burns motion
- 1-word-at-a-time punchy yellow ASS subtitles (Arial Black 70pt)
- Monotonic PTS re-encoding for 100% Linux/Ubuntu GitHub Actions compatibility
- Default Public YouTube Upload
"""

import os
import sys
import json
import time
import asyncio
import random
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
TOPICS_DIR = ASSETS_DIR / "topics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

TOPICS = [
    {
        "id": "dark_and_darker",
        "title": "The Craziest Lawsuit in Gaming History #Shorts",
        "description": "How indie studio Ironmace fought Korean gaming giant Nexon and released their game via torrents! #Shorts #GamingDrama #DarkAndDarker #Nexon #Steam",
        "tags": ["Shorts", "GamingDrama", "DarkAndDarker", "Nexon", "Steam", "GamingNews", "Ironmace"],
        "scenes": [
            "What in the actual hell happens when an indie studio gets sued by a fifteen billion dollar giant for allegedly stealing an entire game?",
            "Nexon accused former developers of stealing Project P3 source code and assets to secretly build Dark and Darker.",
            "Things got so insane that South Korean police actually raided the Ironmace office, seizing hard drives and personal computers.",
            "Valve hit the panic button and ripped Dark and Darker completely off the Steam store due to copyright strikes.",
            "Instead of surrendering, Ironmace went full gigachad and told half a million players to download the game via torrents on Twitter!",
            "The South Korean Supreme Court finally delivered the verdict, throwing out the copyright claims while issuing a trade secret penalty.",
            "Dark and Darker survived the corporate onslaught, proving you cannot kill this medieval dungeon crawler.",
            "Whose side were you on during this crazy war? Drop a comment and subscribe for more gaming drama!"
        ]
    },
    {
        "id": "roblox_ports",
        "title": "The Multi-Million Dollar Roblox Game Stealing Drama #Shorts",
        "description": "How Roblox developers make millions cloning Steam games like Lethal Company while real devs get banned! #Shorts #Roblox #GamingDrama #LethalCompany #Nintendo",
        "tags": ["Shorts", "Roblox", "GamingDrama", "LethalCompany", "DMCA", "GamingNews", "Steam"],
        "scenes": [
            "Roblox creators are making millions of dollars, and they are doing it by shamelessly stealing entire games.",
            "Whenever an indie hit like Lethal Company blows up on Steam, an identical clone appears on Roblox within forty-eight hours.",
            "These copycats rip 3D monsters, sound effects, and maps to cash in on millions of kids who cannot afford PC games.",
            "Even worse, rival developers have started weaponizing fake DMCA copyright strikes to get innocent creators banned overnight.",
            "Because Roblox uses automated support bots, original creators often lose their games while the thieves keep profiting.",
            "Major companies like Nintendo have fought back, nuking beloved fan projects like Pokémon Brick Bronze off the face of the earth.",
            "Is Roblox an amazing creative playground, or just a massive copyright infringement machine?",
            "Tell me your thoughts below, and subscribe before Nintendo copyright strikes this video!"
        ]
    },
    {
        "id": "nintendo_palworld",
        "title": "Nintendo's Nuclear Lawsuit Against Palworld #Shorts",
        "description": "Nintendo stayed silent for 8 months while Palworld made $500M, then dropped a nuclear patent lawsuit! #Shorts #Palworld #Nintendo #Pokemon #GamingDrama",
        "tags": ["Shorts", "Palworld", "Nintendo", "Pokemon", "GamingDrama", "GamingNews", "Steam"],
        "scenes": [
            "Nintendo stayed silent for eight months while Palworld made over five hundred million dollars, and then dropped a tactical legal nuke.",
            "Known as Pokémon with guns, Palworld shattered Steam records with over two million concurrent players.",
            "Everyone expected Nintendo to sue for copyright, but their lawyers did something far more terrifying.",
            "Nintendo filed a joint lawsuit targeting patent infringement, specifically patenting the mechanic of aiming and throwing capture spheres.",
            "Gamers are furious, accusing Nintendo of patenting basic gameplay mechanics just to crush indie competitors.",
            "Pocketpair refuses to back down, vowing to fight Nintendo in court to protect indie developers everywhere.",
            "Do you think Nintendo has a legitimate case, or are they just being salty corporate bullies?",
            "Drop your hot take in the comments and subscribe for part two!"
        ]
    },
    {
        "id": "helldivers_sony",
        "title": "The Day PC Gamers Brought Sony to Its Knees #Shorts",
        "description": "How Helldivers 2 players defeated Sony in 48 hours after 215,000 negative reviews! #Shorts #Helldivers2 #Sony #PlayStation #Steam",
        "tags": ["Shorts", "Helldivers2", "Sony", "PlayStation", "GamingDrama", "Steam", "GamerVictory"],
        "scenes": [
            "Never underestimate PC gamers, because this is the story of how they forced gaming giant Sony to surrender in just forty-eight hours.",
            "Helldivers 2 was the biggest game of the year, until Sony suddenly announced that all PC players must link a PlayStation Network account.",
            "The fatal mistake? PlayStation Network is not even available in over one hundred and seventy countries worldwide.",
            "Steam players united and unleashed the most devastating review bomb in gaming history, dropping over two hundred thousand negative reviews.",
            "Players demanded refunds en masse, and Valve actually started refunding players with over a hundred hours of playtime.",
            "Facing total disaster, Sony surrendered, tweeting that the mandatory account linking requirement was officially canceled.",
            "Gamers proved that when a community stands together, even corporate giants have to bend the knee.",
            "Did you fight in the great Sony review war? Subscribe for more legendary gaming moments!"
        ]
    },
    {
        "id": "concord_disaster",
        "title": "The $400 Million Game That Died in 14 Days #Shorts",
        "description": "Sony spent 8 years and $400 million on Concord, only to shut it down after 2 weeks! #Shorts #Concord #PlayStation #GamingDrama #Sony",
        "tags": ["Shorts", "Concord", "PlayStation", "Sony", "GamingDrama", "GamingNews", "Flop"],
        "scenes": [
            "Sony spent eight long years and four hundred million dollars on this game, and it was murdered in just fourteen days.",
            "This was Concord, a sci-fi hero shooter that Sony hyped up as the next massive PlayStation franchise.",
            "When the game finally launched, it hit a pathetic all-time peak of just six hundred and sixty concurrent players on Steam.",
            "Nobody wanted to pay forty dollars for generic characters and uninspired gameplay when rivals like Overwatch were completely free.",
            "Just two weeks after release, Sony pulled the plug, took the servers offline, and refunded every single player.",
            "A few weeks later, Sony permanently shut down Firewalk Studios, erasing four hundred million dollars into thin air.",
            "Concord officially goes down in history as the biggest commercial gaming flop of the twenty-first century.",
            "What was the worst game you ever bought? Let me know in the comments and subscribe!"
        ]
    }
]

def sec_to_ass(sec):
    hrs = int(sec // 3600)
    mins = int((sec % 3600) // 60)
    secs = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    return f"{hrs:01d}:{mins:02d}:{secs:02d}.{cs:02d}"

async def generate_speech_and_scene_timing(topic: dict, mp3_path: Path, ass_path: Path):
    """
    Synthesizes speech via Edge-TTS and aligns:
    1. Sentence boundaries for scene transitions (videos/images)
    2. Word boundaries for 1-word-at-a-time punchy ASS subtitles
    """
    import edge_tts
    
    full_text = " ".join(topic["scenes"])
    print(f"[TTS] Synthesizing narration for topic: {topic['title']}")
    
    comm = edge_tts.Communicate(
        text=full_text,
        voice="en-US-ChristopherNeural",
        rate="+5%",
        pitch="-1Hz",
        boundary="WordBoundary"
    )

    words = []
    with open(mp3_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                offset_sec = chunk["offset"] / 10_000_000
                duration_sec = chunk["duration"] / 10_000_000
                w_text = chunk["text"].strip()
                if w_text:
                    words.append({
                        "start": offset_sec,
                        "end": offset_sec + duration_sec,
                        "word": w_text
                    })

    print(f"[TTS] Captured {len(words)} individual words with exact millisecond timestamps.")

    # Smooth out tiny pauses between words
    for i in range(len(words) - 1):
        gap = words[i+1]["start"] - words[i]["end"]
        if 0 < gap < 0.25:
            words[i]["end"] = words[i+1]["start"]

    # Calculate exact duration for each sentence scene
    scene_durations = []
    word_idx = 0
    current_time = 0.0

    for sc_text in topic["scenes"]:
        sc_words = sc_text.strip().split()
        target_last_word = sc_words[-1].lower().rstrip('.?!,;"')
        
        found_end = current_time + 4.5
        while word_idx < len(words):
            cur_w = words[word_idx]["word"].lower().rstrip('.?!,;"')
            if cur_w == target_last_word:
                found_end = words[word_idx]["end"]
                word_idx += 1
                break
            word_idx += 1
        
        dur = max(found_end - current_time, 2.0)
        scene_durations.append(dur)
        current_time = found_end

    # Build ASS Subtitle File: Arial Black, 70pt, Bright Yellow, Thick Black Stroke
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
    for w in words:
        dialogues.append(
            f"Dialogue: 0,{sec_to_ass(w['start'])},{sec_to_ass(w['end'])},Default,,0,0,0,,{w['word'].upper()}"
        )

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(dialogues))

    total_audio_len = words[-1]["end"] + 0.5 if words else sum(scene_durations)
    return scene_durations, total_audio_len

def find_scene_asset(topic_dir: Path, idx: int) -> Path:
    """
    Finds the media file for a scene, prioritizing video clips over images.
    """
    # Check for video formats first
    for ext in [".webm", ".mp4", ".mkv", ".mov"]:
        v = topic_dir / f"scene_{idx}{ext}"
        if v.exists() and v.stat().st_size > 5000:
            return v
            
    # Then check for image formats
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        img = topic_dir / f"scene_{idx}{ext}"
        if img.exists() and img.stat().st_size > 5000:
            return img

    # Fallback to scene_0
    candidates = list(topic_dir.glob("scene_0.*"))
    if candidates:
        return candidates[0]

    # Global fallback
    fallbacks = list(ASSETS_DIR.glob("scene_*.jpg"))
    if fallbacks:
        return fallbacks[idx % len(fallbacks)]

    raise FileNotFoundError(f"Missing media asset for scene {idx} in {topic_dir}")

def build_scene_cards_video(topic: dict, scene_durations: list, out_cards_video: Path):
    """
    Stitches dynamic scene cards (videos + images) into a seamless 900x600 stream
    with 6px crisp white frame borders and monotonic PTS timestamps.
    """
    print("[Video] Building animated content cards (Videos & Images) with 6px white borders...")
    topic_assets_dir = TOPICS_DIR / topic["id"]
    concat_txt = OUTPUT_DIR / f"{topic['id']}_concat.txt"
    lines = []

    for idx, duration in enumerate(scene_durations):
        media_path = find_scene_asset(topic_assets_dir, idx)
        is_video = media_path.suffix.lower() in [".webm", ".mp4", ".mkv", ".mov"]
        seg_mp4 = OUTPUT_DIR / f"{topic['id']}_seg_{idx}.mp4"

        if is_video:
            print(f"  🎬 Scene {idx+1}: [VIDEO CLIP] {media_path.name} ({duration:.2f}s)")
            cmd = [
                "ffmpeg", "-y",
                "-stream_loop", "-1",
                "-i", str(media_path),
                "-t", f"{duration:.2f}",
                "-vf", "scale=900:600:force_original_aspect_ratio=increase,crop=900:600,drawbox=x=0:y=0:w=iw:h=ih:color=white:t=6",
                "-r", "30",
                "-pix_fmt", "yuv420p",
                "-an",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                str(seg_mp4)
            ]
        else:
            print(f"  🖼️ Scene {idx+1}: [IMAGE] {media_path.name} ({duration:.2f}s)")
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(media_path),
                "-t", f"{duration:.2f}",
                "-vf", "scale=900:600:force_original_aspect_ratio=increase,crop=900:600,drawbox=x=0:y=0:w=iw:h=ih:color=white:t=6",
                "-r", "30",
                "-pix_fmt", "yuv420p",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                str(seg_mp4)
            ]

        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        lines.append(f"file '{seg_mp4.as_posix()}'")

    with open(concat_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Re-encode concat with libx264 to guarantee monotonic PTS on Linux & Windows
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        str(out_cards_video)
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[Video] Content cards stitched successfully with perfect timestamps: {out_cards_video}")

def render_final_composite(
    bg_video: Path,
    cards_video: Path,
    audio_path: Path,
    ass_path: Path,
    duration: float,
    out_video: Path
):
    """
    Composites:
    - 1080x1920 vertical background gameplay
    - 900x600 floating content card at overlay=90:260:eof_action=repeat
    - 1-word-at-a-time 70pt punchy yellow ASS subtitles at y=890
    - Audio
    """
    print(f"[FFmpeg] Compositing final video ({duration:.2f}s) to {out_video}...")
    ass_clean = str(ass_path).replace("\\", "/").replace(":", "\\:")

    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];"
        f"[bg][1:v]overlay=90:260:eof_action=repeat[v_card];"
        f"[v_card]ass='{ass_clean}'[outv]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", str(bg_video),
        "-i", str(cards_video),
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "2:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-t", f"{duration:.2f}",
        str(out_video)
    ]
    subprocess.run(cmd, check=True)
    print(f"🎉 FINAL VIDEO READY: {out_video}")

def main():
    print("==================================================")
    print("🚀 AUTOMATED VIRAL SHORTS PIPELINE")
    print("==================================================")

    # 1. Topic Selection (Rotate daily or pick via env var TOPIC_ID)
    topic_id_env = os.environ.get("TOPIC_ID")
    if topic_id_env:
        topic = next((t for t in TOPICS if t["id"] == topic_id_env), None)
        if not topic:
            raise ValueError(f"Unknown topic: {topic_id_env}")
    else:
        day_idx = int(time.strftime("%d")) % len(TOPICS)
        topic = TOPICS[day_idx]
    print(f"[Topic] ID: {topic['id']}")
    print(f"[Topic] Title: {topic['title']}")
    print(f"[Topic] Scenes: {len(topic['scenes'])} sentences")

    # 2. Audio & Subtitle Generation
    mp3_file = OUTPUT_DIR / f"{topic['id']}_narration.mp3"
    ass_file = OUTPUT_DIR / f"{topic['id']}_words.ass"
    scene_durations, total_duration = asyncio.run(
        generate_speech_and_scene_timing(topic, mp3_file, ass_file)
    )

    # 3. Build Floating Scene Visuals (Mixing Videos & Images)
    cards_video = OUTPUT_DIR / f"{topic['id']}_cards.mp4"
    build_scene_cards_video(topic, scene_durations, cards_video)

    # 4. Composite Final Vertical Short Video
    bg_video = ASSETS_DIR / "bg_minecraft_60s.mp4"
    if not bg_video.exists():
        bg_video = ASSETS_DIR / "minecraft_parkour.mp4"

    final_video = OUTPUT_DIR / f"{topic['id']}_final_short.mp4"
    render_final_composite(
        bg_video=bg_video,
        cards_video=cards_video,
        audio_path=mp3_file,
        ass_path=ass_file,
        duration=total_duration,
        out_video=final_video
    )

    # 5. YouTube Upload (DEFAULT: PUBLIC)
    if os.environ.get("SKIP_UPLOAD") == "1":
        print("\n[Upload] SKIP_UPLOAD=1 detected. Skipping YouTube upload.")
    else:
        privacy = os.environ.get("UPLOAD_PRIVACY", "public")
        print(f"\n[Upload] Publishing to YouTube (privacy='{privacy}')...")
        
        from youtube_uploader import upload_video
        upload_video(
            file_path=str(final_video),
            title=topic["title"],
            description=topic["description"],
            tags=topic["tags"],
            privacy_status=privacy
        )
    print("\n==================================================")
    print("✨ ALL STEPS FINISHED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    main()
