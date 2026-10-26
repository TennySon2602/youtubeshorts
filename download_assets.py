import requests
import os

ASSETS_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation\assets"

images_to_download = {
    "scene_1_chamber.jpg": "https://upload.wikimedia.org/wikipedia/commons/5/52/Anechoic_chamber.jpg",
    "scene_2_soundproof.jpg": "https://upload.wikimedia.org/wikipedia/commons/0/0a/Radio-frequency-anechoic-chamber-HDR-0a.jpg",
    "scene_3_heart.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/e4/O%27Donnell-Luria%E2%80%93Rodan_syndrome_%E2%80%94_Brain_MRI.jpg",
}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for filename, url in images_to_download.items():
    dest = os.path.join(ASSETS_DIR, filename)
    print(f"Downloading {filename}...")
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            with open(dest, "wb") as f:
                f.write(r.content)
            print(f"✅ Saved: {dest} ({len(r.content)} bytes)")
        else:
            print(f"❌ Failed: HTTP {r.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
