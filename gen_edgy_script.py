import subprocess
import os

BASE_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation"
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Kịch bản mới: Hài hước, châm biếm, có chửi bậy nhẹ kiểu slang Gen-Z/YouTube Mỹ (hell, damn, freaking, coward)
# Rất an toàn với luật YouTube (Green monetization) nhưng cuốn hút gấp 10 lần!
narration_sentences = [
    ("What in the actual hell happens if you sit inside a room so quiet you can hear your own eyeballs moving?", 5.5),
    ("Inside Microsoft's anechoic chamber, background noise drops to minus twenty decibels, which is quieter than complete silence.", 6.5),
    ("Within two minutes, your ears start freaking out.", 3.5),
    ("Suddenly, your heartbeat sounds like a damn bass drum blasting inside your skull.", 4.5),
    ("You can literally hear your lungs wheezing and your blood rushing through your veins.", 4.5),
    ("Without any sound, your brain gets paranoid and starts hallucinating phantom noises just to screw with you.", 6.0),
    ("The longest anyone ever survived in total darkness here is forty-five minutes before losing their damn mind.", 6.0),
    ("Would you survive an hour for a million bucks, or would you cry like a baby? Drop a comment and follow, you coward.", 6.5)
]

full_text = " ".join([s[0] for s in narration_sentences])

txt_file = os.path.join(OUTPUT_DIR, "edgy_script.txt")
with open(txt_file, "w", encoding="utf-8") as f:
    f.write(full_text)

mp3_file = os.path.join(OUTPUT_DIR, "edgy_narration.mp3")
vtt_file = os.path.join(OUTPUT_DIR, "edgy_narration.vtt")

python_exe = os.path.expanduser(r"~\scoop\apps\python\current\python.exe")
# Giọng ChristopherNeural với rate +5% cho nhịp điệu nhanh, dứt khoát, hài hước
cmd = [
    python_exe, "-m", "edge_tts",
    "-v", "en-US-ChristopherNeural",
    "-f", txt_file,
    "--rate", "+5%",
    "--pitch", "-1Hz",
    "--write-media", mp3_file,
    "--write-subtitles", vtt_file
]

print("Generating high-energy voiceover with edge-tts...")
subprocess.run(cmd, check=True)
print("Voice & VTT generated!")
