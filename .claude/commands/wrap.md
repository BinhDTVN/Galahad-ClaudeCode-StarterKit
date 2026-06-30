---
description: Wrap-up cuối task — rút bài học, cô đọng thành rule, route theo escalation ladder (Tier-1 LESSONS.md ghi thẳng; Tier-2 CLAUDE.md / Tier-3 BUILD_STATUS.md chỉ đề xuất diff).
allowed-tools: Read, Edit, ToolSearch, mcp__plugin_claude-mem_mcp-search__search
---

# /wrap — Khép vòng task trước khi /clear

Mục tiêu: cô đọng những gì học được trong session NÀY thành dạng mà Memory-First (Rule 0)
sẽ đọc lại được ở task sau. Đây là mắt xích: `/wrap` GHI vào đúng store mà Rule 0 ĐỌC.

Chạy tuần tự. KHÔNG bỏ bước. KHÔNG tự ghi vào file — chỉ đề xuất diff (trừ claude-mem, xem Bước 4).

---

## Bước 1 — Quét session, rút bài học

Đọc lại hội thoại của session hiện tại. Rút bài học CHỈ từ 3 nguồn (bỏ qua mọi thứ khác):

| Nguồn | Tín hiệu nhận biết |
|-------|--------------------|
| **Root-cause** | Một bug/lỗi đã tìm ra nguyên nhân gốc — và cách tránh lần sau |
| **User sửa tôi** | Chỗ Galahad chỉnh hướng / bác bỏ giả định / sửa cách làm của tôi |
| **Pattern lặp** | Cùng một loại lỗi hoặc quyết định xuất hiện ≥2 lần |

Nếu không có bài học thật nào ở cả 3 nguồn → nói thẳng "Session này không có lesson đáng lưu",
KHÔNG bịa lesson cho đủ (Rule 12 fail-loud).

## Bước 2 — Cô đọng mỗi bài học thành ĐÚNG 1 rule

- 1 dòng, mệnh lệnh, có thể kiểm chứng. Ví dụ tốt: "Hook Windows phải đọc/ghi stdin/stdout
  bằng UTF-8 buffer — locale cp1252 làm hỏng tiếng Việt."
- Ví dụ xấu (bỏ): "Cẩn thận với encoding." (không kiểm chứng được, không hành động được).

## Bước 3 — Phân tầng (escalation ladder)

| Tier | Lesson loại nào | Đi đâu |
|------|-----------------|--------|
| 1 | Bài học / quyết định 1 lần | **`.claude/LESSONS.md`** (append 1 dòng, có tag) |
| 2 | Rule **lặp ≥2 lần** hoặc universal | **`CLAUDE.md` gốc** (rule mới hoặc mục `## LESSONS`) |
| 3 | Trạng thái done / TODO của task | **`docs/BUILD_STATUS.md`** |

Quy tắc thăng cấp: mặc định MỌI lesson vào Tier 1. Chỉ thăng lên Tier 2 (CLAUDE.md) khi nó
đã lặp lại ≥2 lần hoặc rõ ràng universal — "saved where the agent reads on every future task".
Đừng làm phình CLAUDE.md bằng lesson một lần.

> Lý do Tier 1 là file, không phải claude-mem: claude-mem chạy **worker mode** → `observation_add`
> KHÔNG ghi được (chỉ server-beta). `.claude/LESSONS.md` là store ghi-được, sống qua `/clear`,
> và Rule 0 đọc nó đầu tiên. Auto-capture của worker chỉ bổ sung (đọc qua `search`).

## Bước 4 — Thực thi routing

**Tier 1 → GHI THẲNG vào `.claude/LESSONS.md`** (deterministic, in-repo, an toàn):
- `Read .claude/LESSONS.md` trước (Rule 8), rồi `Edit` để APPEND mỗi lesson dưới mục `## LESSONS`,
  đúng format: `- [YYYY-MM-DD][tag][tag] <1 rule>`. Tag giúp Rule 0 tra sắc, không lẫn noise.
- Append, KHÔNG sửa/xoá dòng cũ. Ghi xong báo lại các dòng đã thêm.

**Tier 2 (CLAUDE.md) & Tier 3 (BUILD_STATUS.md) → CHỈ ĐỀ XUẤT DIFF, KHÔNG tự Edit:**
- Đọc file đích trước (Rule 8). Trình diff đề xuất (before/after) cho Galahad duyệt.
- Chỉ chạy Edit sau khi Galahad đồng ý. Nếu Galahad không duyệt trong lượt này → để nguyên,
  lesson vẫn an toàn ở Tier 1.

## Bước 5 — Tổng kết

In một bảng: mỗi lesson | tier | trạng thái (đã ghi claude-mem / chờ duyệt diff). Sau đó nhắc:
"Có thể /clear an toàn — Tier 1 đã bền, Tier 2/3 chờ bạn duyệt."
