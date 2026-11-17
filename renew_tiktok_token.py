"""
TikTok OAuth 2.0 Token Generator for GTA VI Shorts Automation
Implements PKCE (code_challenge & code_verifier) as strictly required by TikTok v2 API.
"""

import os
import sys
import json
import base64
import hashlib
import secrets
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

def generate_pkce_pair():
    """
    Generates a cryptographically random code_verifier and its SHA256 code_challenge.
    Required by TikTok v2 OAuth security policies.
    """
    # 60 bytes of URL-safe random string (~80 characters, within 43-128 range)
    verifier = secrets.token_urlsafe(60)
    # SHA-256 hash
    sha256_digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    # Base64-URL encode without padding
    challenge = base64.urlsafe_b64encode(sha256_digest).decode("utf-8").rstrip("=")
    return verifier, challenge

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
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 60px; background: #0F172A; color: white;">
                <h1 style="color: #00FFCC; font-size: 32px;">🎉 ỦY QUYỀN TIKTOK THÀNH CÔNG!</h1>
                <p style="font-size: 18px; color: #94A3B8;">Bot đã bắt được mã xác thực. Đang tạo Access Token và lưu vào hệ thống...</p>
                <p style="font-size: 16px; color: #CBD5E1;">Bạn có thể đóng tab này và quay lại cửa sổ Terminal.</p>
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
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 60px; background: #1E293B; color: white;">
                <h1 style="color: #EF4444; font-size: 32px;">❌ LỖI TIKTOK</h1>
                <p style="font-size: 18px; color: #FCA5A5;">{err}</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(200)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def exchange_code_for_token(code: str, verifier: str):
    print("\n[2/3] Đang gửi mã xác thực kèm code_verifier tới TikTok để lấy Access Token...")
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
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier
    }

    try:
        resp = requests.post(token_url, headers=headers, data=data, timeout=30)
        res_json = resp.json()
    except Exception as e:
        print(f"❌ Lỗi kết nối tới TikTok: {e}")
        return False

    if resp.status_code == 200 and "data" in res_json and "access_token" in res_json["data"]:
        token_data = res_json["data"]
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)
        print(f"✅ Đã lưu token thành công vào: {TOKEN_FILE.name}")
        
        access_token = token_data.get("access_token")
        
        # Copy to clipboard via PowerShell
        try:
            compact_json = json.dumps(token_data)
            process = subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", "$input | Set-Clipboard"],
                stdin=subprocess.PIPE,
                text=True
            )
            process.communicate(input=compact_json)
            print("📋 [3/3] ĐÃ TỰ ĐỘNG COPY TOÀN BỘ TIKTOK TOKEN VÀO CLIPBOARD CỦA BẠN!")
        except Exception as e:
            print(f"⚠️ Không thể tự copy vào clipboard: {e}")

        print("\n" + "=" * 65)
        print("🎉 TIKTOK ACCESS TOKEN ĐÃ SẴN SÀNG:")
        print(f"Access Token: {access_token[:15]}...{access_token[-10:]}")
        print("Expires In: 24 Hours (Hệ thống sẽ tự động làm mới bằng refresh_token)")
        print("=" * 65)
        return True
    else:
        print(f"\n❌ Lỗi khi đổi token từ TikTok (HTTP {resp.status_code}):")
        print(json.dumps(res_json, indent=2, ensure_ascii=False))
        return False

def main():
    print("=" * 65, flush=True)
    print("🔑 CÔNG CỤ TẠO TIKTOK ACCESS TOKEN TỰ ĐỘNG (CHẾ ĐỘ PKCE)", flush=True)
    print("=" * 65, flush=True)

    verifier, challenge = generate_pkce_pair()

    scopes = "user.info.basic,video.upload,video.publish"
    params = {
        "client_key": CLIENT_KEY,
        "scope": scopes,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "state": "tiktok_gta_pkce",
        "code_challenge": challenge,
        "code_challenge_method": "S256"
    }
    auth_url = f"https://www.tiktok.com/v2/auth/authorize/?{urllib.parse.urlencode(params)}"

    server = HTTPServer(("localhost", PORT), TikTokOAuthHandler)
    print(f"\n[1/3] Máy chủ xác thực cục bộ đang chạy tại http://localhost:{PORT}...", flush=True)
    print(f"Đã tạo bảo mật PKCE: code_challenge={challenge[:10]}...", flush=True)
    print("Đang tự động mở trình duyệt để bạn ủy quyền kênh TikTok...", flush=True)
    print(f"\nNếu trình duyệt không tự mở, hãy click hoặc copy link này:\n{auth_url}\n", flush=True)

    webbrowser.open(auth_url)

    # Wait for callback
    while captured_code is None:
        server.handle_request()

    server.server_close()

    if captured_code:
        exchange_code_for_token(captured_code, verifier)
    else:
        print("❌ Không nhận được mã code từ TikTok!")

if __name__ == "__main__":
    main()
