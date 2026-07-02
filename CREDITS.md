# Credits & Attribution

This kit is mostly **behavioral configuration** — a rule contract, a hook, a slash command, and
docs. It stands on the shoulders of other people's work. This file states plainly **what came
from where**, so nothing here is mistaken for ours that isn't.

---

## What this kit authored

Written for this kit (by Galahad), MIT-licensed:

- `CLAUDE.md` — the 12-rule contract structure + Rule 0 Memory-First (the *wording and ordering*;
  the source ideas behind the rules are credited below).
- `.claude/hooks/memory_first.py` — the recall-detection hook.
- `.claude/commands/wrap.md` — the `/wrap` command.
- `.claude/LESSONS.md` — the Tier-1 store format.
- `docs/`, `templates/`, `install.sh`, `README.md`.

---

## External tools — referenced, NOT bundled

This kit **does not contain a single line of these projects' code.** It only references them and
tells you how to install them yourself. They are optional; the kit runs standalone without them.

| Tool | Author | Repo | License | Role here |
|------|--------|------|---------|-----------|
| **claude-mem** | thedotmack | https://github.com/thedotmack/claude-mem | MIT (see upstream) | Tier-2 memory: auto-captures sessions, compresses with AI, injects context back. The kit's Rule 0 reads it via `mcp__plugin_claude-mem_mcp-search__*` tools |
| **codebase-memory** | DeusData | https://github.com/DeusData/codebase-memory-mcp | see upstream | Tier-3 memory: indexes the repo into a code knowledge graph. The kit's Rule 0 reads it via `mcp__codebase-memory__search_graph / query_graph / trace_call_path` |

> Always check each upstream repo for its current license and terms before redistributing.
> If you fork or vendor either tool, you must comply with **their** license, not this kit's.

---

## Idea sources behind the rules

The behavioral rules in `CLAUDE.md` are not invented from scratch — they distill prior work:

| Rules | Source | Link |
|-------|--------|------|
| Rules 1–4 (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven) | Derived from **Andrej Karpathy**'s observations, via forrestchang's skill pack | https://github.com/forrestchang/andrej-karpathy-skills |
| Rules 5–12 (orchestration / token-budget / fail-loud rules) | **@Mnilax** — extended for orchestration, May 2026 | (community, credited inline in `CLAUDE.md`) |
| Rule 2 additions: lazy evaluation ladder + safety floor (Jul 2026) | **DietrichGebert's ponytail** — minimalist code-gen skill, MIT. We adopted the 7-rung ladder and the "never cut validation/security" floor as rule text only; no ponytail code is bundled | https://github.com/DietrichGebert/ponytail |

These attributions are also kept inline at the bottom of `CLAUDE.md` so they travel with the file.

---

## If you redistribute

- Keep this `CREDITS.md` and the inline source notes in `CLAUDE.md` intact.
- Don't strip the upstream links for claude-mem / codebase-memory.
- The MIT license here covers only the kit-authored files listed above.
