# -*- coding: utf-8 -*-
"""SessionStart hook template: cheap, idempotent, source-aware.

Three habits, one per section below:
  1. Branch on `source` (startup | resume | clear | compact). A resumed session
     still has its old context, so re-injecting the same notes is pure noise.
  2. Skip expensive work whose inputs have not changed: hash the input files,
     keep the hash under .claude/.cache/, rerun only on a mismatch.
  3. Print little: a short, capped additionalContext with only what helps now.

Fail-safe: any error -> exit 0 with no output. A broken hook must never block
a session. Stdlib only. Explicit UTF-8 I/O (Windows cp1252 corrupts non-ASCII).

Wire it in .claude/settings.json (see docs/HOOKS.md):
  "SessionStart": [{"hooks": [{"type": "command",
                               "command": "python3 .claude/hooks/session_start.py"}]}]
Add .claude/.cache/ to .gitignore.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
STATUS_DOC = PROJECT / "docs" / "BUILD_STATUS.md"
CACHE_DIR = PROJECT / ".claude" / ".cache"
HASH_FILE = CACHE_DIR / "session_start.sha256"
# Files that decide what the expensive step produces. Edit for your project.
WATCHED = [PROJECT / "requirements.txt", PROJECT / "package-lock.json"]
MAX_LINES = 15


def todo_excerpt() -> str:
    """The 'TODO next' section of BUILD_STATUS.md, capped at MAX_LINES."""
    if not STATUS_DOC.is_file():
        return ""
    out, inside = [], False
    for line in STATUS_DOC.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#"):
            if inside:
                break
            inside = "todo" in line.lower()
            continue
        if inside and line.strip():
            out.append(line)
    return "\n".join(out[:MAX_LINES])


def inputs_hash() -> str:
    h = hashlib.sha256()
    for path in WATCHED:
        h.update(str(path.name).encode("utf-8"))
        h.update(path.read_bytes() if path.is_file() else b"<missing>")
    return h.hexdigest()


def expensive_refresh() -> None:
    """Placeholder for slow work: install deps, rebuild an index, warm a cache.

    Must raise on failure, so the hash is NOT saved and the next session retries.
    """


def refresh_if_inputs_changed() -> bool:
    current = inputs_hash()
    if HASH_FILE.is_file() and HASH_FILE.read_text(encoding="utf-8").strip() == current:
        return False
    HASH_FILE.unlink(missing_ok=True)  # a failed refresh must rerun next time
    expensive_refresh()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    HASH_FILE.write_text(current, encoding="utf-8")
    return True


def main() -> None:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", "replace")
        source = (json.loads(raw) if raw.strip() else {}).get("source", "startup")
    except Exception:
        sys.exit(0)

    notes = []
    try:
        # 1. Branch on source: resume keeps its context, nothing to add.
        if source == "resume":
            sys.exit(0)
        # 2. Expensive work only on a real start, and only when inputs changed.
        if source == "startup" and refresh_if_inputs_changed():
            notes.append("Project inputs changed since last session; refresh ran.")
        # 3. Cheap, capped pointer to where the work stopped.
        todo = todo_excerpt()
        if todo:
            notes.append("TODO next (from docs/BUILD_STATUS.md):\n" + todo)
    except Exception:
        sys.exit(0)

    if not notes:
        sys.exit(0)
    output = {"hookSpecificOutput": {"hookEventName": "SessionStart",
                                     "additionalContext": "\n\n".join(notes)}}
    sys.stdout.buffer.write(json.dumps(output, ensure_ascii=False).encode("utf-8"))
    sys.exit(0)


if __name__ == "__main__":
    main()
