# File: pexels_fetcher.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def download_video_for_keyword(keyword: str, output_path: str) -> bool:
    """
    Tìm kiếm và tải 1 video nền dạng dọc (portrait) chất lượng cao từ Pexels miễn phí.
    """
    if not PEXELS_API_KEY or PEXELS_API_KEY == "your_pexels_api_key_here":
        print(f"[Pexels] Chưa cấu hình PEXELS_API_KEY. Bỏ qua tải tự động cho từ khóa: '{keyword}'.")
        return False
        
    url = f"https://api.pexels.com/videos/search?query={keyword}&orientation=portrait&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json()
        if not data.get("videos"):
            print(f"[Pexels] Không tìm thấy video cho từ khóa: '{keyword}'")
            return False
            
        video_files = data["videos"][0].get("video_files", [])
        # Chọn file video có độ phân giải HD (ưu tiên 1080p hoặc 720p)
        selected_file = None
        for vf in video_files:
            if vf.get("width") and vf.get("height") and vf["height"] > vf["width"]: # dạng dọc
                selected_file = vf.get("link")
                break
        if not selected_file and video_files:
            selected_file = video_files[0].get("link")
            
        if selected_file:
            print(f"[Pexels] Đang tải video cho '{keyword}'...")
            v_res = requests.get(selected_file, stream=True, timeout=30)
            with open(output_path, "wb") as f:
                for chunk in v_res.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            print(f"[Pexels] Đã tải xong: {output_path}")
            return True
    except Exception as e:
        print(f"[Pexels] Lỗi khi tải video: {e}")
        return False

    return False
