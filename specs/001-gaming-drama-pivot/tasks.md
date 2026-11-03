# IMPLEMENTATION TASKS: Chuyển dịch Niche sang Drama Game
**Feature ID:** `001-gaming-drama-pivot`
**Trạng thái:** COMPLETED

---

## Danh sách công việc (Checklist)

- [x] **Task 1: Xây dựng Kịch bản Drama Làng Game trong `pipeline.py`**
  - Viết kịch bản tiếng Anh lôi cuốn, giật gân, tốc độ cao cho 5 topic: `dark_and_darker`, `roblox_ports`, `nintendo_palworld`, `helldivers_sony`, `concord_disaster`.

- [x] **Task 2: Thu thập và Tối ưu hóa Tài nguyên Bằng chứng (Evidence Media)**
  - Tải và tạo các tài nguyên bằng chứng chân thực cho từng topic (video B-roll + ảnh screenshot bằng chứng).
  - Đảm bảo mỗi topic có đầy đủ `scene_0` đến `scene_N` tương ứng với từng câu thoại.

- [x] **Task 3: Cập nhật GitHub Workflow**
  - Đồng bộ danh sách choice `topic_id` trong `.github/workflows/daily_shorts.yml`.

- [x] **Task 4: Render Thử nghiệm Cục bộ & Trích xuất Frame Nghiệm thu**
  - Chạy pipeline cho topic `dark_and_darker` và `roblox_ports` với `SKIP_UPLOAD=1`.
  - Trích xuất frame hình ảnh để kiểm tra chất lượng video, phụ đề và thẻ bằng chứng.

- [x] **Task 5: Commit & Push lên GitHub**
  - Đẩy code và tài nguyên lên `TennySon2602/youtubeshorts`.
