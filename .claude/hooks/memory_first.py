# -*- coding: utf-8 -*-
"""
Memory-First hook (Rule 0) — UserPromptSubmit, keyword-gated.

Khi prompt của user có dấu hiệu "recall" (hỏi về việc đã làm trước đó, VN+EN),
hook chèn additionalContext nhắc agent TRA MEMORY trước khi Glob/Grep filesystem.

Keyword-gated: chỉ chèn khi match pattern recall -> không làm nhiễu prompt thường.
Stdlib-only (json/re/sys) -> chạy với mọi python. Fail-safe: lỗi gì cũng exit 0,
không chèn gì, không bao giờ block prompt (Rule 12 fail-loud nhưng không phá UX).
"""
import sys
import json
import re

# Mẫu recall — Vietnamese + English. So khớp case-insensitive, có unicode.
RECALL_PATTERNS = [
    # --- Vietnamese ---
    r"đã.{0,40}chưa",          # "đã ... chưa" (đã làm X chưa)
    r"hồi (đó|trước|xưa|nãy)",
    r"lần (trước|rồi)",
    r"trước đây",
    r"đã từng|từng làm",
    r"(hôm|bữa|lúc) trước",
    r"(còn|có) nhớ|nhớ không",
    r"(ở|chỗ|nằm|lưu).{0,15}(đâu|nào)",   # ở đâu / lưu ở đâu / file nào / nằm đâu
    r"session (trước|vừa|cũ)",
    r"làm (thế nào|sao|như nào).{0,20}(trước|hồi|lần)",
    # --- English ---
    r"\bhow did we\b",
    r"\bhow do we\b",
    r"\bwhere(?:'s| is| are| was)\b",
    r"\bdid we\b",
    r"\bhave we\b",
    r"\blast time\b",
    r"\bpreviously\b",
    r"\bremember\b",
    r"\bwhat (?:was|did we)\b",
    r"\bearlier we\b",
    r"\bbefore,? we\b",
]

_RECALL_RE = re.compile("|".join(RECALL_PATTERNS), re.IGNORECASE | re.UNICODE)

REMINDER = (
    "[Memory-First / Rule 0] Prompt này có dấu hiệu RECALL (hỏi về việc đã làm trước đó). "
    "TRƯỚC khi Glob/Grep filesystem, hãy tra memory theo thứ tự:\n"
    "1. Read .claude/LESSONS.md (Tier-1 store, luôn có, rẻ) — bài học đã cô đọng.\n"
    "2. claude-mem (worker mode): ToolSearch \"select:mcp__plugin_claude-mem_mcp-search__search,"
    "mcp__plugin_claude-mem_mcp-search__get_observations\" rồi search() với keyword câu hỏi, "
    "get_observations([ID]) để bung chi tiết. (observation_search/observation_add KHÔNG chạy ở "
    "worker mode — đừng gọi.)\n"
    "3. Câu hỏi về code/kiến trúc: ToolSearch \"select:mcp__codebase-memory__search_graph,"
    "mcp__codebase-memory__query_graph,mcp__codebase-memory__trace_call_path\" và tra trước. "
    "(Prefix mcp__codebase-memory__ là tên server bạn đăng ký MCP — đổi nếu đặt khác.)\n"
    "4. Chỉ search file khi memory không trả lời được. Nếu memory trống -> nói rõ, đừng đoán."
)


def main():
    # Đọc/ghi UTF-8 tường minh qua buffer -> bỏ qua locale Windows (cp1252)
    # vốn làm hỏng tiếng Việt cả khi nhận prompt lẫn khi ghi reminder.
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", "replace")
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        # Không parse được input -> không chèn gì, không block.
        sys.exit(0)

    prompt = data.get("prompt", "") or ""
    if not _RECALL_RE.search(prompt):
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": REMINDER,
        }
    }
    sys.stdout.buffer.write(json.dumps(output, ensure_ascii=False).encode("utf-8"))
    sys.exit(0)


if __name__ == "__main__":
    main()
