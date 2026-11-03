# IMPLEMENTATION PLAN: Săn Lùng Tin Tức Drama Game Toàn Ngành Tự Động
**Feature ID:** `002-autonomous-drama-hunter`
**Trạng thái:** COMPLETED

---

## 1. Thiết kế Kiến trúc (Architecture Design)
1. **News Hunter (`news_hunter.py`)**:
   - Sử dụng thư viện `urllib.request` và `xml.etree.ElementTree` để parse Google News RSS không cần API key.
   - Cơ chế lọc đa tầng: loại bỏ tin ngoài ngành (Soccer, NFL, Movies, Politics), lọc trùng lặp qua Jaccard similarity / normalized slug.
2. **Drama Synthesizer (`drama_synthesizer.py`)**:
   - Generator script: Tạo 8 câu thoại tiếng Anh kịch tính, chuẩn YouTube Shorts.
   - Pillow Evidence Renderer: Tạo card 1200x800 với:
     - Header badge nền đỏ / vàng / xanh.
     - Tiêu đề card và phụ đề giải thích.
     - Vạch ngăn cách trang trọng.
     - 4 bullet points với hình tròn màu (`draw.ellipse`) sắc nét, tránh lỗi font unicode.
     - Footer watermark `BREAKING GAMING INVESTIGATION`.
3. **Pipeline Integration (`pipeline.py`)**:
   - Ưu tiên 1: `TOPIC_QUERY` từ biến môi trường.
   - Ưu tiên 2: Tự động quét RSS lấy drama game #1 trong ngày nếu không có biến môi trường hoặc để `auto`.
   - Ưu tiên 3: Dự phòng xoay vòng 5 topic kinh điển nếu mất kết nối mạng.
4. **GitHub Workflow CI/CD (`.github/workflows/daily_shorts.yml`)**:
   - Đổi input `topic_id` thành `topic_query` (type: string, default: 'auto').

---

## 2. Rủi ro & Giải pháp (Risks & Mitigations)
- **Rủi ro font emoji hiển thị hình vuông lỗi (tofu)**: Sử dụng hình học Pillow (`draw.ellipse`) vẽ trực tiếp chấm tròn màu thay vì ký tự unicode.
- **Rủi ro tin tức thể thao lọt vào**: Bổ sung danh sách từ khóa bắt buộc ngành game và danh sách từ khóa cấm.
- **Rủi ro Google RSS bị rate-limit**: Giữ fallback 5 topic kinh điển trong `pipeline.py` để pipeline luôn hoàn thành 100%.
