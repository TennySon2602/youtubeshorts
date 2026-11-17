"""
Quick Test Script for Facebook Reels & Instagram Reels Publishing
"""
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load local environment
load_dotenv()

# Meta credentials
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "1489998967525792")
IG_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "17841457367667463")
ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN", "").strip()

# If not in env, check default fallback or prompt
if not ACCESS_TOKEN:
    ACCESS_TOKEN = "EAAahl5gbyioBTOzX3IXgVqouu1c26nZCHBnte9ZBNsBZC5sw36gHMTWNkrthcxcwtGPk4ZAaQaq1P2ZAARwUZAKEbZCQFECCJw6nxVEJ2OUt299LHIq7NcZCsX4kpgEVXkMmQGYqF5vFRUxdsuaHTY3kBXEagryTVZAPekWTzBLFFaSDx3UmHx5KZCyMaDuvmzQw0UtEDzRB3oG9JWGQ63QHYZBqubDgaVmmuEQMf6LtL7LttAj"

def check_token(token: str):
    print("🔍 Đang kiểm tra trạng thái Token...")
    # Check FB Page
    fb_res = requests.get(
        f"https://graph.facebook.com/v21.0/{FB_PAGE_ID}",
        params={"fields": "name,id", "access_token": token},
        timeout=15
    ).json()

    # Check IG Account
    ig_res = requests.get(
        f"https://graph.facebook.com/v21.0/{IG_ACCOUNT_ID}",
        params={"fields": "username,name,id", "access_token": token},
        timeout=15
    ).json()

    if "error" in fb_res:
        err = fb_res["error"].get("message", "Unknown FB error")
        print(f"❌ Facebook Token Error: {err}")
        return False, err
    if "error" in ig_res:
        err = ig_res["error"].get("message", "Unknown IG error")
        print(f"❌ Instagram Token Error: {err}")
        return False, err

    print(f"✅ Facebook Page: {fb_res.get('name')} (ID: {fb_res.get('id')})")
    print(f"✅ Instagram Account: @{ig_res.get('username')} (ID: {ig_res.get('id')})")
    return True, None

def main():
    global ACCESS_TOKEN
    print("=" * 60)
    print("🚀 KIỂM TRA & ĐĂNG THỬ FACEBOOK REELS & INSTAGRAM REELS")
    print("=" * 60)

    # Check command-line argument for new token
    if len(sys.argv) > 1:
        ACCESS_TOKEN = sys.argv[1].strip()

    valid, err = check_token(ACCESS_TOKEN)
    if not valid:
        print("\n⚠️ Token hiện tại đã hết hạn (expired).")
        print("Vui lòng nhập Token mới (từ Meta Graph API Explorer) hoặc truyền vào lệnh:")
        try:
            new_token = input("\nDán Token mới vào đây rồi nhấn Enter (hoặc bấm Ctrl+C để thoát):\n> ").strip()
            if new_token:
                ACCESS_TOKEN = new_token
                valid, err = check_token(ACCESS_TOKEN)
                if not valid:
                    print(f"❌ Token mới vẫn không hợp lệ: {err}")
                    return
            else:
                return
        except KeyboardInterrupt:
            print("\nĐã hủy.")
            return

    # Check video to upload
    video_path = Path("output/gta6_lucia_ankle_monitor_final_short.mp4")
    if not video_path.exists():
        # Fallback to any mp4 in output
        mp4_list = list(Path("output").glob("*_final_short.mp4"))
        if mp4_list:
            video_path = mp4_list[0]
        else:
            print("❌ Không tìm thấy video test trong thư mục output/!")
            return

    print(f"\n🎬 Chuẩn bị đăng video: {video_path.name}")
    title = "GTA 6 - The Mystery of Lucia's Ankle Monitor"
    description = "Why does Lucia have a tracker in GTA VI? Here is the secret storyline detail Rockstar hid in plain sight."
    tags = ["GTA6", "GTAVI", "RockstarGames", "GamingReels", "Reels"]

    from meta_uploader import upload_facebook_reel, upload_instagram_reel
    tags_str = " ".join([f"#{t.strip('#')}" for t in tags])
    full_caption = f"{title}\n\n{description}\n\n{tags_str}"

    print("\n[1/2] Đang đăng lên Facebook Reels...")
    try:
        fb_res = upload_facebook_reel(str(video_path), full_caption, FB_PAGE_ID, ACCESS_TOKEN)
        print(f"🎉 FACEBOOK REELS THÀNH CÔNG: Video ID = {fb_res.get('video_id')}")
    except Exception as e:
        print(f"❌ Facebook Reels Thất Bại: {e}")

    print("\n[2/2] Đang đăng lên Instagram Reels...")
    try:
        ig_res = upload_instagram_reel(str(video_path), full_caption, IG_ACCOUNT_ID, ACCESS_TOKEN)
        print(f"🎉 INSTAGRAM REELS THÀNH CÔNG: Post ID = {ig_res.get('id')}")
    except Exception as e:
        print(f"❌ Instagram Reels Thất Bại: {e}")

    print("\n" + "=" * 60)
    print("HOÀN TẤT KIỂM TRA ĐĂNG BÀI META!")
    print("=" * 60)

if __name__ == "__main__":
    main()
