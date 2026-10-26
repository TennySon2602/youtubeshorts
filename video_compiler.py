# File: video_compiler.py
import os
import subprocess
import shutil

SHIMS_DIR = os.path.expanduser(r"~\scoop\shims")
FFMPEG_BIN = shutil.which("ffmpeg") or os.path.join(SHIMS_DIR, "ffmpeg.exe")
FFPROBE_BIN = shutil.which("ffprobe") or os.path.join(SHIMS_DIR, "ffprobe.exe")

def get_audio_duration(audio_path: str) -> float:
    cmd = [
        FFPROBE_BIN, "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip())

def create_rich_short_video(background_path: str, audio_path: str, srt_path: str, output_path: str):
    """
    Tạo video hoàn chỉnh chất lượng cao gồm:
    1. Hình nền / Video nền chuyển động dọc 9:16
    2. Sóng âm thanh nhảy theo giọng nói (Audio Waveform)
    3. Phụ đề nổi bật (Dynamic Subtitles)
    """
    duration = get_audio_duration(audio_path)
    total_frames = int((duration + 0.5) * 25)
    srt_clean = srt_path.replace("\\", "/").replace(":", "\\:")
    
    # Kiểm tra input là ảnh hay video
    is_image = background_path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
    
    if is_image:
        bg_filter = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='min(zoom+0.0003,1.25)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=25[bg];"
        )
        input_args = ["-loop", "1", "-i", background_path]
    else:
        bg_filter = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];"
        input_args = ["-stream_loop", "-1", "-i", background_path]

    filter_complex = (
        f"{bg_filter}"
        f"[1:a]showwaves=s=1080x240:mode=line:colors=0x00FFCC@0.8:scale=sqrt[wave];"
        f"[bg][wave]overlay=0:1400[v_with_wave];"
        f"[v_with_wave]subtitles='{srt_clean}':force_style='FontName=Arial,FontSize=18,PrimaryColour=&H0000FFFF,BackColour=&H80000000,BorderStyle=3,Outline=2,Alignment=2,MarginV=180'[outv]"
    )

    cmd = [
        FFMPEG_BIN, "-y",
        *input_args,
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
    print(f"🎉 Render thành công: {output_path}")

if __name__ == "__main__":
    print("Video Compiler sẵn sàng.")
