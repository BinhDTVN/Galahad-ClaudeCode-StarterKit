# Galahad Claude Code Kit

**A drop-in discipline layer for Claude Code: a 12-rule behavioral contract + a memory-first
workflow that closes the loop between what you save and what the agent reads back.**

The problem this solves: every `/clear` wipes the agent's working memory, so it re-greps the
filesystem, re-makes solved mistakes, and quietly degrades. This kit gives Claude Code a cheap,
durable place to write lessons — and a contract that makes it *read them first*.

> **Attribution-first.** This kit is mostly behavioral config (rules, a hook, a command, docs).
> It **depends on** two excellent third-party memory tools but **does not bundle their code** —
> it only references and configures them. Full credit in **[CREDITS.md](CREDITS.md)**.

---

## What this is — and what it isn't

**This is not a memory engine.** It does not store, embed, or retrieve anything itself. It is the
**discipline layer that sits on top** of a memory engine — it decides *what is worth saving* and
makes sure *what you saved actually gets read back*.

| | A memory engine (e.g. [cognee](https://github.com/topoteretes/cognee), [claude-mem](https://github.com/thedotmack/claude-mem)) | This kit |
|---|---|---|
| Role | The warehouse — storage + retrieval (graph, vectors, semantic search) | The operating procedure for the warehouse |
| Analogy | A database | A team's commit-message convention + code-review checklist |
| Ships | Indexing/search technology | Rules, a hook, a `/wrap` command, a curated lesson file |

**Where it sits:** the engine stores everything; this kit keeps a small, hand-curated set of
lessons and enforces one contract — *read memory before you grep the filesystem*. Most memory
setups fail not at storage but at this human-discipline seam: they capture into a store the agent
never opens, or ask it to read a store nothing reliably writes to. This kit closes that loop.

**Best for:** anyone using Claude Code who hasn't tuned it yet — a 5-minute, copy-paste starting
point that pays off immediately. If you've already built your own CLAUDE.md + memory workflow,
you probably don't need this. That's fine — it's a starter kit, not a framework.

---

## What you get (and who made it)

| Piece | What it does | Authored by |
|-------|--------------|-------------|
| `CLAUDE.md` | 12-rule behavioral contract + **Rule 0 Memory-First** | **This kit** (Galahad). Rules 1–4 derived from Karpathy, 5–12 from @Mnilax — see CREDITS |
| `.claude/hooks/memory_first.py` | `UserPromptSubmit` hook: detects "recall" phrasing (VN+EN), nudges the agent to query memory before grepping | **This kit** (Galahad) |
| `.claude/commands/wrap.md` | `/wrap` — end-of-task: distill lessons → route into the 3-tier store | **This kit** (Galahad) |
| `.claude/LESSONS.md` | Tier-1 lesson store: writable, survives `/clear`, read first on recall | **This kit** (Galahad) |
| `docs/`, `templates/`, `install.sh` | Setup, memory model, doc-discipline, copy-paste starters | **This kit** (Galahad) |
| **claude-mem** *(optional, external)* | Auto-captures sessions, compresses them, injects context back | **thedotmack** — [github.com/thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) |
| **codebase-memory** *(optional, external)* | Indexes the repo into a queryable code knowledge graph | **DeusData** — [github.com/DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) |

The kit works **standalone** with just Tier-1 (LESSONS.md). The two external tools add Tier-2
and Tier-3 memory — install them only if you want the full stack.

---

## The 3-tier memory model

```
                       ┌─────────────────────────────────────────────┐
   /wrap  ──writes──▶  │  TIER 1  .claude/LESSONS.md                  │
   (you)               │  hand-curated, writable, survives /clear     │ ◀──┐
                       └─────────────────────────────────────────────┘    │
                       ┌─────────────────────────────────────────────┐    │ Rule 0 +
   sessions ─auto──▶   │  TIER 2  claude-mem (read-only in worker)    │ ───┤ memory_first.py
                       │  auto-capture, semantic + FTS search         │    │ read these
                       └─────────────────────────────────────────────┘    │ BEFORE grep
                       ┌─────────────────────────────────────────────┐    │
   indexer ─builds─▶   │  TIER 3  codebase-memory (code graph)        │ ───┘
                       │  functions / call-paths / routes             │
                       └─────────────────────────────────────────────┘
```

**The loop that makes it work:** `/wrap` *writes* to exactly the store that Rule 0 + the hook
*read* first. Save closes back into recall. Details in
**[docs/MEMORY_ARCHITECTURE.md](docs/MEMORY_ARCHITECTURE.md)**.

---

## How it works in a session

```
SESSION START
   └─ CLAUDE.md (12 rules + Rule 0) loads as project instructions
   └─ (if installed) claude-mem injects relevant context from past sessions

YOU ASK SOMETHING
   └─ recall phrasing? ("did we… last time?", "where is…", "hồi đó…")
        └─ memory_first.py hook fires → injects "check memory before grep"

AGENT RESOLVES IT  (Rule 0 order — cheap → expensive)
   1. read .claude/LESSONS.md        ← curated lessons, tiny, first
   2. search claude-mem               ← past-session recall
   3. query codebase-memory graph     ← code structure in ~1 call, not 10 file reads
   4. only now: Glob/Grep the files   ← last resort

YOU FINISH THE TASK
   └─ run /wrap
        ├─ Tier-1 lesson  → written straight into LESSONS.md
        └─ Tier-2/3 (CLAUDE.md / BUILD_STATUS.md) → proposed as a diff for your OK

/clear  →  next session
   └─ LESSONS.md persists, so step 1 reads back exactly what /wrap wrote.
      The loop is closed: what you saved is what the agent reads first.
```

The payoff is two-fold: **fewer tokens** (one graph query instead of reading many files; one
curated lesson file instead of re-exploring) and **fewer repeated mistakes** (a lesson the agent
already learned stops it from walking the same dead end twice). The savings are largest on big
codebases and recall-heavy work — most of the raw token win comes from the external engines
(especially codebase-memory), while this kit is what makes them get *used* at the right moment.

---

## Quick start

```bash
# One command. Copies CLAUDE.md + .claude/, wires the hook, then OFFERS to install
# claude-mem for you (runs the official `npx claude-mem install` — nothing is bundled).
bash install.sh /path/to/your-project
```

Tier-3 (codebase-memory) is a Go binary, so you install it from upstream and register it as an
MCP server named `codebase-memory` — the installer prints the exact steps and link. The kit also
works **standalone** with just Tier-1, if you skip both.

> **Why these two aren't bundled:** they install from their own source (claude-mem builds a local
> vector DB per machine; codebase-memory is a platform-specific binary), they update often, and
> vendoring them would blur whose work is whose. The installer fetches them for you instead —
> same "download-and-go" result, full credit intact. See [CREDITS.md](CREDITS.md).

Then, in Claude Code:
- Ask a recall question ("did we fix X last time?") → the hook nudges memory-first.
- Finish a task → run **`/wrap`** → lessons land in `LESSONS.md` for next session.

Full walkthrough + per-piece verification: **[docs/SETUP.md](docs/SETUP.md)**.

---

## Documentation

| Doc | Read it when |
|-----|--------------|
| [docs/SETUP.md](docs/SETUP.md) | Installing — step by step, including the two external tools |
| [docs/MEMORY_ARCHITECTURE.md](docs/MEMORY_ARCHITECTURE.md) | You want to understand the 3-tier model and the read/write loop |
| [docs/DOC_DISCIPLINE.md](docs/DOC_DISCIPLINE.md) | You want the rule for which living doc to write into (CLAUDE.md / IMPLEMENTATION_NOTES / BUILD_STATUS / LESSONS) |
| [CREDITS.md](CREDITS.md) | Always — who made what, and what this kit does *not* claim |

---

## License

MIT, covering **only the files authored in this kit** (see the "Authored by: This kit" rows
above). The external tools keep their own licenses — see [CREDITS.md](CREDITS.md). Full text in
[LICENSE](LICENSE).
