# LESSONS — Tier-1 memory store

Bài học đã cô đọng từ các task trước. `/wrap` append vào đây; **Rule 0 (Memory-First) đọc file này ĐẦU TIÊN** mỗi khi recall — nó luôn có, rẻ, không lẫn noise auto-capture.

Format mỗi dòng: `- [YYYY-MM-DD][tag][tag] <1 rule mệnh lệnh, kiểm chứng được>`

> Vì claude-mem chạy worker mode (không có manual write tool), đây là store ghi-được duy nhất sống qua `/clear`. Auto-capture của worker bổ sung qua `search`/`get_observations`, nhưng file này là nguồn lessons có chủ đích.

## LESSONS

- [2026-06-28][hook][windows][encoding] Hook/script Python trên Windows phải đọc-ghi stdin/stdout bằng UTF-8 buffer (`sys.stdin.buffer.read().decode("utf-8")` / `sys.stdout.buffer.write(...encode("utf-8"))`). Locale cp1252 làm hỏng tiếng Việt cả khi NHẬN prompt (regex không match) lẫn khi GHI (UnicodeEncodeError trên ký tự có dấu).
- [2026-06-28][claude-mem][runtime] claude-mem ở worker mode: `observation_add`/`observation_search`/`memory_add` đều CHỈ chạy server-beta → fail ở worker. Worker mode chỉ đọc được qua `search`/`timeline`/`get_observations`, và KHÔNG có manual write tool.
