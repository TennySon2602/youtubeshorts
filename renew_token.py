import os
import json
import subprocess
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly'
]

CLIENT_SECRETS_FILE = Path(__file__).parent / "client_secrets.json"
TOKEN_FILE = Path(__file__).parent / "token.json"

def main():
    print("=" * 60)
    print("🔑 CÔNG CỤ TẠO LẠI YOUTUBE OAUTH TOKEN (RENEW TOKEN)")
    print("=" * 60)
    
    if not CLIENT_SECRETS_FILE.exists():
        print(f"❌ Lỗi: Không tìm thấy {CLIENT_SECRETS_FILE.name}!")
        return

    print("\n[1/3] Đang khởi động trình duyệt để đăng nhập tài khoản YouTube...")
    print("👉 Hãy đăng nhập và chọn 'Cho phép' (Allow) trên trình duyệt.")
    print("👉 Nếu gặp thông báo 'Google hasn't verified this app', bấm 'Advanced' -> 'Go to... (unsafe)'.\n")

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRETS_FILE),
        SCOPES
    )
    
    creds = flow.run_local_server(
        port=0,
        open_browser=True,
        access_type='offline',
        prompt='consent',
        authorization_prompt_message='[OAuth URL] Vui lòng mở link sau trong trình duyệt nếu trình duyệt không tự mở:\n{url}\n'
    )

    token_json_str = creds.to_json()
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token_json_str)

    print("\n✅ [2/3] Đã lưu token mới vào token.json thành công!")

    # Compact token string for GitHub Secrets
    compact_token = json.dumps(json.loads(token_json_str))
    
    # Copy to clipboard via PowerShell
    try:
        process = subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", "$input | Set-Clipboard"],
            stdin=subprocess.PIPE,
            text=True
        )
        process.communicate(input=compact_token)
        print("📋 [3/3] ĐÃ TỰ ĐỘNG COPY TOKEN VÀO BỘ NHỚ TẠM (CLIPBOARD) CỦA BẠN!")
    except Exception as e:
        print(f"⚠️ Không thể tự copy vào clipboard: {e}")

    print("\n" + "=" * 60)
    print("👉 BƯỚC TIẾP THEO:")
    print("1. Vào GitHub repo: https://github.com/TennySon2602/youtubeshorts/settings/secrets/actions")
    print("2. Tìm secret 'YOUTUBE_TOKEN_JSON' -> bấm Edit (hoặc Update).")
    print("3. Nhấn Ctrl+V để dán token mới vào -> bấm 'Update secret'.")
    print("=" * 60)

if __name__ == "__main__":
    main()
