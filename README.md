# 🎬 Dark Curiosity & Science Facts - YouTube Shorts Automation Pipeline

Hệ thống tự động hóa 100% quy trình sản xuất và đăng tải video ngắn (YouTube Shorts) chuẩn viral:
- **Kịch bản**: Niche khoa học bí ẩn, rùng rợn, giật gân (Dark Curiosity & Science Facts) bằng tiếng Anh chuẩn với giọng điệu hài hước, châm biếm ("damn", "coward", "freaking out").
- **Âm thanh & Phụ đề**: Giọng đọc AI tự nhiên (`en-US-ChristopherNeural`) kết hợp tạo phụ đề **từng từ một (1-word-at-a-time)**, viền đen dày, chữ vàng nổi bật chuẩn YouTube Shorts.
- **Hình ảnh**: Background Minecraft gameplay parkour không bản quyền (vertical 1080x1920) + khung nội dung ở giữa chuyển cảnh liên tục sau mỗi câu nói.
- **Hoàn toàn miễn phí trên Cloud**: Chạy tự động qua **GitHub Actions** (không cần bật máy tính, không tốn dung lượng ổ cứng).

---

## 🚀 Hướng dẫn kích hoạt chạy tự động trên GitHub Actions

### Bước 1: Tạo Repository mới trên GitHub
1. Truy cập [github.com/new](https://github.com/new).
2. Đặt tên repository (ví dụ: `youtube-shorts-automation`).
3. Chọn chế độ **Private** (khuyên dùng để bảo mật các file cấu hình).
4. Bấm **Create repository**.

---

### Bước 2: Đẩy toàn bộ mã nguồn lên GitHub
Mở PowerShell tại thư mục dự án và chạy các lệnh sau (thay URL bằng link repo GitHub của bạn):

```bash
git remote add origin https://github.com/<your-username>/youtube-shorts-automation.git
git push -u origin main
```

---

### Bước 3: Cấu hình GitHub Secrets (Quan trọng)
Truy cập vào Repository trên GitHub:
$\rightarrow$ **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions** $\rightarrow$ Bấm **New repository secret**.

Thêm 2 Secret sau:

1. **`YOUTUBE_TOKEN_JSON`**:
   - Mở file `token.json` trên máy bạn (tại `C:\Users\ASUS\.gemini\antigravity\scratch\dark_curiosity_automation\token.json`) bằng Notepad.
   - Copy toàn bộ nội dung JSON đó và dán vào giá trị của Secret này.
   - *(Secret này chứa `refresh_token` đã xác thực với kênh YouTube của bạn, giúp máy chủ GitHub tự động upload video mà không cần đăng nhập lại).*

2. **`OXION_API_KEY`** (Tùy chọn):
   - Nhập API Key Oxion / OpenAI nếu bạn muốn sinh kịch bản động mới mỗi ngày qua LLM. (Nếu không có, hệ thống sẽ tự động dùng kho kịch bản viral chọn lọc có sẵn, không bao giờ lo bị lỗi).

---

### Bước 4: Chạy thử và Lịch biểu tự động

- **Chạy thử ngay lập tức (1-Click)**:
  - Vào tab **Actions** trên GitHub $\rightarrow$ Chọn workflow **"Daily Automated YouTube Shorts"** bên trái $\rightarrow$ Bấm nút **Run workflow**.
  - GitHub Actions sẽ tự khởi động máy ảo Ubuntu, cài FFmpeg, dựng video và tải trực tiếp lên kênh YouTube của bạn trong khoảng 2-3 phút!
  
- **Lịch biểu tự động hàng ngày**:
  - File `.github/workflows/daily_shorts.yml` đã được cài đặt lịch chạy tự động:
    `cron: '0 12 * * *'` (chạy vào 19:00 hàng ngày giờ Việt Nam / 07:00 EST sáng Mỹ - khung giờ vàng viewer US xem Shorts).
