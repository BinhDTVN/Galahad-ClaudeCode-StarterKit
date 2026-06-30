# Doc Discipline — which living doc gets what

Four documents form the project's memory on disk. Confusion about *which one to write into* is
what makes them rot. The rule is simple: **each doc answers one question, at one cadence.**

| Doc | Question it answers | When you write to it | Lifetime |
|-----|---------------------|----------------------|----------|
| `CLAUDE.md` | "What rules govern how the agent works here?" | A lesson recurs (≥2×) or is universal | Permanent contract |
| `docs/IMPLEMENTATION_NOTES.md` | "Why is the code like *this* and not the obvious way?" | After any non-obvious implementation decision | Append-only log |
| `docs/BUILD_STATUS.md` | "What's done, what's next, what's verified?" | End of each session | Rolling snapshot |
| `.claude/LESSONS.md` | "What did we learn, once?" | Whenever you learn something checkable | Append-only, Tier-1 store |

---

## The decision: where does *this* note go?

```
 Did you just learn / decide something worth keeping?
        │
        ├─ It's a RULE for how to work, and it's recurred ≥2× or is universal
        │        → CLAUDE.md   (a new numbered rule, or the ## LESSONS section)
        │
        ├─ It's WHY the code is shaped this way (a tradeoff, a deviation from spec)
        │        → docs/IMPLEMENTATION_NOTES.md
        │
        ├─ It's the STATE of the task (done / TODO next / test results)
        │        → docs/BUILD_STATUS.md
        │
        └─ It's a one-off LESSON (a root cause, a correction, a gotcha)
                 → .claude/LESSONS.md      ← default lands here
```

**Default to `LESSONS.md`.** Promote to `CLAUDE.md` only after a lesson has earned it by
recurring. This keeps the contract small and high-signal — a 400-line `CLAUDE.md` of one-off
notes is one nobody reads.

---

## Format rules

### `.claude/LESSONS.md`
One line per lesson, imperative, **checkable**:
```
- [YYYY-MM-DD][tag][tag] <one rule, stated so you could verify a violation>
```
- Good: *"Python hooks on Windows must read/write stdin/stdout as UTF-8 buffers — cp1252 locale
  corrupts non-ASCII."*
- Bad: *"Be careful with encoding."* (not checkable, not actionable — drop it.)

Tags let Rule 0 grep precisely. Append only; never rewrite old lines.

### `docs/IMPLEMENTATION_NOTES.md`
One entry per decision: what you chose, what you rejected, and **why**. The reader is a future
maintainer asking "why didn't they just do the obvious thing?" See `templates/IMPLEMENTATION_NOTES.md`.

### `docs/BUILD_STATUS.md`
Refreshed at session end: **Done**, **TODO next session**, **E2E / test results**. This is the
file you read *first* next session to know where you stopped. See `templates/BUILD_STATUS.md`.

### `CLAUDE.md`
A numbered behavioral rule, or an entry under a `## LESSONS` section. Keep it terse. Every rule
should change behavior — if it doesn't, it's documentation, not a rule.

---

## How `/wrap` automates this

The `/wrap` command runs this ladder for you at end-of-task:

1. Scan the session for real lessons (root cause / user correction / repeated pattern only).
2. Distill each into exactly one checkable rule.
3. Route by tier: **Tier-1 → written straight into `LESSONS.md`**; Tier-2 (`CLAUDE.md`) and
   Tier-3 (`BUILD_STATUS.md`) are **proposed as diffs for your approval**, never auto-edited.
4. Summarize what landed where.

The asymmetry is deliberate: the cheap, low-risk store (`LESSONS.md`) is written automatically;
the permanent contract and the shared status file are only touched with your sign-off.
