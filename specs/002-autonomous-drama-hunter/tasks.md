# IMPLEMENTATION TASKS: Săn Lùng Tin Tức Drama Game Toàn Ngành Tự Động
**Feature ID:** `002-autonomous-drama-hunter`
**Trạng thái:** COMPLETED

---

## Danh sách công việc (Checklist)

- [x] **Task 1: Xây dựng Module Săn Tin Tức Drama (`news_hunter.py`)**
  - Quét Google News RSS với bộ lọc chuyên sâu về gaming controversy.
  - Lọc bỏ tin rác, thể thao, chính trị.
  - Hỗ trợ custom query và tự động lấy tin hot nhất.

- [x] **Task 2: Xây dựng Module Tổng Hợp Drama & Dựng Bằng Chứng (`drama_synthesizer.py`)**
  - Tự động sinh kịch bản 8 câu tiếng Anh chuẩn viral.
  - Sinh tiêu đề, mô tả SEO và tags.
  - Sử dụng Pillow vẽ tự động 7 thẻ bằng chứng 1200x800 sắc nét với bullet tròn màu.
  - Ghép nối video B-roll và biểu tượng đăng ký kênh.

- [x] **Task 3: Tích hợp vào Pipeline Chính (`pipeline.py`)**
  - Tiếp nhận `TOPIC_QUERY` từ môi trường hoặc kích hoạt chế độ auto-hunting.
  - Tự động dựng thư mục tài nguyên và kịch bản động trước khi render.

- [x] **Task 4: Cập nhật GitHub Actions Workflow (`.github/workflows/daily_shorts.yml`)**
  - Chuyển `topic_id` dạng choice tĩnh sang `topic_query` dạng chuỗi tự do (default `auto`).

- [x] **Task 5: Nghiệm thu Render Cục bộ**
  - Chạy thử nghiệm với topic động thực tế (*Dead by Daylight Devs Backlash*).
  - Trích xuất frame hình ảnh kiểm tra bố cục card, phụ đề vàng 1-từ và background Minecraft.

- [x] **Task 6: Commit & Push lên GitHub Repository**
  - Đồng bộ toàn bộ mã nguồn lên nhánh `main` của `TennySon2602/youtubeshorts`.
