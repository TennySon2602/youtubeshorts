# File: main.py
import os
import asyncio
from script_generator import generate_script
from tts_engine import DEFAULT_VOICE_EN, DEFAULT_VOICE_VI
from subtitle_generator import parse_vtt
from video_compiler import create_rich_short_video
import subprocess

BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

async def run_pipeline(topic: str, language: str = "en"):
    print(f"\n==========================================")
    print(f"🎬 BẮT ĐẦU TẠO VIDEO SHORT CHO: '{topic}'")
    print(f"==========================================\n")
    
    # Bước 1: Sinh kịch bản qua OxionAI
    print("▶️ BƯỚC 1: Đang chuẩn bị kịch bản...")
    script_data = generate_script(topic=topic, language=language)
    print(f"✅ Kịch bản: {script_data.get('topic')}")
    print(f"🔥 Hook: {script_data.get('hook')}\n")

    # Bước 2: Tạo giọng đọc AI & Phụ đề đồng bộ (VTT & SRT)
    print("▶️ BƯỚC 2: Đang tạo giọng đọc AI và phụ đề từng chữ...")
    audio_path = os.path.join(OUTPUT_DIR, "narration.mp3")
    vtt_path = os.path.join(OUTPUT_DIR, "narration.vtt")
    voice = DEFAULT_VOICE_VI if language == "vi" else DEFAULT_VOICE_EN
    
    # Ghi nội dung vào file tạm để sinh voice + sub
    txt_temp = os.path.join(OUTPUT_DIR, "script_temp.txt")
    with open(txt_temp, "w", encoding="utf-8") as f:
        f.write(script_data["full_narration"])
        
    python_exe = os.path.expanduser(r"~\scoop\apps\python\current\python.exe")
    cmd = [
        python_exe, "-m", "edge_tts",
        "-v", voice,
        "-f", txt_temp,
        "--pitch", "-2Hz",
        "--write-media", audio_path,
        "--write-subtitles", vtt_path
    ]
    subprocess.run(cmd, check=True)
    srt_path = parse_vtt(vtt_path)
    print(f"✅ Âm thanh & Phụ đề đã sẵn sàng!\n")

    # Bước 3: Chọn tư liệu hình ảnh / video nền
    print("▶️ BƯỚC 3: Chọn hình ảnh / video nội dung...")
    # Ưu tiên các file ảnh thật trong assets
    candidates = [
        os.path.join(ASSETS_DIR, "scene_2_soundproof.jpg"),
        os.path.join(ASSETS_DIR, "scene_1_chamber.jpg"),
        os.path.join(ASSETS_DIR, "background.mp4")
    ]
    selected_bg = None
    for cand in candidates:
        if os.path.exists(cand):
            selected_bg = cand
            break
            
    print(f"✅ Đã chọn tư liệu nền: {os.path.basename(selected_bg)}\n")

    # Bước 4: Render video hoàn chỉnh
    print("▶️ BƯỚC 4: Đang ghép video, tạo sóng âm và dập phụ đề...")
    final_output = os.path.join(OUTPUT_DIR, "viral_anechoic_chamber_short.mp4")
    create_rich_short_video(selected_bg, audio_path, srt_path, final_output)
    
    print(f"\n🎉 HOÀN THÀNH XUẤT SẮC!")
    print(f"📁 Video hoàn chỉnh: {final_output}\n")

if __name__ == "__main__":
    test_topic = "The anechoic chamber: The world's quietest room"
    asyncio.run(run_pipeline(test_topic, language="en"))
