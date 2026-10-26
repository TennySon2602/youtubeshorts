# File: render_word_by_word_video.py
import os
import subprocess
import shutil

BASE_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SHIMS_DIR = os.path.expanduser(r"~\scoop\shims")

FFMPEG = shutil.which("ffmpeg") or os.path.join(SHIMS_DIR, "ffmpeg.exe")

def render():
    audio_path = os.path.join(OUTPUT_DIR, "edgy_narration.mp3")
    ass_path = os.path.join(OUTPUT_DIR, "edgy_word_by_word.ass")
    gameplay_path = os.path.join(ASSETS_DIR, "minecraft_parkour.mp4")
    merged_clips = os.path.join(OUTPUT_DIR, "all_edgy_clips.mp4")
    final_output = os.path.join(OUTPUT_DIR, "viral_edgy_word_by_word_short.mp4")

    ass_clean = ass_path.replace("\\", "/").replace(":", "\\:")
    
    # Filter graph:
    # 1. Background: Minecraft gameplay scale 1080x1920
    # 2. Overlay 9 phân cảnh nội dung đổi liên tục tại x=90, y=260
    # 3. Phụ đề TỪNG TỪ MỘT (Word-by-word) nhảy ngay tức thì khi phát âm, cỡ to 70pt, nằm sát dưới khung
    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];"
        f"[bg][1:v]overlay=90:260[v_card];"
        f"[v_card]ass='{ass_clean}'[outv]"
    )

    cmd = [
        FFMPEG, "-y",
        "-stream_loop", "-1", "-i", gameplay_path,
        "-i", merged_clips,
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "2:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-t", "47.46",
        final_output
    ]

    print("[FFmpeg] Đang tiến hành ghép phụ đề chuẩn từng từ 100% khớp miệng...")
    subprocess.run(cmd, check=True)
    print(f"\n🎉 HOÀN THÀNH: {final_output}\n")

if __name__ == "__main__":
    render()
