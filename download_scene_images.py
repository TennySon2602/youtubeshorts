import requests
import os

ASSETS_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation\assets"

# Các link ảnh trực tiếp từ Wikimedia / Unsplash CDN mở
images = {
    "scene_3_heart.jpg": "https://upload.wikimedia.org/wikipedia/commons/1/12/CG_Heart.gif", # or anatomy photo
    "scene_4_brain.jpg": "https://images.unsplash.com/photo-1559757175-5700dde675bc?auto=format&fit=crop&w=900&q=80", # Human brain scan
    "scene_5_dark.jpg": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=900&q=80", # Dark mysterious hallway
}

# Thêm link ảnh quả tim chất lượng cao
heart_url = "https://images.unsplash.com/photo-1530026405186-ed1f139313f8?auto=format&fit=crop&w=900&q=80"
images["scene_3_heart.jpg"] = heart_url

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for name, url in images.items():
    dest = os.path.join(ASSETS_DIR, name)
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            with open(dest, "wb") as f:
                f.write(r.content)
            print(f"✅ Downloaded {name} ({len(r.content)} bytes)")
        else:
            print(f"❌ Failed {name}: {r.status_code}")
    except Exception as e:
        print(f"❌ Error {name}: {e}")
