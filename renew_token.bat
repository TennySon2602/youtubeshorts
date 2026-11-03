@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Đang mở trình duyệt xác thực YouTube OAuth...
python renew_token.py
pause
