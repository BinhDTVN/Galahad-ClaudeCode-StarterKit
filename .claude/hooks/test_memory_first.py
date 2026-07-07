# -*- coding: utf-8 -*-
"""Smoke: memory_first two-tier classifier (Rule 9 — verify the routing intent).

  planning -> light pointer (LESSONS + status docs, 1-2 calls)
  recall   -> full ladder (LESSONS -> claude-mem -> codebase-memory -> fs)
  None     -> no reminder (normal prompt untouched)

Prompts are real diacritic Vietnamese (how Galahad types) + English. Prints are
ASCII-only (lesson 66: diacritic print crashes cp1258 -> FALSE fail).

Run:  PYTHONUTF8=1 python .claude/hooks/test_memory_first.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memory_first import classify  # noqa: E402

# (id, prompt, expected) — id is ASCII-safe for printing; prompt is data.
CASES = [
    # planning / what-next / continuation -> LIGHT (incl. lesson 116's own case)
    ("vn-tiep-theo-plan", "Tiếp theo plan của chúng ta là gì bro?", "planning"),
    ("vn-tiep-tuc", "tiếp tục vấn đề webapp", "planning"),
    ("vn-lam-gi-tiep", "làm gì tiếp theo", "planning"),
    ("vn-buoc-ke", "bước kế tiếp là gì", "planning"),
    ("vn-ke-hoach", "kế hoạch hôm nay ra sao", "planning"),
    ("en-whats-next", "what's next?", "planning"),
    ("en-continue", "continue where we left off", "planning"),
    ("en-resume", "resume the migration task", "planning"),
    # genuine past-recall -> FULL ladder
    ("vn-da-chua", "đã deploy chưa", "recall"),
    ("vn-hoi-do", "hồi đó mình fix lỗi này thế nào", "recall"),
    ("vn-luu-o-dau", "file config lưu ở đâu", "recall"),
    ("en-where-is", "where is the settings file", "recall"),
    ("en-did-we", "did we already solve this", "recall"),
    ("en-last-time", "last time we used which approach", "recall"),
    ("en-remember", "do you remember the port we used", "recall"),
    # normal prompts -> no reminder
    ("vn-viet-ham", "viết cho tôi một hàm sort mảng", None),
    ("vn-fix-bug", "fix cái bug ở dòng 42", None),
    ("en-add-button", "add a button to the login page", None),
    # precedence: PLANNING wins when both signals present
    ("mix-planning-wins", "tiếp theo, hồi đó mình đã làm gì", "planning"),
]

_ok = True
for cid, prompt, expected in CASES:
    got = classify(prompt)
    good = got == expected
    _ok = _ok and good
    print(("PASS" if good else "FAIL") + f" - [{expected}] {cid}"
          + ("" if good else f"  (got {got})"))

print()
print("RESULT: " + ("ALL PASS" if _ok else "SOME FAIL"))
sys.exit(0 if _ok else 1)
