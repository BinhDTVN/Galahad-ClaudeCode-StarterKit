# Implementation Notes

> Why the code is shaped the way it is. One entry per non-obvious decision: what was chosen,
> what was rejected, and **why**. The reader is a future maintainer asking "why not the obvious
> way?" Append-only — newest at the bottom (or top, pick one and keep it).

Format:

```
## YYYY-MM-DD — <short title of the decision>
**Context:** what problem / constraint forced a choice.
**Decision:** what we did.
**Rejected:** the obvious alternative, and why not.
**Tradeoff:** what we gave up.
```

---

## 2026-06-28 — Tier-1 lessons live in a file, not in claude-mem

**Context:** needed a place `/wrap` can write lessons to that survives `/clear` and is read back
on recall.
**Decision:** write to `.claude/LESSONS.md` (a plain file in the repo).
**Rejected:** writing into claude-mem — in worker mode `observation_add` requires `server-beta`
and fails, so there is no reliable runtime write path.
**Tradeoff:** lessons aren't semantically indexed like claude-mem captures; mitigated by keeping
each lesson to one tagged, greppable line.
