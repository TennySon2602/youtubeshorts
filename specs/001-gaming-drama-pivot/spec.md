# FEATURE SPEC: Chuyển dịch Niche sang Tin tức Drama Làng Game (Gaming Drama Shorts)
**Feature ID:** `001-gaming-drama-pivot`
**Ngày tạo:** 2026-11-03
**Trạng thái:** APPROVED / IN PROGRESS

---

## 1. Mục tiêu & Bối cảnh (Why & What)
- **Bối cảnh:** Thay vì các câu chuyện khoa học rùng rợn cũ, người dùng muốn kênh tập trung vào **Drama & Tin tức nóng hổi trong thế giới Game** (Gaming Drama, Lawsuits, Studio Scandals, Roblox Ports).
- **Mục tiêu:**
  1. Xây dựng bộ kịch bản mới xoay quanh các vụ drama game nổi tiếng nhất: *Dark and Darker vs Nexon*, *Vấn nạn port trộm game sang Roblox & DMCA*, *Nintendo kiện Palworld*, *Vụ nổ review Helldivers 2 PSN*, *Thảm họa 400 triệu đô Concord*.
  2. Tự động thu thập bằng chứng thực tế: Logo hãng game, đơn kiện, bài tweet, biểu đồ review bomb Steam, ảnh so sánh đồ họa, clip gameplay B-roll.
  3. Giữ nguyên định dạng chuẩn Shorts: Nền Minecraft Parkour dọc, thẻ bằng chứng 900x600 viền trắng 6px, phụ đề chữ vàng nhảy từng chữ 70pt Arial Black.
  4. Render video kiểm chứng cục bộ và đẩy lên GitHub tự động hóa.

## 2. Tiêu chí thành công (Acceptance Criteria)
- [ ] Kịch bản mang văn phong bình luận châm biếm, cuốn hút, giật gân, tốc độ nói nhanh bằng giọng ChristopherNeural.
- [ ] 100% hình ảnh và video B-roll là **bằng chứng thật** (chụp màn hình Steam, tài liệu pháp lý, logo Nexon/Ironmace/Roblox, so sánh game) khớp từng câu nói.
- [ ] Thẻ media 900x600 viền trắng 6px không bị mất hình hoặc lỗi PTS trên Linux runner.
- [ ] Render thử nghiệm thành công 1 video hoàn chỉnh, trích xuất frame ảnh để kiểm tra nghiệm thu.
- [ ] Push toàn bộ lên GitHub `TennySon2602/youtubeshorts`.
