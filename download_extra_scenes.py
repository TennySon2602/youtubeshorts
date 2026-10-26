import requests
import os

ASSETS_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation\assets"

# Các hình ảnh độ nét cao Unsplash / Wikimedia không bản quyền cho từng câu thoại:
assets_to_download = {
    # Câu 1: Eyeball close-up
    "scene_1_eye.jpg": "https://images.unsplash.com/photo-1574158622682-e40e69881006?auto=format&fit=crop&w=900&q=80",
    # Câu 3: Loud noise / Ear panic / Sound wave
    "scene_3_soundwave.jpg": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=900&q=80",
    # Câu 5: Lungs & blood vessels / red cells
    "scene_5_lungs.jpg": "https://images.unsplash.com/photo-1584036561566-baf8f5f1b144?auto=format&fit=crop&w=900&q=80",
    # Câu 8: 1 Million Dollars / Money cash
    "scene_8_money.jpg": "https://images.unsplash.com/photo-1580519542036-c47de6196ba5?auto=format&fit=crop&w=900&q=80",
    # Câu 9: Comment & Trophy / Subscribe
    "scene_9_trophy.jpg": "https://images.unsplash.com/photo-1569437061241-a848be43cc82?auto=format&fit=crop&w=900&q=80"
}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for filename, url in assets_to_download.items():
    dest = os.path.join(ASSETS_DIR, filename)
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            with open(dest, "wb") as f:
                f.write(r.content)
            print(f"✅ Downloaded {filename} ({len(r.content)} bytes)")
        else:
            print(f"❌ Failed {filename}: {r.status_code}")
    except Exception as e:
        print(f"❌ Error {filename}: {e}")
