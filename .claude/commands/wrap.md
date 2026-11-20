---
description: Wrap-up cuối task — rút bài học, cô đọng thành rule, route theo escalation ladder (Tier-1 LESSONS.md ghi thẳng; Tier-2 CLAUDE.md / Tier-3 BUILD_STATUS.md chỉ đề xuất diff).
allowed-tools: Read, Edit, Write, ToolSearch, mcp__plugin_claude-mem_mcp-search__search
---

# /wrap — Khép vòng task trước khi /clear

Mục tiêu: cô đọng những gì học được trong session NÀY thành dạng mà Memory-First (Rule 0)
sẽ đọc lại được ở task sau. Đây là mắt xích: `/wrap` GHI vào đúng store mà Rule 0 ĐỌC.

Chạy tuần tự. KHÔNG bỏ bước. KHÔNG tự ghi vào file — chỉ đề xuất diff (trừ `.claude/LESSONS.md`, xem Bước 4).

---

## Bước 1 — Quét session, rút bài học

Đọc lại hội thoại của session hiện tại. Rút bài học CHỈ từ 3 nguồn (bỏ qua mọi thứ khác):

| Nguồn | Tín hiệu nhận biết |
|-------|--------------------|
| **Root-cause** | Một bug/lỗi đã tìm ra nguyên nhân gốc — và cách tránh lần sau |
| **User sửa tôi** | Chỗ owner (người đang làm việc với tôi) chỉnh hướng / bác bỏ giả định / sửa cách làm của tôi |
| **Pattern lặp** | Cùng một loại lỗi hoặc quyết định xuất hiện ≥2 lần |

Nếu không có bài học thật nào ở cả 3 nguồn → nói thẳng "Session này không có lesson đáng lưu",
KHÔNG bịa lesson cho đủ (Rule 12 fail-loud).

Lọc bỏ trước khi đi tiếp (chi tiết ở `docs/MEMORY_ARCHITECTURE.md`, mục "What is worth saving"):
- Thứ tự hết hạn: tên nhánh, port, việc đang dở, "file X là bản mới nhất". Chỗ của nó là
  `docs/BUILD_STATUS.md`, không phải lesson.
- Kết luận của chính agent mà owner chưa xác nhận: nếu vẫn ghi thì gắn tag `[inferred]`,
  để phân biệt với quyết định owner đã chốt (`[owner]`).

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
| Skill | Một QUY TRÌNH nhiều bước đã lặp ≥2 lần (checklist release, khuôn báo cáo, quy trình QA) | **Đề xuất skill** `.claude/skills/<tên>/SKILL.md` |

Vì sao quy trình thành skill mà không thành lesson: `CLAUDE.md` và memory nạp vào MỌI session,
còn skill chỉ nạp mô tả một dòng cho tới khi được dùng. Quy trình dài để trong lesson vừa tốn
token vừa dễ bị đọc sót bước.

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
- Đọc file đích trước (Rule 8). Trình diff đề xuất (before/after) cho owner duyệt.
- Chỉ chạy Edit sau khi owner đồng ý. Nếu owner không duyệt trong lượt này → để nguyên,
  lesson vẫn an toàn ở Tier 1.

**Skill → CHỈ ĐỀ XUẤT, KHÔNG tự Write:**
- Trình bản nháp SKILL.md: frontmatter `name` + `description` (một câu nói rõ KHI NÀO dùng),
  rồi các bước của quy trình đúng như đã chạy trong session này.
- Kiểm `.claude/skills/` trước: đã có skill gần giống thì đề xuất sửa skill đó, không tạo trùng.
- Chỉ Write sau khi owner đồng ý. Tối đa 3 đề xuất mỗi lần /wrap; không đề xuất lại skill
  owner đã từ chối.

## Bước 5 — Tổng kết

In một bảng: mỗi lesson | tier | trạng thái (đã ghi LESSONS.md / chờ duyệt diff / đề xuất skill).
Sau đó nhắc: "Có thể /clear an toàn — Tier 1 đã bền, Tier 2/3 và skill chờ bạn duyệt."
