# SPECIFICATION: Săn Lùng Tin Tức Drama Game Toàn Ngành Tự Động (Autonomous Gaming Drama Hunter)
**Feature ID:** `002-autonomous-drama-hunter`
**Mục tiêu:** Xóa bỏ sự phụ thuộc vào danh sách topic cố định (`topic_id` tĩnh). Tự động tìm kiếm, phân tích và dựng video Shorts cho drama mới nhất của toàn ngành game (Steam, Nintendo, PlayStation, Xbox, Game Devs, Lawsuits, Backlash).

---

## 1. Bối cảnh & Vấn đề (Context & Problem Statement)
Trước đây, hệ thống chỉ hỗ trợ danh sách cứng gồm 5 topic drama cố định. Khi xuất hiện các drama mới nổi (như vụ kiện mới, drama NPH, review bomb, v.v.), hệ thống không tự phát hiện được mà phải sửa code thủ công.
Người dùng yêu cầu:
1. Tự động săn lùng drama mới nhất của toàn ngành game (thời gian thực, không giới hạn danh mục).
2. Tự động phân tích headline thành kịch bản Shorts 8 câu chuẩn viral.
3. Tự động sinh bộ bằng chứng (evidence cards) độ phân giải cao bằng Pillow với các bullet tròn màu sắc và icon phù hợp.
4. Cho phép chạy tự động 100% không cần can thiệp hoặc nhập keyword tùy chỉnh trên GitHub Actions.

---

## 2. Yêu cầu Chức năng (Functional Requirements)
1. **Module `news_hunter.py`**:
   - Truy vấn Google News RSS với query tìm kiếm chuyên sâu về gaming controversy:
     `(video game OR steam OR nintendo OR playstation OR xbox OR "game developer") (controversy OR drama OR lawsuit OR backlash OR boycott OR "review bomb") when:3d`
   - Lọc bỏ các bài báo thể thao, bóng đá, celebrity bằng `FILTER_KEYWORDS` và yêu cầu bắt buộc có `REQUIRED_GAMING_WORDS`.
   - Hỗ trợ tham số `custom_query` (ví dụ: `Roblox`, `Dead by Daylight`, `GTA 6`) khi người dùng muốn chỉ định.
2. **Module `drama_synthesizer.py`**:
   - Chuyển đổi headline tin tức thành kịch bản 8 câu tiếng Anh có cấu trúc viral (Hook -> Bối cảnh -> Cốt lõi -> Bằng chứng -> Động thái NPH -> Phản ứng cộng đồng -> Hậu quả -> Kêu gọi bình luận).
   - Tự động sinh 8 scene (gồm 7 ảnh Pillow evidence cards 1200x800 sắc nét và 1 B-roll clip động hành động).
   - Đảm bảo độc lập 100%, có rule-based fallback không bị gián đoạn kể cả khi thiếu API key AI.
3. **Tích hợp `pipeline.py` & GitHub Actions**:
   - Nếu `TOPIC_QUERY` được cung cấp hoặc để trống/`auto`, pipeline tự động gọi `news_hunter` và `drama_synthesizer`.
   - Cập nhật `.github/workflows/daily_shorts.yml` cho phép nhập `topic_query` tự do hoặc để trống để chạy tự động mỗi ngày.
4. **Chuẩn hiển thị thị giác**:
   - Minecraft parkour 1080x1920 60fps vertical background.
   - Thẻ nổi 900x600 có viền trắng 6px ở `y=260`.
   - Phụ đề 1 từ màu vàng font Arial Black cỡ 70, viền đen dày, căn giữa ở `y=1475` (`MarginV=890`).

---

## 3. Tiêu chí Nghiệm thu (Acceptance Criteria)
- [x] Chạy `news_hunter.py` trả về danh sách drama game thực tế mới nhất trong 3 ngày qua mà không lẫn tin thể thao.
- [x] Tạo thành công bộ asset `assets/topics/drama_<slug>/` với đầy đủ kịch bản, ảnh bằng chứng Pillow, clip và cúp đăng ký.
- [x] Render video thành công với FFmpeg, không lỗi font, không mất glyph, phụ đề vàng 1-từ khớp giọng đọc Edge-TTS.
- [x] GitHub Actions workflow sẵn sàng với input `topic_query`.
