"""
TikTok OAuth 2.0 Token Generator for GTA VI Shorts Automation
Automatically opens browser, captures auth code, and retrieves Access Token + Refresh Token.
"""

import os
import sys
import json
import urllib.parse
import webbrowser
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY", "awtbu0l2t6tw00zn")
CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "UcmYPH53gJZoBip2jewVjPGdHw7TREYz")
PORT = 8080
REDIRECT_URI = f"http://localhost:{PORT}/callback"
TOKEN_FILE = Path(__file__).parent / "tiktok_token.json"

captured_code = None

class TikTokOAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global captured_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            captured_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <html>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #0F172A; color: white;">
                <h1 style="color: #00FFCC;">🎉 ĐĂNG NHẬP TIKTOK THÀNH CÔNG!</h1>
                <p>Bot đã nhận được mã xác thực. Token đang được tạo và tự động lưu lại.</p>
                <p>Bạn có thể đóng cửa sổ trình duyệt này và quay lại terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        elif "error" in params:
            err = params.get("error_description", ["Unknown error"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = f"""
            <html>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #1E293B; color: white;">
                <h1 style="color: #EF4444;">❌ LỖI XÁC THỰC TIKTOK</h1>
                <p>{err}</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(200)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence console log noise
        pass

def exchange_code_for_token(code: str):
    print("\n[2/3] Đang gửi mã xác thực tới TikTok để lấy Access Token...")
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }

    resp = requests.post(token_url, headers=headers, data=data, timeout=30)
    res_json = resp.json()

    if resp.status_code == 200 and "data" in res_json and "access_token" in res_json["data"]:
        token_data = res_json["data"]
        # Save token
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)
        print(f"✅ Đã lưu token thành công vào: {TOKEN_FILE.name}")
        
        access_token = token_data.get("access_token")
        
        # Copy to clipboard
        try:
            compact_json = json.dumps(token_data)
            process = subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", "$input | Set-Clipboard"],
                stdin=subprocess.PIPE,
                text=True
            )
            process.communicate(input=compact_json)
            print("📋 [3/3] ĐÃ TỰ ĐỘNG COPY TOÀN BỘ TIKTOK TOKEN JSON VÀO CLIPBOARD CỦA BẠN!")
        except Exception as e:
            print(f"⚠️ Không thể tự copy vào clipboard: {e}")

        print("\n" + "=" * 60)
        print("🎉 TIKTOK ACCESS TOKEN ĐÃ SẴN SÀNG:")
        print(f"Access Token: {access_token[:15]}...{access_token[-10:]}")
        print("Expires In: 24 Hours (Có thể tự động refresh bằng refresh_token)")
        print("=" * 60)
        return True
    else:
        print(f"❌ Lỗi khi đổi token từ TikTok: {res_json}")
        return False

def main():
    print("=" * 60, flush=True)
    print("🔑 CÔNG CỤ TẠO TIKTOK ACCESS TOKEN TỰ ĐỘNG", flush=True)
    print("=" * 60, flush=True)

    scopes = "user.info.basic,video.upload,video.publish"
    auth_url = (
        f"https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={CLIENT_KEY}"
        f"&scope={scopes}"
        f"&response_type=code"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&state=tiktok_gta_auth"
    )

    server = HTTPServer(("localhost", PORT), TikTokOAuthHandler)
    print(f"\n[1/3] Máy chủ xác thực cục bộ đang chạy tại http://localhost:{PORT}...", flush=True)
    print("Đang tự động mở trình duyệt để bạn ủy quyền kênh TikTok...", flush=True)
    print(f"\nNếu trình duyệt không tự mở, hãy click hoặc copy link này:\n{auth_url}\n", flush=True)

    webbrowser.open(auth_url)

    # Wait for one incoming request
    while captured_code is None:
        server.handle_request()

    server.server_close()

    if captured_code:
        exchange_code_for_token(captured_code)
    else:
        print("❌ Không nhận được mã code từ TikTok!")

if __name__ == "__main__":
    main()
