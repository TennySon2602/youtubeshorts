# File: render_rich_video.py
import os
import subprocess
import shutil

BASE_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SHIMS_DIR = os.path.expanduser(r"~\scoop\shims")

FFMPEG = shutil.which("ffmpeg") or os.path.join(SHIMS_DIR, "ffmpeg.exe")
FFPROBE = shutil.which("ffprobe") or os.path.join(SHIMS_DIR, "ffprobe.exe")

def get_audio_duration(audio_path: str) -> float:
    cmd = [
        FFPROBE, "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip())

def render_documentary_short(image_path: str, audio_path: str, srt_path: str, output_path: str):
    """
    Tạo video Shorts chuyên nghiệp gồm:
    1. Ảnh phòng tiêu âm Anechoic Chamber HDR với hiệu ứng chuyển động chậm (Ken Burns Pan/Zoom)
    2. Sóng âm thanh Neon Audio Waveform nhảy theo tần số giọng nói
    3. Phụ đề chữ to vàng/trắng viền đen chuẩn TikTok/Shorts
    """
    duration = get_audio_duration(audio_path)
    total_frames = int((duration + 0.5) * 25)
    
    print(f"[Render] Bắt đầu render video tài liệu {duration:.1f}s...")
    
    # Chuẩn hóa đường dẫn srt cho FFmpeg filter
    srt_clean = srt_path.replace("\\", "/").replace(":", "\\:")
    
    # Filter graph:
    # 1. zoompan: tạo chuyển động zoom chậm từ 1.0 đến 1.25 trên ảnh nền
    # 2. showwaves: tạo sóng âm thanh neon xanh lục nhảy theo voice ở góc dưới
    # 3. overlay sóng âm thanh lên ảnh nền
    # 4. subtitles: chèn phụ đề chữ to ở giữa màn hình
    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"zoompan=z='min(zoom+0.0003,1.25)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=25[bg];"
        f"[1:a]showwaves=s=1080x240:mode=line:colors=0x00FFCC@0.8:scale=sqrt[wave];"
        f"[bg][wave]overlay=0:1400[v_with_wave];"
        f"[v_with_wave]subtitles='{srt_clean}':force_style='FontName=Arial,FontSize=18,PrimaryColour=&H0000FFFF,BackColour=&H80000000,BorderStyle=3,Outline=2,Alignment=2,MarginV=180'[outv]"
    )
    
    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-t", f"{duration + 0.5:.2f}",
        output_path
    ]
    
    print("[FFmpeg] Đang xử lý các lớp hình ảnh, sóng âm và phụ đề...")
    subprocess.run(cmd, check=True)
    print(f"🎉 Render hoàn tất: {output_path}")

if __name__ == "__main__":
    img = os.path.join(ASSETS_DIR, "scene_2_soundproof.jpg")
    audio = os.path.join(OUTPUT_DIR, "narration.mp3")
    vtt = os.path.join(OUTPUT_DIR, "narration.vtt")
    srt = os.path.join(OUTPUT_DIR, "narration.srt")
    final_video = os.path.join(OUTPUT_DIR, "viral_anechoic_chamber_short.mp4")
    
    from subtitle_generator import parse_vtt
    if os.path.exists(vtt):
        parse_vtt(vtt)
    elif os.path.exists(os.path.join(OUTPUT_DIR, "test_sub.srt")):
        srt = os.path.join(OUTPUT_DIR, "test_sub.srt")
        
    render_documentary_short(img, audio, srt, final_video)
