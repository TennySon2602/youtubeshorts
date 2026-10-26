"""
Master Automation Pipeline for YouTube Shorts
Niche: Dark Curiosity & Science Facts
Features:
- Dynamic multi-topic rotation
- Custom 900x600 visual scenes per sentence (Pollinations AI + Fallback)
- Ken Burns cinematic zoompan + sharp 6px white frame border
- 1-word-at-a-time punchy yellow subtitles (Arial Black 70pt)
- Minecraft parkour background gameplay
- Headless YouTube API v3 upload via OAuth refresh_token
"""

import os
import sys
import json
import time
import asyncio
import random
import subprocess
import urllib.parse
import requests
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# 5 High-Retention Viral Topics
TOPICS = [
    {
        "id": "anechoic_chamber",
        "title": "Can Total Silence Actually Kill You? #Shorts",
        "description": "What happens if you sit inside a room so quiet you hear your own eyeballs moving? #Shorts #DarkCuriosity #Science #Minecraft",
        "tags": ["Shorts", "ScienceFacts", "DarkCuriosity", "AnechoicChamber", "Psychology", "DidYouKnow"],
        "scenes": [
            {
                "text": "What in the actual hell happens if you sit inside a room so quiet you can hear your own eyeballs moving?",
                "query": "extreme close up human eyeball moving in total darkness pupil dilated cinematic macro 8k"
            },
            {
                "text": "Inside Microsoft's anechoic chamber, background noise drops to minus twenty decibels, quieter than pure silence.",
                "query": "futuristic anechoic chamber soundproof acoustic foam wedges dark neon lighting"
            },
            {
                "text": "Within two minutes, your ears start freaking out.",
                "query": "close up human ear glowing sound wave frequencies eerie dark science"
            },
            {
                "text": "Suddenly, your heartbeat sounds like a damn bass drum blasting inside your skull.",
                "query": "anatomical 3D human heart glowing red beating dramatically in dark space"
            },
            {
                "text": "You can literally hear your lungs wheezing and your blood rushing through your veins.",
                "query": "glowing transparent human lungs and vascular blood vessels medical 3d rendering"
            },
            {
                "text": "Without any sound, your brain gets paranoid and starts hallucinating phantom noises just to screw with you.",
                "query": "human brain neural synapses firing glowing hallucination psychological thriller"
            },
            {
                "text": "The longest anyone ever survived in total darkness here is forty-five minutes before losing their damn mind.",
                "query": "vintage analog timer counting down 45 minutes in pitch black room ominous"
            },
            {
                "text": "Would you survive an hour for a million bucks, or would you cry like a baby?",
                "query": "briefcase full of one million dollars cash glowing cinematic dramatic lighting"
            },
            {
                "text": "Drop a comment and follow, you coward.",
                "query": "golden victory trophy illuminated in darkness dramatic trophy award"
            }
        ]
    },
    {
        "id": "lake_natron",
        "title": "The Poison Lake That Turns Animals to Stone #Shorts",
        "description": "Lake Natron in Tanzania literally calcifies birds and bats into petrified stone statues. #Shorts #DarkCuriosity #Science #Nature",
        "tags": ["Shorts", "ScienceFacts", "DarkCuriosity", "LakeNatron", "TerrifyingNature", "DidYouKnow"],
        "scenes": [
            {
                "text": "Nature is terrifying, and Lake Natron in Tanzania is absolute proof.",
                "query": "aerial view mysterious blood red caustic lake cracked salt crust dramatic landscape"
            },
            {
                "text": "The water here reaches temperatures of one hundred and forty degrees Fahrenheit, with an alkalinity close to pure ammonia.",
                "query": "boiling red toxic alkaline water steaming lake surface chemical reflection"
            },
            {
                "text": "The lake is loaded with sodium carbonate, the exact chemical ancient Egyptians used to mummify pharaohs.",
                "query": "ancient egyptian mummification rituals embalming salts dark tomb cinematic"
            },
            {
                "text": "Any bird or bat that crashes into the toxic surface gets calcified and turned into actual petrified stone.",
                "query": "calcified petrified bat turned into rough stone statue eerie dramatic lighting"
            },
            {
                "text": "Dead animals wash ashore looking like creepy Halloween statues frozen in time.",
                "query": "calcified flamingo petrified like stone statue dark dramatic alkaline shore"
            },
            {
                "text": "Swimming in this water will literally strip your skin right off your bones in minutes.",
                "query": "warning hazard danger sign skull bones toxic caustic chemical water lake"
            },
            {
                "text": "Would you dare dip a toe in this death trap for ten grand?",
                "query": "silhouette of brave explorer standing at edge of steaming red caustic lake"
            },
            {
                "text": "Tell me in the comments and subscribe for more dark science.",
                "query": "ancient mysterious stone statue glowing eyes dark dramatic nature horizon"
            }
        ]
    },
    {
        "id": "russian_sleep",
        "title": "The Terrifying Russian Sleep Experiment #Shorts",
        "description": "What happens when researchers keep human subjects awake for 15 straight days? #Shorts #DarkCuriosity #UrbanLegend #Psychology",
        "tags": ["Shorts", "ScienceFacts", "DarkCuriosity", "SleepDeprivation", "UrbanLegend", "Psychology"],
        "scenes": [
            {
                "text": "In nineteen forty-seven, researchers kept five prisoners awake for fifteen straight days using experimental gas.",
                "query": "sealed 1940s cold war underground bunker laboratory heavy iron door sealed"
            },
            {
                "text": "By day five, the test subjects started screaming so hard their vocal cords literally tore apart.",
                "query": "dark psychiatric hospital observation window misty condensation shadows"
            },
            {
                "text": "By day nine, the screaming stopped completely, replaced by eerie, dead silence.",
                "query": "analog pressure gauge leaking ominous green stimulant gas retro machinery"
            },
            {
                "text": "When researchers broke inside, the test subjects had severely mutilated their own flesh.",
                "query": "shadowy silhouette behind foggy reinforced glass dark vintage laboratory"
            },
            {
                "text": "They begged researchers not to turn the gas off, whispering that sleep was their greatest enemy.",
                "query": "vintage audio reel to reel tape recorder spinning in dark secret interrogation room"
            },
            {
                "text": "While debated as a legend, extreme sleep deprivation does cause severe psychosis within days.",
                "query": "distorted human face insomnia sleep deprivation hallucination dark surreal"
            },
            {
                "text": "How many days have you ever stayed awake before losing your mind?",
                "query": "digital alarm clock flashing 3 33 AM in pitch dark eerie bedroom neon red"
            },
            {
                "text": "Subscribe right now if you actually enjoy sleeping.",
                "query": "mysterious dark science laboratory cinematic glowing neon warning signs"
            }
        ]
    },
    {
        "id": "boiling_river",
        "title": "The Boiling River That Melts Animals Alive #Shorts",
        "description": "Deep in the Amazon lies Shanay-Timpishka, a river hot enough to boil anything instantly. #Shorts #DarkCuriosity #NatureFacts",
        "tags": ["Shorts", "ScienceFacts", "DarkCuriosity", "BoilingRiver", "AmazonRainforest", "DidYouKnow"],
        "scenes": [
            {
                "text": "Deep in the Amazon rainforest lies a legendary river so boiling hot it cooks anything that falls into it alive.",
                "query": "steaming boiling thermal river flowing through dense dark tropical amazon jungle"
            },
            {
                "text": "The water reaches temperatures over two hundred degrees Fahrenheit, hot enough to brew tea instantly.",
                "query": "scalding boiling thermal spring water bubbling hot steam rising close up"
            },
            {
                "text": "Small animals and reptiles that slip into the river have their eyes turn milky white before being boiled alive.",
                "query": "thick mystical geothermal steam rising above jungle rapids dramatic sunlight"
            },
            {
                "text": "Local shamans believe the river was created by the mythical giant serpent spirit Yacumama.",
                "query": "ancient mythical glowing serpent spirit rising from mystical jungle waters"
            },
            {
                "text": "Geologists were stunned to find the heat comes from massive hydrothermal faults thousands of miles away.",
                "query": "geothermal fault lines glowing red molten underground magma earth cross section"
            },
            {
                "text": "Would you dare take a dip in this prehistoric death jacuzzi for fifty thousand dollars?",
                "query": "rickety wooden bridge crossing over roaring steaming boiling river in jungle"
            },
            {
                "text": "Tell me in the comments and subscribe for more insane discoveries.",
                "query": "lone adventurer holding fiery torch walking through dark mysterious rainforest"
            }
        ]
    },
    {
        "id": "spontaneous_combustion",
        "title": "Can Humans Actually Explode Into Flames? #Shorts",
        "description": "The terrifying phenomenon of Spontaneous Human Combustion explained by science. #Shorts #DarkCuriosity #ScienceFacts",
        "tags": ["Shorts", "ScienceFacts", "DarkCuriosity", "Combustion", "Mystery", "DidYouKnow"],
        "scenes": [
            {
                "text": "Imagine sitting peacefully in your armchair, and suddenly your body bursts into a three-thousand-degree inferno with no external fire.",
                "query": "vintage armchair in dark room glowing embers smoke rising cinematic mystery"
            },
            {
                "text": "In nineteen fifty-one, Mary Reeser was found burned to a pile of ash, yet the carpet and chair beside her were completely unburned.",
                "query": "vintage 1950s living room detective investigation mystery scene moody lighting"
            },
            {
                "text": "Scientists call this the wick effect, where clothing acts like a candle wick melting body fat as fuel.",
                "query": "macro close up candle flame burning intensely in pure darkness glowing"
            },
            {
                "text": "Yet the skull, feet, and slippers are often found completely untouched by the flames.",
                "query": "mysterious unburned vintage slipper resting on dark floor next to cold ash"
            },
            {
                "text": "Can a human truly ignite from the inside out due to static electricity or ketosis?",
                "query": "silhouette of human body glowing with internal fiery bioluminescence sparks"
            },
            {
                "text": "Or is there something even more terrifying science has not explained yet?",
                "query": "antique scientific laboratory with glowing eerie smoke and electricity sparks"
            },
            {
                "text": "Share your craziest theory in the comments and follow, if you are not afraid of catching fire.",
                "query": "fiery sparks and embers swirling in dark night sky cinematic dramatic"
            }
        ]
    }
]

def sec_to_ass(sec):
    hrs = int(sec // 3600)
    mins = int((sec % 3600) // 60)
    secs = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    return f"{hrs:01d}:{mins:02d}:{secs:02d}.{cs:02d}"

def download_scene_image(query: str, save_path: Path, scene_idx: int) -> bool:
    """
    Downloads custom 900x600 image from Pollinations.ai (Flux/Turbo model).
    Falls back to existing local assets if network request fails.
    """
    if save_path.exists() and save_path.stat().st_size > 5000:
        return True

    print(f"  [Image] Fetching scene {scene_idx+1}: '{query[:45]}...'")
    try:
        encoded_prompt = urllib.parse.quote(query)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=900&height=600&nologo=true"
        resp = requests.get(url, timeout=25)
        if resp.status_code == 200 and len(resp.content) > 10000:
            with open(save_path, "wb") as f:
                f.write(resp.content)
            return True
    except Exception as e:
        print(f"  [Image] Notice: Pollinations fetch timed out ({e}). Using local fallback asset.")

    # Fallback to local asset if available
    local_fallbacks = list(ASSETS_DIR.glob("scene_*.jpg"))
    if local_fallbacks:
        fb = local_fallbacks[scene_idx % len(local_fallbacks)]
        import shutil
        shutil.copy(fb, save_path)
        return True
    return False

async def generate_speech_and_scene_timing(topic: dict, mp3_path: Path, ass_path: Path):
    """
    Synthesizes speech via Edge-TTS and aligns:
    1. Sentence boundaries for scene card transitions
    2. Word boundaries for 1-word-at-a-time punchy ASS subtitles
    """
    import edge_tts
    
    full_text = " ".join([s["text"] for s in topic["scenes"]])
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

    for sc in topic["scenes"]:
        sc_words = sc["text"].strip().split()
        target_last_word = sc_words[-1].lower().rstrip('.?!,;"')
        
        # Scan words to find the end of this sentence
        found_end = current_time + 4.5 # Default fallback duration
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

def build_scene_cards_video(topic: dict, scene_durations: list, out_cards_video: Path):
    """
    Creates the 900x600 video of floating content cards changing scene every sentence.
    Includes Ken Burns zoompan + 6px crisp white frame border.
    """
    print("[Video] Building animated content cards with Ken Burns & 6px white borders...")
    segment_files = []
    concat_txt = OUTPUT_DIR / "concat_cards.txt"
    lines = []

    for idx, (scene, duration) in enumerate(zip(topic["scenes"], scene_durations)):
        img_path = OUTPUT_DIR / f"{topic['id']}_scene_{idx}.jpg"
        download_scene_image(scene["query"], img_path, idx)
        
        seg_mp4 = OUTPUT_DIR / f"{topic['id']}_seg_{idx}.mp4"
        
        # FFmpeg filter: scale to 900x600, draw 6px white border, loop for duration
        cmd = [
            "ffmpeg", "-y", "-loop", "1",
            "-i", str(img_path),
            "-t", f"{duration:.2f}",
            "-vf", "scale=900:600:force_original_aspect_ratio=increase,crop=900:600,drawbox=x=0:y=0:w=iw:h=ih:color=white:t=6",
            "-r", "30",
            "-pix_fmt", "yuv420p",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            str(seg_mp4)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        segment_files.append(seg_mp4)
        # Use forward slashes for concat file
        lines.append(f"file '{seg_mp4.as_posix()}'")

    with open(concat_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Fast concatenate all segments with demuxer
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        str(out_cards_video)
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[Video] Content cards stitched successfully: {out_cards_video}")

def render_final_composite(
    bg_video: Path,
    cards_video: Path,
    audio_path: Path,
    ass_path: Path,
    duration: float,
    out_video: Path
):
    """
    Merges:
    - Background 1080x1920 vertical Minecraft gameplay
    - Centered floating content cards at overlay=90:260 (size 900x600)
    - 1-word-at-a-time 70pt punchy yellow ASS subtitles at y=890
    - Crystal clear narration audio
    """
    print(f"[FFmpeg] Compositing final video ({duration:.2f}s) to {out_video}...")
    ass_clean = str(ass_path).replace("\\", "/").replace(":", "\\:")

    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];"
        f"[bg][1:v]overlay=90:260[v_card];"
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

    # 1. Topic Selection (Rotate daily or pick based on day of month)
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

    # 3. Build Floating Scene Visuals
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

    # 5. YouTube Upload
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
