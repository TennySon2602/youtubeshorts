# File: subtitle_generator.py
import re
import os

def parse_vtt(vtt_path: str):
    """Đọc file vtt từ edge-tts và chia nhỏ thành các cụm từ ngắn (3-5 từ) hiển thị lần lượt"""
    with open(vtt_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.findall(r"(\d{2}:\d{2}:\d{2}[\.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[\.,]\d{3})\s*\n(.*?)(?=\n\n|\Z)", content, re.DOTALL)
    
    srt_entries = []
    idx = 1
    
    for start_str, end_str, text in blocks:
        text = text.strip().replace("\n", " ")
        if not text:
            continue
            
        def time_to_sec(t_str):
            t_str = t_str.replace(",", ".")
            parts = t_str.split(":")
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            
        def sec_to_srt(sec):
            hrs = int(sec // 3600)
            mins = int((sec % 3600) // 60)
            secs = int(sec % 60)
            ms = int(round((sec - int(sec)) * 1000))
            return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"

        start_sec = time_to_sec(start_str)
        end_sec = time_to_sec(end_str)
        total_dur = end_sec - start_sec
        
        words = text.split()
        if not words:
            continue
            
        # Chia thành các nhóm 3 - 5 từ mỗi slide chữ
        chunk_size = 4
        chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        dur_per_chunk = total_dur / len(chunks)
        
        for i, chunk in enumerate(chunks):
            c_start = start_sec + i * dur_per_chunk
            c_end = start_sec + (i + 1) * dur_per_chunk
            srt_entries.append(f"{idx}\n{sec_to_srt(c_start)} --> {sec_to_srt(c_end)}\n{chunk.upper()}\n\n")
            idx += 1

    srt_path = vtt_path.replace(".vtt", ".srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        f.writelines(srt_entries)
        
    print(f"[Subtitles] Đã tạo file phụ đề đồng bộ: {srt_path}")
    return srt_path

if __name__ == "__main__":
    test_vtt = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation\output\test_sub.vtt"
    if os.path.exists(test_vtt):
        parse_vtt(test_vtt)
