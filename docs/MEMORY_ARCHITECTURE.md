# Memory Architecture

The core idea: **the cheapest search is the one you already did.** An agent that re-greps the
filesystem every session keeps paying to rediscover what it already learned. This kit gives
Claude Code a layered memory and — crucially — a contract (**Rule 0**) that makes it *read that
memory before searching*.

---

## The three tiers

| Tier | Store | Written by | Read by | Survives `/clear`? | Writable at runtime? |
|------|-------|-----------|---------|--------------------|----------------------|
| 1 | `.claude/LESSONS.md` | `/wrap` (and you, by hand) | Rule 0, every recall | Yes | **Yes** — plain file |
| 2 | claude-mem | auto-capture hooks | Rule 0 search tools | Yes | Read-only in worker mode |
| 3 | codebase-memory | the indexer | Rule 0 graph tools | Yes (re-indexed) | Read-only (derived from code) |

Each tier answers a different question:

- **Tier 1 — "what did we *decide / learn*?"** Hand-curated, one line per lesson, highest signal,
  zero noise. This is the first place Rule 0 looks.
- **Tier 2 — "what *happened* in past sessions?"** Auto-captured narrative, searchable. Broad
  recall, lower signal-to-noise than Tier 1.
- **Tier 3 — "how is the *code* shaped?"** Functions, call-paths, routes. For structural and
  architecture questions, not for decisions or lessons.

---

## The loop: save closes into recall

```
   ┌──────────────────────── you finish a task ────────────────────────┐
   │                                                                    │
   ▼                                                                    │
  /wrap  ── distills lessons ──▶  TIER 1  .claude/LESSONS.md            │
                                          │                             │
                                          │ (Rule 0 reads this FIRST)   │
                                          ▼                             │
   next session, you ask a recall question ──▶ memory_first.py hook     │
       fires on recall phrasing, injects "check memory before grep"     │
                                          │                             │
                                          ▼                             │
   agent reads LESSONS.md → claude-mem → codebase-memory → (only        │
   then) filesystem ───────────────────────────────────────────────────┘
```

`/wrap` writes to **exactly** the store Rule 0 reads first. That is the whole trick: there is no
gap between "where lessons go" and "where the agent looks". Most memory setups break here — they
capture into a store the agent never consults, or consult a store nothing writes to.

---

## Why a separate Tier-1 file, when claude-mem exists?

Because in **worker mode**, claude-mem cannot be written to on demand — `observation_add` /
`observation_search` / `memory_add` require `server-beta` and fail in worker mode. Its
auto-capture still works (and Rule 0 reads it via `search` / `get_observations`), but there is no
reliable *manual write* tool.

So the kit keeps `LESSONS.md`: a writable store that survives `/clear`, costs nothing to read,
and carries no auto-capture noise. `/wrap` writes here deterministically. claude-mem's
auto-capture *complements* it; it does not replace it.

---

## Rule 0 read order (from `CLAUDE.md`)

On a recall request, the agent queries memory **before** Glob/Grep, in this order:

1. **`.claude/LESSONS.md`** — always present, cheapest, hand-curated.
2. **claude-mem** — `search()` by keyword, `get_observations([ID])` to expand.
3. **codebase-memory** — for code/architecture questions: `search_graph` / `query_graph` /
   `trace_call_path`.
4. **Filesystem** — only when memory can't answer. If memory is empty, **say so** — don't
   fabricate (Rule 12, fail-loud).

The `memory_first.py` hook is a *nudge* that fires on recall phrasing (Vietnamese + English).
Rule 0 is the *contract*. The hook makes the contract hard to forget.

### Two-tier nudge — cheap lookup before the deep dig

The same answer-ladder principle CaelionAI uses for document Q&A (a cheap lookup
before a deep LLM call) applies to Claude Code's own memory: **not every "recall"
prompt deserves the full 6–8-round memory dig.** The hook classifies the prompt
(deterministic — `classify()` in code, not the model) into one of two lanes:

| Lane | Triggers on | Nudge |
|------|-------------|-------|
| **PLANNING** (light) | "what next / plan / continue / resume / tiếp theo / tiếp tục / bước kế" | Read `LESSONS.md` + the status docs (`BUILD_STATUS.md` / `IMPLEMENTATION_NOTES.md`), **1–2 tool calls**; escalate only if those don't answer. |
| **RECALL** (full) | genuine past-work recall — "đã…chưa / how did we / where is / last time" | Full ladder: `LESSONS.md` → claude-mem → codebase-memory → filesystem. |

PLANNING wins when both signals appear (a continuation is planning, not a dig).
This exists because a one-line *"what's next?"* used to fire the full ladder —
cache-cold base context + adaptive deep-thinking + 6–8 memory rounds ≈ **~10% of a
turn's limit for a one-line question.** The light lane points straight at the
cheap curated sources instead. Verify with `.claude/hooks/test_memory_first.py`.

---

## Escalation: where lessons graduate to

`/wrap` doesn't dump everything into `LESSONS.md` forever. It uses a ladder (see
`docs/DOC_DISCIPLINE.md`):

| Tier | Lesson type | Goes to |
|------|-------------|---------|
| 1 | One-off lesson / decision | `.claude/LESSONS.md` (append, tagged) |
| 2 | Repeated ≥2× or universal | `CLAUDE.md` (a new rule) |
| 3 | Task done/TODO state | `docs/BUILD_STATUS.md` |

Default everything to Tier 1. Promote to Tier 2 only when a lesson has recurred or is clearly
universal — don't bloat `CLAUDE.md` with one-off notes.
