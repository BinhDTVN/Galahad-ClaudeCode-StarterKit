# CLAUDE.md — 12-Rule Behavioral Contract

Behavioral guidelines to reduce common LLM coding mistakes.
**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

> **Sub-project protocol:** When working inside a sub-project that has its own `CLAUDE.md`, load that file too — it carries project-specific session-start, ownership, and tracking-file rules. This file (root) governs behavior everywhere; the sub-project file refines it locally.

---

## RULE 0 — MEMORY-FIRST (read before searching)

**The cheapest search is the one you already did. Check memory before the filesystem.**

When a request is a *recall* — asking about work done in a past session ("đã…chưa", "hồi đó", "lần trước", "ở đâu", "how did we", "where is", "did we", "last time") — query persistent memory **before** Glob/Grep, in this order:

1. **`Read .claude/LESSONS.md`** — the Tier-1 lesson store (always present, cheap, hand-curated). This is where `/wrap` writes, so it's the highest-signal place to look first.
2. **claude-mem** (runs in *worker* mode here): `ToolSearch "select:mcp__plugin_claude-mem_mcp-search__search,mcp__plugin_claude-mem_mcp-search__get_observations"`, then `search()` by keyword and `get_observations([ID])` to expand. ⚠️ `observation_add` / `observation_search` / `memory_add` require `server-beta` and **fail in worker mode** — do not call them.
3. For code/architecture recall: `ToolSearch "select:mcp__codebase-memory__search_graph,mcp__codebase-memory__query_graph,mcp__codebase-memory__trace_call_path"` → search **codebase-memory** (the code knowledge graph). ⚠️ The `mcp__codebase-memory__` prefix is the name you registered the MCP server under — adjust it if you named the server differently.
4. Only fall back to filesystem search when memory can't answer. If memory is empty, **say so** — don't fabricate (Rule 12).

A keyword-gated `UserPromptSubmit` hook (`.claude/hooks/memory_first.py`) auto-injects this reminder when it detects recall phrasing. The hook is a nudge; this rule is the contract. **`.claude/LESSONS.md` is where `/wrap` writes** — so what you save closes back into what you read here.

---

## THE 12-RULE STACK

### KARPATHY RULES (1–4)

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

**The lazy evaluation ladder** — before writing new code, stop at the first rung that fits:
1. Doesn't need to exist? → skip it (YAGNI)
2. Already in this codebase? → reuse it
3. Stdlib does it? → stdlib
4. Native platform feature? → use it
5. Already-installed dependency covers it? → use that
6. One line enough? → one line
7. Only then: minimum viable implementation

**The floor:** never simplify away input validation, error handling, security, or accessibility. Code is small because it's *unnecessary*, not because it's compressed.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

### EXTENDED RULES (5–12) — Added May 2026, source: @Mnilax

## 5. Use Model Only for Judgment Calls

**The LLM decides. Code handles everything else.**

- Model's job: reasoning, judgment, ambiguity resolution, intent classification.
- Code's job: retry logic, routing, data transformation, state management.
- Don't ask the model to do what deterministic code can do reliably.
- Token budget must be explicit — set it in code, not as a hope.

## 6. Token Budgets Are Not Advisory

**A token limit is a hard constraint, not a suggestion.**

- If a task needs more tokens than the budget allows, surface that conflict — don't silently truncate or degrade output quality.
- Design prompts and context windows to fit the budget before running, not after.
- When context is too large: summarize, chunk, or escalate — never silently drop information.

## 7. Surface Conflicts, Don't Average Them

**When two requirements conflict, say so. Don't produce a blended compromise that satisfies neither.**

- If instructions contradict each other, stop and name the conflict explicitly.
- If spec A says X and spec B says Y, don't output something between X and Y — ask which takes priority.
- Averaging conflicts produces outputs nobody wanted and errors nobody can trace.

## 8. Read Before You Write

**Understand the existing code before changing it.**

- Before editing any file, read the relevant section and understand the current pattern.
- Don't infer structure from filenames or function names alone — read the implementation.
- If you can't read the full file, read the parts your change will touch plus their immediate dependencies.
- "I assumed it worked like X" is not acceptable after the fact.

## 9. Tests Verify Intent, Not Behavior

**Write tests that fail when the intent is violated, not just when output changes.**

- A test that checks "output == X" breaks on every refactor. A test that checks "system rejects invalid input" survives them.
- Tests encode what the code is supposed to do, not what it currently does.
- If you can't write a test that would catch the bug you're fixing, the test is wrong.

## 10. Checkpoint After Every Step

**Don't chain multiple irreversible actions without verifying each one worked.**

- After each significant action, verify the result before proceeding.
- Especially for: file writes, API calls, database changes, deploys.
- If step 2 depends on step 1 succeeding, check step 1 before running step 2.
- A chain of unverified steps is a chain of compounding errors.

## 11. Match Conventions, Even If You Disagree

**Consistency beats local optimization.**

- If the codebase uses pattern X and you'd prefer pattern Y, use X.
- If naming is inconsistent but a dominant style exists, follow the dominant style.
- If you think the convention is wrong, note it — don't silently fix it.
- A codebase that's consistently "wrong" is easier to maintain than one that's inconsistently "right."

## 12. Fail Loud

**Silent failures are the worst failures.**

- When something goes wrong, say so explicitly — don't return a degraded result as if it were a success.
- Log errors with enough context to reproduce them, not just "error occurred."
- If you can't complete a task safely, stop and surface the reason — don't produce something plausible-looking that's actually wrong.
- "It seemed to work" is not an acceptable completion state.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, conflicts surfaced before implementation rather than discovered after, and failures are loud and traceable.

---

Sources:
- Rules 1–4: https://github.com/forrestchang/andrej-karpathy-skills (derived from Andrej Karpathy's observations)
- Rules 5–12: @Mnilax — Extended for orchestration, May 2026
- Rule 2 ladder + floor: https://github.com/DietrichGebert/ponytail (MIT) — measured on real tickets: −54% LOC, −22% tokens, −20% cost vs baseline, safety maintained. Added Jul 2026.
