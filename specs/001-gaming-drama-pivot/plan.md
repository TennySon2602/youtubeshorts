# TECHNICAL PLAN: Kiến trúc Kịch bản Drama Game & Thu thập Bằng chứng
**Feature ID:** `001-gaming-drama-pivot`
**Tham chiếu:** `spec.md`, `.specify/memory/constitution.md`

---

## 1. Danh sách Chủ đề Drama Game (New TOPICS in `pipeline.py`)

1. **`dark_and_darker`** (The Most Insane Gaming Lawsuit in History):
   - Hook: How an indie studio got sued by gaming giant Nexon over stolen code and released their game via torrents.
   - Evidence/Media: Nexon HQ, Ironmace logo, Project P3 vs Dark and Darker comparison, Police raid headlines, Steam DMCA delisting notice, Supreme court fine document.
2. **`roblox_ports`** (Roblox's Multi-Million Dollar Game Stealing Epidemic):
   - Hook: How kids are porting entire AAA & indie games into Roblox and making millions while real devs get banned by fake DMCA.
   - Evidence/Media: Roblox logo, Lethal Company clone in Roblox, Counter-Strike Roblox clone, Robux cash symbol, DMCA takedown notice, Dev tweet outrage.
3. **`nintendo_palworld`** (Nintendo's Nuclear Lawsuit Against Palworld):
   - Hook: Palworld made $500M in a month, so Nintendo unleashed their legal ninjas with a patent lawsuit.
   - Evidence/Media: Palworld key art, Nintendo Tokyo HQ, Patent filing diagram, Pokeball catching mechanic, $500M cash graphic, Trophy.
4. **`helldivers_sony`** (The Day Gamers Defeated Sony):
   - Hook: Sony forced PSN login on Helldivers 2, locking out 177 countries, and faced the biggest Steam review bomb in gaming history.
   - Evidence/Media: Helldivers 2 logo, Sony PSN sign-in screen, Steam Overwhelmingly Negative chart (200k red reviews), Arrowhead CEO tweet, Sony apology tweet.
5. **`concord_disaster`** (The $400 Million Game That Died in 14 Days):
   - Hook: Sony spent 8 years and $400 million on Concord, only for it to shut down after two weeks with 600 players.
   - Evidence/Media: Concord cover art, Steam chart showing 660 peak players, Firewalk Studios logo, "Servers Shutting Down" announcement, Full refund email.

## 2. Luồng xử lý kỹ thuật (Pipeline Architecture)
- Cập nhật biến `TOPICS` trong `pipeline.py`.
- Tự động tải & chuẩn bị assets trong `assets/topics/<topic_id>/` (gồm cả video clip gameplay B-roll và ảnh bằng chứng).
- Tối ưu dung lượng hình ảnh $\le 500$KB và video $\le 3$MB để repo gọn gàng.
- Cập nhật workflow `.github/workflows/daily_shorts.yml` với danh sách topic mới.
