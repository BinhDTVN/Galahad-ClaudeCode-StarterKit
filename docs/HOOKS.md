# Hooks: keep them cheap, idempotent and quiet

Hooks are the only part of a Claude Code setup that runs whether the agent remembers it or not.
That makes them powerful, and it makes their cost invisible until a session feels slow or the
context fills with the same notice every morning. These are the habits that keep them healthy.

---

## Know when they run

| Event | Fires | Blocks? |
|-------|-------|---------|
| `SessionStart` | Every `startup`, `resume`, `clear` and `compact`. The reason arrives as `source` on stdin | A synchronous hook holds the user's first prompt until it finishes |
| `UserPromptSubmit` | Every prompt | Yes, before the model sees the prompt |
| `PreToolUse` / `PostToolUse` | Every matching tool call | Yes, on that call |
| `Stop` | Every time the agent finishes a turn | Yes, on the turn end |

A hook that takes two seconds and fires on every prompt costs two seconds on every prompt. Budget
for that the way you would budget a database query in a hot path.

## The habits

1. **Branch on `source`.** A `resume` keeps its old context, so re-injecting the same notes adds
   noise and nothing else. `clear` and `compact` lost context, so a short pointer helps there.
   Daily reminders belong on `startup` only.
2. **Skip work whose inputs have not changed.** Hash the files that decide the result (a lockfile,
   a requirements file, the folders you scan), store the hash under `.claude/.cache/`, and rerun
   only on a mismatch. Delete the old hash *before* the work starts, so a failed run retries next
   time.
3. **Print only what is new.** A hook that lists the same seven stale items every session trains
   everyone to ignore it. Compare against what you showed last time; collapse old items into one
   line ("7 items older than 14 days, run X to see them").
4. **Cap the output.** Inject a few lines and a pointer to the full file, not the file itself.
5. **Fail safe.** Any error: exit 0 with no output. A broken hook must never block a session or a
   prompt. The one exception is a guard hook whose *job* is to block (see below).
6. **One dispatcher per event.** Five separate `SessionStart` hooks start five interpreters. One
   script that calls five functions starts one, and it can share parsed input and a time budget.
7. **Explicit UTF-8.** On Windows, read stdin and write stdout as UTF-8 bytes
   (`sys.stdin.buffer` / `sys.stdout.buffer`). The cp1252 locale corrupts non-ASCII text in both
   directions, and a regex that silently stops matching is the worst kind of failure.
8. **Retire what you switched off.** A feature you disabled should also lose its hook entry, or
   it keeps running (and costing) for nothing.

## Guard hooks: block with a reason and a fix

A `PreToolUse` hook can stop a tool call that repeats a known mistake. When it blocks, the message
is what the agent reads next, so make it actionable:

```
[rule id] what was detected
  Seen:        the exact pattern that matched
  Do instead:  the command or approach that works
  Source:      where the lesson is recorded (a LESSONS.md tag)
```

A block without a "do instead" line just makes the agent try random variations.

## Template

`templates/session_start_example.py` puts habits 1 to 5 and 7 into about 100 lines of stdlib
Python: it skips `resume`, runs a placeholder expensive step only when watched files change, and
injects the "TODO next" section of `docs/BUILD_STATUS.md`, capped at 15 lines.

To use it:

```bash
cp templates/session_start_example.py .claude/hooks/session_start.py
echo ".claude/.cache/" >> .gitignore
```

Then add it to `.claude/settings.json` next to the existing hooks:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "python3 .claude/hooks/session_start.py" } ] }
    ]
  }
}
```

Check it before relying on it. Run it twice and confirm the second run skips the expensive step,
then change a watched file and confirm the step runs again:

```bash
echo '{"source":"startup"}' | python3 .claude/hooks/session_start.py
echo '{"source":"startup"}' | python3 .claude/hooks/session_start.py
echo '{"source":"resume"}'  | python3 .claude/hooks/session_start.py   # prints nothing
```

On Windows, use `python` instead of `python3` if that is your interpreter name.
