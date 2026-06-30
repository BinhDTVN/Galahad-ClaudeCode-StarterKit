# Setup

Three layers, installed independently. The kit works with just **Layer 1**; Layers 2 and 3 are
optional external tools that deepen the memory stack.

| Layer | What | Required? |
|-------|------|-----------|
| 1 | The kit itself — `CLAUDE.md`, the hook, `/wrap`, `LESSONS.md` | **Yes** |
| 2 | claude-mem (auto-capture memory) | Optional |
| 3 | codebase-memory (code knowledge graph) | Optional |

---

## Layer 1 — Install the kit

### Option A — the install script (recommended)

```bash
bash install.sh /path/to/your-project
```

It copies `CLAUDE.md` and `.claude/` into the target, and wires the hook into
`.claude/settings.json`. It is idempotent and will not clobber an existing unrelated hook —
it warns instead. Run with no argument to install into the current directory.

### Option B — manual

1. Copy `CLAUDE.md` to your project root.
2. Copy the `.claude/` folder (`commands/`, `hooks/`, `LESSONS.md`) to your project root.
3. Merge `templates/settings.json` into `.claude/settings.json` (create it if absent).

### Verify Layer 1

```bash
# Hook fires on recall phrasing, stays silent otherwise:
echo '{"prompt":"did we fix the encoding bug last time?"}' | python3 .claude/hooks/memory_first.py
#   → prints JSON containing "additionalContext" with the memory-first reminder

echo '{"prompt":"add a button"}' | python3 .claude/hooks/memory_first.py
#   → prints nothing, exits 0
```

In Claude Code: `/wrap` should appear in the slash-command list, and `CLAUDE.md` should be
picked up automatically as project instructions.

---

## Layer 2 — claude-mem (optional)

Auto-captures sessions and lets the agent search past context. Authored by **thedotmack** —
**https://github.com/thedotmack/claude-mem** (this kit does not bundle it).

```bash
npx claude-mem install
```

Follow the upstream README for the current install flow and modes. Once installed, Rule 0 in
`CLAUDE.md` will use its search tools (`mcp__plugin_claude-mem_mcp-search__search`,
`...get_observations`).

> **Worker vs server-beta:** in worker mode, claude-mem is **read-only** — `observation_add` /
> `memory_add` only work under server-beta and fail in worker mode. That is *why* this kit keeps
> a writable Tier-1 store (`LESSONS.md`) of its own. See `docs/MEMORY_ARCHITECTURE.md`.

### Verify Layer 2
Ask a recall question in Claude Code and confirm the agent can call the claude-mem search tools
and return past observations.

---

## Layer 3 — codebase-memory (optional)

Indexes your repo into a code knowledge graph for precise, low-token structural queries.
Authored by **DeusData** — **https://github.com/DeusData/codebase-memory-mcp** (not bundled).

1. Install / build per the upstream README.
2. Register it as an MCP server. The kit's Rule 0 assumes the server is named
   **`codebase-memory`**, so it references `mcp__codebase-memory__search_graph`,
   `mcp__codebase-memory__query_graph`, `mcp__codebase-memory__trace_call_path`.
3. If you register it under a different name, update that prefix in `CLAUDE.md` (Rule 0, item 3)
   and in `.claude/hooks/memory_first.py` (the `REMINDER` string).

### Verify Layer 3
In Claude Code, ask an architecture question and confirm the agent can call
`query_graph` / `search_graph` against the index.

---

## Wiring reference — `.claude/settings.json`

The hook is registered as a `UserPromptSubmit` hook. Minimal wiring (also in
`templates/settings.json`):

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          { "type": "command", "command": "python3 .claude/hooks/memory_first.py" }
        ]
      }
    ]
  }
}
```

On Windows, use `python` instead of `python3` if that is your interpreter name. The hook reads
and writes UTF-8 explicitly, so it is safe under non-UTF-8 locales (e.g. Windows cp1252).
