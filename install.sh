#!/usr/bin/env bash
# install.sh — drop the Galahad Claude Code Kit into a project.
# Copies CLAUDE.md + .claude/ and wires the memory-first hook into .claude/settings.json.
# Idempotent. Does NOT install third-party tools — it only prints how.
set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$(pwd)}"

if [ ! -d "$TARGET" ]; then
  echo "ERROR: target directory does not exist: $TARGET" >&2
  exit 1
fi
TARGET="$(cd "$TARGET" && pwd)"

if [ "$TARGET" = "$KIT_DIR" ]; then
  echo "ERROR: target is the kit itself. Pass your project dir: bash install.sh /path/to/project" >&2
  exit 1
fi

PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo "ERROR: python3 (or python) is required to wire the hook." >&2
  exit 1
fi

echo "Kit:    $KIT_DIR"
echo "Target: $TARGET"
echo

# 1. CLAUDE.md — copy, warn (do not clobber) if one already exists.
if [ -e "$TARGET/CLAUDE.md" ]; then
  echo "• CLAUDE.md already exists in target — leaving it untouched."
  echo "  Review $KIT_DIR/CLAUDE.md and merge by hand if you want the 12 rules."
else
  cp "$KIT_DIR/CLAUDE.md" "$TARGET/CLAUDE.md"
  echo "• Copied CLAUDE.md"
fi

# 2. .claude/ — commands + hooks always refreshed; LESSONS.md preserved if present.
mkdir -p "$TARGET/.claude/commands" "$TARGET/.claude/hooks"
cp "$KIT_DIR/.claude/commands/wrap.md"      "$TARGET/.claude/commands/wrap.md"
cp "$KIT_DIR/.claude/hooks/memory_first.py" "$TARGET/.claude/hooks/memory_first.py"
echo "• Installed /wrap command and memory_first.py hook"

if [ -e "$TARGET/.claude/LESSONS.md" ]; then
  echo "• .claude/LESSONS.md already exists — preserved (your lessons are safe)."
else
  cp "$KIT_DIR/.claude/LESSONS.md" "$TARGET/.claude/LESSONS.md"
  echo "• Seeded .claude/LESSONS.md"
fi

# 3. Wire the hook into .claude/settings.json (merge, don't clobber).
SETTINGS="$TARGET/.claude/settings.json"
"$PY" - "$SETTINGS" <<'PYEOF'
import json, os, sys
path = sys.argv[1]
HOOK_CMD = "python3 .claude/hooks/memory_first.py"

data = {}
if os.path.exists(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f) or {}
    except Exception as e:
        print(f"  ! Could not parse existing settings.json ({e}); not modifying it.")
        sys.exit(0)

hooks = data.setdefault("hooks", {})
ups = hooks.setdefault("UserPromptSubmit", [])

def already_wired(blocks):
    for b in blocks:
        for h in b.get("hooks", []):
            if "memory_first.py" in (h.get("command") or ""):
                return True
    return False

if already_wired(ups):
    print("  • Hook already wired in settings.json — nothing to do.")
else:
    if ups:
        print("  ! Existing UserPromptSubmit hook(s) found — appending ours alongside them.")
    ups.append({"hooks": [{"type": "command", "command": HOOK_CMD}]})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("  • Wired memory_first.py into UserPromptSubmit")
PYEOF

echo
echo "Layer 1 installed."
echo
echo "Optional external memory tools — NOT bundled with this kit (see CREDITS.md)."
echo "They are installed FROM THEIR OWN SOURCE, not redistributed here."
echo

# Tier-2: claude-mem. Offer to run the official installer (only in an interactive shell).
if [ -t 0 ] && [ "${WITH_MEMORY:-ask}" != "no" ]; then
  if command -v npx >/dev/null 2>&1; then
    printf "• Install claude-mem now via the official installer (npx claude-mem install)? [y/N] "
    read -r ans
    case "$ans" in
      [yY]*) npx claude-mem install || echo "  ! claude-mem install failed — run it yourself later." ;;
      *)     echo "  Skipped. Run later: npx claude-mem install" ;;
    esac
  else
    echo "• Tier-2 claude-mem: needs Node.js (npx). Install Node, then: npx claude-mem install"
  fi
else
  echo "• Tier-2 claude-mem  →  npx claude-mem install   (github.com/thedotmack/claude-mem)"
fi

echo
echo "• Tier-3 codebase-memory (Go binary, platform-specific — install from upstream):"
echo "    github.com/DeusData/codebase-memory-mcp"
echo "    Build/download per its README, then register it as an MCP server named"
echo "    'codebase-memory' (or edit that prefix in CLAUDE.md + the hook)."
echo
echo "Verify the hook:"
echo "  echo '{\"prompt\":\"did we fix this last time?\"}' | $PY $TARGET/.claude/hooks/memory_first.py"
