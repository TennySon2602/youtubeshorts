# File: create_viral_short.py
import os
import subprocess
import shutil

BASE_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SHIMS_DIR = os.path.expanduser(r"~\scoop\shims")

FFMPEG = shutil.which("ffmpeg") or os.path.join(SHIMS_DIR, "ffmpeg.exe")
FFPROBE = shutil.which("ffprobe") or os.path.join(SHIMS_DIR, "ffprobe.exe")

def generate_punchy_subtitles(vtt_path: str, srt_path: str):
    """Tạo phụ đề 2-3 từ mỗi dòng, chữ to, màu vàng viền đen chuẩn Shorts"""
    import re
    with open(vtt_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.findall(r"(\d{2}:\d{2}:\d{2}[\.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[\.,]\d{3})\s*\n(.*?)(?=\n\n|\Z)", content, re.DOTALL)
    
    srt_entries = []
    idx = 1
    
    def time_to_sec(t_str):
        t_str = t_str.replace(",", ".")
        p = t_str.split(":")
        return float(p[0]) * 3600 + float(p[1]) * 60 + float(p[2])
        
    def sec_to_srt(sec):
        hrs = int(sec // 3600)
        mins = int((sec % 3600) // 60)
        secs = int(sec % 60)
        ms = int(round((sec - int(sec)) * 1000))
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"

    for start_str, end_str, text in blocks:
        text = text.strip().replace("\n", " ")
        words = text.split()
        if not words:
            continue
            
        start_sec = time_to_sec(start_str)
        end_sec = time_to_sec(end_str)
        total_dur = end_sec - start_sec
        
        # Chia thành 2 - 3 từ mỗi lần xuất hiện để giật phụ đề bắt mắt
        chunk_size = 3
        chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        dur_per_chunk = total_dur / len(chunks)
        
        for i, chunk in enumerate(chunks):
            c_start = start_sec + i * dur_per_chunk
            c_end = start_sec + (i + 1) * dur_per_chunk
            srt_entries.append(f"{idx}\n{sec_to_srt(c_start)} --> {sec_to_srt(c_end)}\n{chunk.upper()}\n\n")
            idx += 1

    with open(srt_path, "w", encoding="utf-8") as f:
        f.writelines(srt_entries)
    print(f"✅ Đã tạo phụ đề phong cách Shorts: {srt_path}")

def render_minecraft_split_short():
    audio_path = os.path.join(OUTPUT_DIR, "narration.mp3")
    vtt_path = os.path.join(OUTPUT_DIR, "narration.vtt")
    srt_path = os.path.join(OUTPUT_DIR, "punchy_subtitles.srt")
    gameplay_path = os.path.join(ASSETS_DIR, "minecraft_parkour.mp4")
    final_output = os.path.join(OUTPUT_DIR, "minecraft_anechoic_short.mp4")

    # Tạo phụ đề nhịp điệu nhanh
    generate_punchy_subtitles(vtt_path, srt_path)

    # Danh sách 5 ảnh tương ứng với timeline kịch bản:
    # 0s - 7s: scene_1_chamber
    # 7s - 16s: scene_2_soundproof
    # 16s - 26s: scene_3_heart
    # 26s - 35s: scene_4_brain
    # 35s - 43.5s: scene_5_dark
    scenes = [
        (os.path.join(ASSETS_DIR, "scene_1_chamber.jpg"), 7.0),
        (os.path.join(ASSETS_DIR, "scene_2_soundproof.jpg"), 9.0),
        (os.path.join(ASSETS_DIR, "scene_3_heart.jpg"), 10.0),
        (os.path.join(ASSETS_DIR, "scene_4_brain.jpg"), 9.0),
        (os.path.join(ASSETS_DIR, "scene_5_dark.jpg"), 8.54),
    ]

    # Bước 1: Render slideshow video của 5 ảnh nội dung (kích thước 920x620 có bo viền trắng)
    card_clips = []
    concat_list_file = os.path.join(OUTPUT_DIR, "concat_slides.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for idx, (img_path, dur) in enumerate(scenes):
            clip_name = f"slide_{idx}.mp4"
            clip_path = os.path.join(OUTPUT_DIR, clip_name)
            
            # Scale ảnh thành 920x620 và thêm viền trắng 6px
            cmd_slide = [
                FFMPEG, "-y",
                "-loop", "1", "-i", img_path,
                "-vf", "scale=920:620:force_original_aspect_ratio=increase,crop=920:620,drawbox=x=0:y=0:w=iw:h=ih:color=white@0.9:t=6",
                "-c:v", "libx264", "-t", str(dur), "-pix_fmt", "yuv420p",
                clip_path
            ]
            subprocess.run(cmd_slide, check=True)
            f.write(f"file '{clip_path}'\n")

    # Ghép 5 slide lại thành 1 video nội dung duy nhất
    slides_video = os.path.join(OUTPUT_DIR, "all_slides.mp4")
    subprocess.run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list_file, "-c", "copy", slides_video
    ], check=True)
    print("✅ Đã ghép xong video các phân cảnh nội dung thay đổi liên tục!")

    # Bước 2: Ghép Gameplay Minecraft ở dưới + Card nội dung ở trên + Phụ đề chữ to màu vàng
    srt_clean = srt_path.replace("\\", "/").replace(":", "\\:")
    
    # Filter:
    # 1. Background: Minecraft parkour scale về 1080:1920
    # 2. Overlay card slides tại vị trí x=80, y=280 (khoảng giữa trên)
    # 3. Dập phụ đề ở y khoảng 1200 (phía dưới khung ảnh)
    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];"
        f"[bg][1:v]overlay=80:280[v_card];"
        f"[v_card]subtitles='{srt_clean}':force_style='FontName=Arial Black,FontSize=22,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=4,Shadow=2,Alignment=2,MarginV=260'[outv]"
    )

    cmd_final = [
        FFMPEG, "-y",
        "-stream_loop", "-1", "-i", gameplay_path,
        "-i", slides_video,
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

    print("[FFmpeg] Đang tiến hành ghép Gameplay + Slides ảnh chuyển cảnh + Phụ đề...")
    subprocess.run(cmd_final, check=True)
    print(f"\n🎉 HOÀN THÀNH VIDEO VIRAL MINECRAFT STYLE: {final_output}\n")

if __name__ == "__main__":
    render_minecraft_split_short()
