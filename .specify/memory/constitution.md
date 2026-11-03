# PROJECT CONSTITUTION & AGENT GOVERNANCE
**Project:** YouTube Shorts Dark Curiosity Automation (`youtubeshorts`)
**Framework:** Spec-Driven Development (SDD) via GitHub Spec Kit
**Version:** 1.0.0
**Last Updated:** 2026-11-03

---

## 🏛️ TỔNG QUAN VỀ HIẾN PHÁP DỰ ÁN (CONSTITUTION)
Tài liệu này là **bộ quy tắc tối cao** quy định cách thức AI Agent và Lập trình viên tương tác, thiết kế và sinh mã nguồn trong toàn bộ vòng đời của repository này. 
Mọi tính năng mới, chỉnh sửa lỗi (bugfix) hoặc nâng cấp kiến trúc đều **BẮT BUỘC** phải tuân thủ nghiêm ngặt các nguyên tắc dưới đây.

---

## 📜 5 NGUYÊN TẮC CỐT LÕI (CORE PRINCIPLES)

### Nguyên tắc I: Specification Before Implementation (Đặc tả trước khi viết Code)
* **Quy tắc:** Tuyệt đối không nhảy vào viết code ngay ("vibe coding"). Mọi yêu cầu phải đi qua quy trình 4 bước chuẩn Spec Kit:
  1. **Spec (`spec.md`):** Làm rõ *Làm cái gì (What)* và *Tại sao (Why)*, tiêu chí thành công (Acceptance Criteria), các trường hợp ngoại lệ (Edge cases).
  2. **Plan (`plan.md`):** Lựa chọn công nghệ, cấu trúc thư mục, luồng dữ liệu (Data flow) và đánh giá rủi ro kỹ thuật.
  3. **Tasks (`tasks.md`):** Chia nhỏ công việc thành từng task độc lập (atomic), có checklist kiểm thử cụ thể.
  4. **Implement:** AI chỉ được phép sinh code bám sát checklist trong `tasks.md`.

### Nguyên tắc II: Media & Content Fidelity (Tuyệt đối chuẩn xác về Nội dung & Tư liệu)
* **Quy tắc:** Trong các hệ thống tự động hóa sản xuất nội dung / video:
  * Hình ảnh (`.jpg`, `.png`) và video B-roll (`.mp4`, `.webm`) phải **khớp 100% với ngữ cảnh câu nói/kịch bản**.
  * Cấm tuyệt đối việc sử dụng ảnh/video placeholder ngẫu nhiên, hình ảnh lạc đề không liên quan (ví dụ: đang nói về xác ướp thì không được dùng ảnh cô gái đọc sách, nói về dơi không được dùng ảnh máy chơi game).
  * Tất cả tài nguyên media nội bộ phải được lưu trữ chuẩn hóa theo topic tại `assets/topics/<topic_id>/` và tối ưu dung lượng (video $\le$ 5MB, ảnh $\le$ 2MB).

### Nguyên tắc III: Cross-Platform & CI/CD Portability (Tương thích đa nền tảng)
* **Quy tắc:** Mã nguồn phải chạy hoàn hảo cả ở môi trường phát triển cục bộ (Windows PowerShell) và môi trường thực thi tự động (Ubuntu Linux trên GitHub Actions).
  * FFmpeg filter, đường dẫn file (`Path.as_posix()`) và timestamp PTS phải được re-encode monotonic để tránh drop frame trên Linux.
  * Mọi tham số nhạy cảm (API Keys, Refresh Tokens, Client Secrets) phải nạp qua Environment Variables / GitHub Secrets, tuyệt đối không commit file bí mật lên Git.

### Nguyên tắc IV: Deterministic & Robust Pipelines (Quy trình xác định & Chống lỗi)
* **Quy tắc:**
  * Giảm thiểu sự phụ thuộc vào các API bên thứ 3 có rate-limit không ổn định trong lúc render video.
  * Xử lý fallback có kiểm soát: Nếu asset thiếu, phải raise lỗi rõ ràng thay vì âm thầm chèn dữ liệu rác.
  * Phụ đề chữ và audio phải luôn đồng bộ thời gian (Word-level synchronization với Edge-TTS).

### Nguyên tắc V: Atomic Tasks & Continuous Verification (Kiểm chứng liên tục)
* **Quy tắc:**
  * Sau khi hoàn thành mỗi task, AI phải thực hiện xác minh (Verification): chạy thử nghiệm, trích xuất frame (`ffmpeg -ss`), kiểm tra log thực tế trước khi đánh dấu hoàn thành.
  * Mỗi commit Git phải mang thông điệp rõ ràng theo chuẩn Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`).

---

## 🛠️ QUY TRÌNH THỰC HIỆN KHI CÓ YÊU CẦU MỚI (WORKFLOW)
Khi người dùng đưa ra một yêu cầu mới, AI Agent sẽ tự động:
1. **Khởi tạo hoặc cập nhật Feature Spec** trong thư mục `specs/`:
   - `specs/<feature-name>/spec.md`
   - `specs/<feature-name>/plan.md`
   - `specs/<feature-name>/tasks.md`
2. **Yêu cầu người dùng xác nhận** kế hoạch trước khi can thiệp vào các file code chính (`pipeline.py`, `youtube_uploader.py`, workflows).
3. **Thực thi và kiểm thử trực tiếp**, xuất bằng chứng (frame ảnh, kết quả build, log terminal).
