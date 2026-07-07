# -*- coding: utf-8 -*-
"""
Memory-First hook (Rule 0) — UserPromptSubmit, keyword-gated, TWO-TIER.

The answer-ladder idea (cheap lookup before deep work) applied to Claude Code's
own memory: not every "recall" prompt deserves the full 6-8-round memory dig.

  Tier PLANNING (light)  — "what next / plan / continue / resume" prompts want
                           the CURRENT plan/status, not a deep history dig. Nudge
                           to read the cheap curated sources (LESSONS + status
                           docs) with 1-2 tool calls, and only escalate if those
                           don't answer. (Fixes lesson 116: a 1-line "tiếp theo
                           làm gì?" used to trigger the full ladder ~= 10% limit.)

  Tier RECALL (full)     — genuine past-work recall ("đã…chưa", "how did we",
                           "where is", "last time") warrants the full ladder:
                           LESSONS -> claude-mem -> codebase-memory -> filesystem.

Classification is deterministic (Rule 5 — code decides the tier, not the model).
PLANNING takes precedence when both match (continuation is planning, not a dig).

Keyword-gated so normal prompts are untouched. Stdlib-only (json/re/sys) -> runs
on any python. Fail-safe: any error -> exit 0, insert nothing, never block the
prompt. UTF-8 buffer I/O -> bypass Windows cp1252 that corrupts Vietnamese both
on read (regex miss) and write (UnicodeEncodeError).
"""
from __future__ import annotations  # `str | None` hint safe on py<3.10

import sys
import json
import re

# ── Tier PLANNING: what-next / plan / continuation → light pointer ───────────
# Liberal on purpose: over-matching the LIGHT tier is cheap; the harm we avoid
# is the opposite (firing the heavy ladder on a planning one-liner).
PLANNING_PATTERNS = [
    # --- Vietnamese ---
    r"tiếp theo",
    r"kế tiếp",
    r"bước (tiếp|kế|sau|này|tới)",
    r"(làm|còn) (gì|việc|bước).{0,12}(tiếp|nữa|kế)",   # "làm gì tiếp", "còn việc gì nữa"
    r"kế hoạch",
    r"\bplan\b|plan của|roadmap|lộ trình",
    r"tiếp tục",
    r"làm tiếp|tiếp đi",
    r"quay lại (vụ|việc|vấn đề|chuyện|task)",
    r"còn (gì|bước|việc|task).{0,15}(nữa|phải|chưa|không)",
    # --- English ---
    r"\bnext step\b|\bnext task\b",
    r"what(?:'s| is| should we do)?.{0,10}\bnext\b",
    r"\bcontinue\b|\bresume\b|\bpick up where\b",
    r"\bwhat's the plan\b|\bour plan\b|\broadmap\b",
]

# ── Tier RECALL: genuine past-work recall → full ladder ──────────────────────
RECALL_PATTERNS = [
    # --- Vietnamese ---
    r"đã.{0,40}chưa",          # "đã làm X chưa"
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

_PLANNING_RE = re.compile("|".join(PLANNING_PATTERNS), re.IGNORECASE | re.UNICODE)
_RECALL_RE = re.compile("|".join(RECALL_PATTERNS), re.IGNORECASE | re.UNICODE)

REMINDER_PLANNING = (
    "[Memory-First / Rule 0 — làn NHẸ] Prompt này hỏi KẾ HOẠCH / BƯỚC KẾ / nối "
    "mạch việc. ĐỪNG Read cả LESSONS.md (~25k tokens, đụng trần Read). Tra bằng "
    "CODE trước (Rule 5 — code query miễn phí, LLM chỉ khi MISS):\n"
    "1. Grep .claude/LESSONS.md theo keyword/tag câu hỏi (vd tag [webapp]/[seshat]) "
    "→ chỉ Read các dòng KHỚP, không đọc cả file.\n"
    "2. Grep/tail 'Next Steps' / TODO gần nhất trong BUILD_STATUS.md / "
    "IMPLEMENTATION_NOTES.md (không đọc cả file).\n"
    "3. CHỈ leo full ladder (claude-mem / codebase-memory) hoặc gọi LLM tổng hợp "
    "khi code-query ở trên MISS. Đừng fan-out 6-8 vòng cho câu 1 dòng."
)

REMINDER_RECALL = (
    "[Memory-First / Rule 0 — làn ĐẦY ĐỦ] Prompt này có dấu hiệu RECALL (hỏi về "
    "việc đã làm trước đó). TRƯỚC khi Glob/Grep filesystem, tra memory theo thứ tự:\n"
    "1. Grep .claude/LESSONS.md theo keyword/tag câu hỏi (code query, miễn phí) → "
    "Read các dòng KHỚP; chỉ Read cả file khi cần bối cảnh rộng (~25k tokens).\n"
    "2. claude-mem (worker mode): ToolSearch \"select:mcp__plugin_claude-mem_mcp-search__search,"
    "mcp__plugin_claude-mem_mcp-search__get_observations\" rồi search() với keyword câu hỏi, "
    "get_observations([ID]) để bung chi tiết. (observation_search/observation_add KHÔNG chạy ở "
    "worker mode — đừng gọi.)\n"
    "3. Câu hỏi về code/kiến trúc: ToolSearch \"select:mcp__codebase-memory__search_code,"
    "mcp__codebase-memory__query_graph\" và tra trước.\n"
    "4. Chỉ search file khi memory không trả lời được. Nếu memory trống -> nói rõ, đừng đoán."
)


def classify(prompt: str) -> str | None:
    """Return 'planning' | 'recall' | None for a prompt.

    PLANNING wins when both match — a continuation/what-next prompt should take
    the cheap lane even if it also reads as recall.
    """
    if _PLANNING_RE.search(prompt):
        return "planning"
    if _RECALL_RE.search(prompt):
        return "recall"
    return None


def main():
    # Đọc/ghi UTF-8 tường minh qua buffer -> bỏ qua locale Windows (cp1252)
    # vốn làm hỏng tiếng Việt cả khi nhận prompt lẫn khi ghi reminder.
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", "replace")
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    tier = classify(data.get("prompt", "") or "")
    if tier is None:
        sys.exit(0)

    reminder = REMINDER_PLANNING if tier == "planning" else REMINDER_RECALL
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": reminder,
        }
    }
    sys.stdout.buffer.write(json.dumps(output, ensure_ascii=False).encode("utf-8"))
    sys.exit(0)


if __name__ == "__main__":
    main()
