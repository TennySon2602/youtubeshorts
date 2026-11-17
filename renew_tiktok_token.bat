@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Đang mở trình duyệt xác thực TikTok OAuth...
python renew_tiktok_token.py
pause
