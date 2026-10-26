import subprocess
import os

ASSETS_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation\assets"
OUTPUT_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation\output"
FFMPEG = os.path.expanduser(r"~\scoop\shims\ffmpeg.exe")

clips = [
    "clip_chamber.mp4.mkv",
    "clip_heart.mp4.mkv",
    "clip_brain.mp4.webm",
    "clip_clock.mp4.webm",
    "minecraft_parkour.mp4"
]

for c in clips:
    in_path = os.path.join(ASSETS_DIR, c)
    out_path = os.path.join(OUTPUT_DIR, f"check_{os.path.splitext(c)[0]}.jpg")
    cmd = [
        FFMPEG, "-y",
        "-ss", "00:00:03",
        "-i", in_path,
        "-vframes", "1",
        out_path
    ]
    subprocess.run(cmd, check=True)
    print(f"Extracted: {out_path}")
