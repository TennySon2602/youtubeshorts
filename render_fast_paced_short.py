# File: render_fast_paced_short.py
import os
import subprocess
import shutil

BASE_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SHIMS_DIR = os.path.expanduser(r"~\scoop\shims")

FFMPEG = shutil.which("ffmpeg") or os.path.join(SHIMS_DIR, "ffmpeg.exe")
FFPROBE = shutil.which("ffprobe") or os.path.join(SHIMS_DIR, "ffprobe.exe")

def generate_big_punchy_subtitles(vtt_path: str, ass_path: str):
    """
    Tạo phụ đề ASS CỠ TO NỔI BẬT (Fontsize=62), đặt ngay dưới khung nội dung.
    Font Arial Black, chữ in hoa, màu vàng rực viền đen dày 7px chuẩn viral Shorts.
    """
    import re
    with open(vtt_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.findall(r"(\d{2}:\d{2}:\d{2}[\.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[\.,]\d{3})\s*\n(.*?)(?=\n\n|\Z)", content, re.DOTALL)
    
    def time_to_sec(t_str):
        t_str = t_str.replace(",", ".")
        p = t_str.split(":")
        return float(p[0]) * 3600 + float(p[1]) * 60 + float(p[2])
        
    def sec_to_ass(sec):
        hrs = int(sec // 3600)
        mins = int((sec % 3600) // 60)
        secs = int(sec % 60)
        cs = int(round((sec - int(sec)) * 100))
        return f"{hrs:01d}:{mins:02d}:{secs:02d}.{cs:02d}"

    dialogues = []
    
    for start_str, end_str, text in blocks:
        text = text.strip().replace("\n", " ")
        words = text.split()
        if not words:
            continue
            
        start_sec = time_to_sec(start_str)
        end_sec = time_to_sec(end_str)
        total_dur = end_sec - start_sec
        
        # Nhóm 2 - 3 từ mỗi lần xuất hiện để giật phụ đề bắt mắt
        chunk_size = 2 if len(words) > 6 else 3
        chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        dur_per_chunk = total_dur / len(chunks)
        
        for i, chunk in enumerate(chunks):
            c_start = start_sec + i * dur_per_chunk
            c_end = start_sec + (i + 1) * dur_per_chunk
            dialogues.append(
                f"Dialogue: 0,{sec_to_ass(c_start)},{sec_to_ass(c_end)},Default,,0,0,0,,{chunk.upper()}"
            )

    # Cỡ chữ TO HẲN: Fontsize=62 (nâng từ 46 lên 62), viền đen siêu dày Outline=7.0
    # MarginV=890 (nằm ngay sát mép dưới khung video y=860)
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,62,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7.0,3.0,8,30,30,890,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(dialogues))
        
    print(f"✅ Đã tạo phụ đề CỠ TO 62pt: {ass_path}")

def render_fast_paced_video():
    audio_path = os.path.join(OUTPUT_DIR, "edgy_narration.mp3")
    vtt_path = os.path.join(OUTPUT_DIR, "edgy_narration.vtt")
    ass_path = os.path.join(OUTPUT_DIR, "edgy_subtitles_big.ass")
    gameplay_path = os.path.join(ASSETS_DIR, "minecraft_parkour.mp4")
    final_output = os.path.join(OUTPUT_DIR, "viral_edgy_minecraft_short.mp4")

    # 1. Tạo phụ đề cỡ to 62pt
    generate_big_punchy_subtitles(vtt_path, ass_path)

    # 2. Sử dụng lại file video 9 phân cảnh đã ghép sẵn để render siêu tốc (chỉ mất ~10s!)
    merged_clips = os.path.join(OUTPUT_DIR, "all_edgy_clips.mp4")

    # 3. Ghép Background Minecraft + 9 phân cảnh nội dung + Phụ đề CỠ TO 62pt
    ass_clean = ass_path.replace("\\", "/").replace(":", "\\:")
    
    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];"
        f"[bg][1:v]overlay=90:260[v_card];"
        f"[v_card]ass='{ass_clean}'[outv]"
    )

    cmd_final = [
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

    print("[FFmpeg] Đang tiến hành ghép phụ đề cỡ to 62pt vào video...")
    subprocess.run(cmd_final, check=True)
    print(f"\n🎉 HOÀN THÀNH: {final_output}\n")

if __name__ == "__main__":
    render_fast_paced_video()
