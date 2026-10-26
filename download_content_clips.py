import subprocess
import os

ASSETS_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation\assets"
YT_DLP = os.path.expanduser(r"~\scoop\shims\yt-dlp.exe")
FFMPEG_DIR = os.path.expanduser(r"~\scoop\shims")

videos_to_get = [
    ("clip_chamber.mp4", "https://www.youtube.com/watch?v=_2Zj-rlcuPg"),
    ("clip_heart.mp4", "https://www.youtube.com/watch?v=9WzkyhOK9-Y"),
    ("clip_brain.mp4", "https://www.youtube.com/watch?v=UuCTfDvdeoU"),
    ("clip_clock.mp4", "https://www.youtube.com/watch?v=32nR1MXg1QY"),
]

for filename, url in videos_to_get:
    out_path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(out_path):
        print(f"File {filename} đã tồn tại, bỏ qua.")
        continue
    print(f"Downloading {filename}...")
    cmd = [
        YT_DLP,
        "--ffmpeg-location", FFMPEG_DIR,
        "-f", "bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=720][ext=mp4]/best[height<=720]",
        "--download-sections", "*0-25",
        url,
        "-o", out_path
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Xong: {filename}")
    except Exception as e:
        print(f"❌ Lỗi tải {filename}: {e}")
