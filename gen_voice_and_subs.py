import subprocess
import os

BASE_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation"
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

narration_text = (
    "What happens if you sit inside a room so quiet that you can hear your own eyeballs moving? "
    "Inside Microsoft's anechoic chamber, background noise measures at minus twenty decibels. "
    "That is quieter than complete silence. "
    "Within minutes, your ears adapt. Suddenly, your heartbeat sounds like a bass drum. "
    "You hear your lungs pumping air and your blood rushing through your veins. "
    "Without any external sound, your brain begins to hallucinate, inventing phantom noises just to stay sane. "
    "The longest anyone has ever survived inside this room in total darkness is just forty-five minutes. "
    "Follow for more dark science secrets you won't learn in school."
)

txt_file = os.path.join(OUTPUT_DIR, "full_script.txt")
with open(txt_file, "w", encoding="utf-8") as f:
    f.write(narration_text)

mp3_file = os.path.join(OUTPUT_DIR, "narration.mp3")
vtt_file = os.path.join(OUTPUT_DIR, "narration.vtt")

python_exe = r"C:\Users\ASUS\scoop\apps\python\current\python.exe"
cmd = [
    python_exe, "-m", "edge_tts",
    "-v", "en-US-ChristopherNeural",
    "-f", txt_file,
    "--pitch", "-2Hz",
    "--write-media", mp3_file,
    "--write-subtitles", vtt_file
]

print("Generating voice and synchronized subtitles...")
subprocess.run(cmd, check=True)
print("Done!")

from subtitle_generator import parse_vtt
srt_file = parse_vtt(vtt_file)
print(f"SRT generated: {srt_file}")
