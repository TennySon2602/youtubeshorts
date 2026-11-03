# ANTIGRAVITY & AI AGENT PROJECT INSTRUCTIONS

> [!IMPORTANT]
> Dự án này áp dụng phương pháp **Spec-Driven Development (SDD)** lấy cảm hứng từ **GitHub Spec Kit** (`github/spec-kit`).
> Mọi trợ lý AI (Antigravity, Copilot, Claude) khi làm việc trong repository này **bắt buộc** phải tuân theo các nguyên tắc được định nghĩa dưới đây.

---

## 1. Hiến pháp dự án (Project Constitution)
Tất cả các nguyên tắc tối cao của dự án được lưu tại:
👉 [Hiến pháp dự án: `.specify/memory/constitution.md`](file:///.specify/memory/constitution.md)

Khi nhận một nhiệm vụ phức tạp hoặc phát triển tính năng mới:
1. **Không "vibe coding":** Không viết code khi chưa thống nhất giải pháp.
2. **Tuân thủ quy trình 4 bước:**
   - **Spec (`spec.md`):** Làm rõ yêu cầu, kịch bản, tiêu chuẩn nghiệm thu.
   - **Plan (`plan.md`):** Thiết kế kiến trúc kỹ thuật và giải pháp xử lý.
   - **Tasks (`tasks.md`):** Chia nhỏ công việc thành checklist độc lập.
   - **Implement & Verify:** Viết code và trích xuất bằng chứng kiểm thử (log, frame hình ảnh, video).

---

## 2. Các quy định kỹ thuật bất biến (Non-negotiable Standards)
- **Chuẩn xác nội dung (Content Fidelity):**
  - Mọi hình ảnh và video B-roll phải gắn chặt với từng câu nói trong kịch bản. Tuyệt đối không dùng ảnh placeholder rác hoặc không liên quan.
- **Tiêu chuẩn video Shorts:**
  - Định dạng: 1080x1920 (9:16), 60fps.
  - Khung nội dung minh họa (Content Card): 900x600, viền trắng 6px sắc nét, tọa độ `y=260`.
  - Phụ đề (Subtitles): Chữ vàng tươi, viền đen dày, phông `Arial Black 70pt`, hiển thị nhảy đúng từng từ (1-word-at-a-time) đồng bộ với giọng nói Edge-TTS.
- **Tương thích đa nền tảng:**
  - Đảm bảo lệnh FFmpeg và luồng Concat PTS chạy mượt mà trên cả Windows PowerShell và GitHub Actions (Ubuntu).
- **Chế độ bảo mật & Upload:**
  - Token OAuth 2.0 và API Key chỉ lấy qua biến môi trường.
  - Video được đăng mặc định ở chế độ `public`.
