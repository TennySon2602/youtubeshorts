# File: tts_engine.py
import asyncio
import edge_tts
import os

# Voice models:
# Tiếng Việt: vi-VN-NamMinhNeural (nam) hoặc vi-VN-HoaiMyNeural (nữ)
# Tiếng Anh: en-US-ChristopherNeural (nam trầm bí ẩn) hoặc en-US-JennyNeural (nữ)

DEFAULT_VOICE_VI = "vi-VN-NamMinhNeural"
DEFAULT_VOICE_EN = "en-US-ChristopherNeural"

async def generate_voice(text: str, output_path: str, voice: str = DEFAULT_VOICE_EN, rate: str = "+0%", pitch: str = "-2Hz"):
    """
    Tạo giọng đọc AI chân thực từ văn bản và lưu thành file mp3.
    rate: điều chỉnh tốc độ nói (ví dụ "+10%", "+0%")
    pitch: điều chỉnh độ trầm ấm của giọng nói (ví dụ "-2Hz" giúp giọng trầm bí ẩn hơn)
    """
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)
    print(f"[TTS] Đã tạo thành công file âm thanh: {output_path}")

if __name__ == "__main__":
    sample_text = "What would happen if you were trapped inside the world's quietest room for more than 45 minutes? It is said that the silence can literally drive you insane."
    test_output = os.path.join(os.path.dirname(__file__), "output", "test_voice.mp3")
    asyncio.run(generate_voice(sample_text, test_output))
