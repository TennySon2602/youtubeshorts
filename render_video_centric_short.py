# File: render_video_centric_short.py
import os
import subprocess
import shutil

BASE_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SHIMS_DIR = os.path.expanduser(r"~\scoop\shims")

FFMPEG = shutil.which("ffmpeg") or os.path.join(SHIMS_DIR, "ffmpeg.exe")
FFPROBE = shutil.which("ffprobe") or os.path.join(SHIMS_DIR, "ffprobe.exe")

def generate_subtitles_under_card(vtt_path: str, ass_path: str):
    """
    Tạo phụ đề ASS đặt chuẩn xác NGAY DƯỚI khung video nội dung (y ~ 900).
    Cỡ chữ trung bình (Fontsize=36), font Arial Black, màu vàng rực viền đen đậm.
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
        
        # Nhóm 2 - 3 từ mỗi lần hiển thị
        chunk_size = 3
        chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        dur_per_chunk = total_dur / len(chunks)
        
        for i, chunk in enumerate(chunks):
            c_start = start_sec + i * dur_per_chunk
            c_end = start_sec + (i + 1) * dur_per_chunk
            dialogues.append(
                f"Dialogue: 0,{sec_to_ass(c_start)},{sec_to_ass(c_end)},Default,,0,0,0,,{chunk.upper()}"
            )

    # Cỡ chữ trung bình: Fontsize=36 (tăng từ 24 lên 36), viền đen Outline=4.5
    # Alignment=8 (căn top-center) với MarginV=890 (nằm ngay sát mép dưới khung video y=860)
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,36,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4.5,2,8,40,40,890,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(dialogues))
        
    print(f"✅ Đã tạo phụ đề (Cỡ trung bình 36pt, nằm dưới khung): {ass_path}")

def render_video_with_clean_clips():
    audio_path = os.path.join(OUTPUT_DIR, "narration.mp3")
    vtt_path = os.path.join(OUTPUT_DIR, "narration.vtt")
    ass_path = os.path.join(OUTPUT_DIR, "subtitles_below_card.ass")
    gameplay_path = os.path.join(ASSETS_DIR, "minecraft_parkour.mp4")
    final_output = os.path.join(OUTPUT_DIR, "minecraft_clean_short.mp4")

    # 1. Tạo file phụ đề ASS cỡ trung bình
    generate_subtitles_under_card(vtt_path, ass_path)

    # 2. Xử lý 4 phân cảnh nội dung (100% SẠCH SẼ, KHÔNG WATERMARK):
    # Segment 1: Ảnh phòng tiêu âm HDR 3.8MB với hiệu ứng Ken Burns lia máy chậm (thay thế cho clip dính watermark) (12.0s)
    # Segment 2: Video 3D Tim đập (10.0s)
    # Segment 3: Video nơ-ron não bộ phát sáng (11.0s)
    # Segment 4: Video đồng hồ đếm ngược (10.54s)
    
    # Clip 1: Tạo từ ảnh HDR với hiệu ứng zoom chậm cực đẹp, sạch 100%
    chamber_img = os.path.join(ASSETS_DIR, "scene_2_soundproof.jpg")
    out_clip_0 = os.path.join(OUTPUT_DIR, "norm_clean_0.mp4")
    total_frames = int(12.0 * 25)
    cmd_clip0 = [
        FFMPEG, "-y",
        "-loop", "1", "-i", chamber_img,
        "-vf", f"scale=900:600:force_original_aspect_ratio=increase,crop=900:600,zoompan=z='min(zoom+0.0004,1.20)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=900x600:fps=25,drawbox=x=0:y=0:w=iw:h=ih:color=white@0.95:t=6",
        "-c:v", "libx264", "-t", "12.0", "-r", "25", "-pix_fmt", "yuv420p", "-an",
        out_clip_0
    ]
    subprocess.run(cmd_clip0, check=True)

    # Clip 2, 3, 4: Các video đã kiểm tra 100% KHÔNG WATERMARK
    motion_clips = [
        ("clip_heart.mp4.mkv", 10.0, "norm_clean_1.mp4"),
        ("clip_brain.mp4.webm", 11.0, "norm_clean_2.mp4"),
        ("clip_clock.mp4.webm", 10.54, "norm_clean_3.mp4"),
    ]

    concat_list = os.path.join(OUTPUT_DIR, "concat_clean.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        f.write(f"file '{out_clip_0}'\n")
        for filename, dur, out_name in motion_clips:
            src_file = os.path.join(ASSETS_DIR, filename)
            out_clip = os.path.join(OUTPUT_DIR, out_name)
            cmd_norm = [
                FFMPEG, "-y",
                "-stream_loop", "-1", "-i", src_file,
                "-vf", "scale=900:600:force_original_aspect_ratio=increase,crop=900:600,drawbox=x=0:y=0:w=iw:h=ih:color=white@0.95:t=6",
                "-c:v", "libx264", "-t", str(dur), "-r", "25", "-pix_fmt", "yuv420p", "-an",
                out_clip
            ]
            subprocess.run(cmd_norm, check=True)
            f.write(f"file '{out_clip}'\n")

    # Ghép 4 clip nội dung thành 1 video 43.54s
    merged_clips = os.path.join(OUTPUT_DIR, "all_clean_clips.mp4")
    subprocess.run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list, "-c", "copy", merged_clips
    ], check=True)
    print("✅ Đã ghép xong chuỗi video nội dung sạch 100%!")

    # 3. Ghép Background Minecraft + Khung Video sạch + Phụ đề cỡ 36pt ngay dưới khung
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
        "-t", "43.54",
        final_output
    ]

    print("[FFmpeg] Đang render bản video sạch không watermark...")
    subprocess.run(cmd_final, check=True)
    print(f"\n🎉 HOÀN THÀNH: {final_output}\n")

if __name__ == "__main__":
    render_video_with_clean_clips()
