import requests
import time
import os

ASSETS_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation\assets"

urls = {
    "scene_3_brain.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Human_brain_NIH.png/800px-Human_brain_NIH.png",
    "scene_4_heart.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Diagram_of_the_human_heart_%28cropped%29.svg/800px-Diagram_of_the_human_heart_%28cropped%29.svg.png"
}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for name, url in urls.items():
    dest = os.path.join(ASSETS_DIR, name)
    try:
        time.sleep(1)
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            with open(dest, "wb") as f:
                f.write(r.content)
            print(f"Downloaded {name} successfully ({len(r.content)} bytes)")
        else:
            print(f"Failed {name}: {r.status_code}")
    except Exception as e:
        print(f"Error {name}: {e}")
