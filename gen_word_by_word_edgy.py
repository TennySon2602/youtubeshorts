# File: gen_word_by_word_edgy.py
import asyncio
import edge_tts
import os

BASE_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation"
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

narration_text = (
    "What in the actual hell happens if you sit inside a room so quiet you can hear your own eyeballs moving? "
    "Inside Microsoft's anechoic chamber, background noise drops to minus twenty decibels, which is quieter than complete silence. "
    "Within two minutes, your ears start freaking out. "
    "Suddenly, your heartbeat sounds like a damn bass drum blasting inside your skull. "
    "You can literally hear your lungs wheezing and your blood rushing through your veins. "
    "Without any sound, your brain gets paranoid and starts hallucinating phantom noises just to screw with you. "
    "The longest anyone ever survived in total darkness here is forty-five minutes before losing their damn mind. "
    "Would you survive an hour for a million bucks, or would you cry like a baby? "
    "Drop a comment and follow, you coward."
)

mp3_file = os.path.join(OUTPUT_DIR, "edgy_narration.mp3")
ass_file = os.path.join(OUTPUT_DIR, "edgy_word_by_word.ass")

def sec_to_ass(sec):
    hrs = int(sec // 3600)
    mins = int((sec % 3600) // 60)
    secs = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    return f"{hrs:01d}:{mins:02d}:{secs:02d}.{cs:02d}"

async def generate_speech_and_word_subtitles():
    comm = edge_tts.Communicate(
        text=narration_text,
        voice="en-US-ChristopherNeural",
        rate="+5%",
        pitch="-1Hz",
        boundary="WordBoundary"
    )
    
    words_data = []
    print("Generating speech with exact WordBoundary stream...")
    
    with open(mp3_file, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                offset_sec = chunk["offset"] / 10_000_000
                duration_sec = chunk["duration"] / 10_000_000
                word = chunk["text"].strip()
                if word:
                    words_data.append({
                        "start": offset_sec,
                        "end": offset_sec + duration_sec,
                        "word": word
                    })
                    
    print(f"Captured {len(words_data)} exact words with millisecond timestamps!")
    
    # Nối thời gian kết thúc của từ này với từ tiếp theo nếu khoảng cách < 0.2s để chữ không bị nhấp nháy giật
    for i in range(len(words_data) - 1):
        gap = words_data[i+1]["start"] - words_data[i]["end"]
        if 0 < gap < 0.25:
            words_data[i]["end"] = words_data[i+1]["start"]
            
    # Tạo định dạng ASS: Mỗi từ 1 dòng, Cỡ 70pt, Vàng viền đen siêu nét
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,70,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7.5,3.0,8,30,30,890,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = []
    for w in words_data:
        dialogues.append(
            f"Dialogue: 0,{sec_to_ass(w['start'])},{sec_to_ass(w['end'])},Default,,0,0,0,,{w['word'].upper()}"
        )
        
    with open(ass_file, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(dialogues))
        
    print(f"Saved 1-word-at-a-time ASS subtitles to: {ass_file}")

if __name__ == "__main__":
    asyncio.run(generate_speech_and_word_subtitles())
