# WORKLOG — mid-contract scratchpad

This is the **hand-off memory** between sessions and between PCs (office ↔ home). Keep it
current and commit+push before you stop (build-protocol §2). On the other machine, `git
pull` then run `.agents/workflows/resume.md`. Antigravity's chat/memory is per-machine and
does not travel between PCs — this file, plus the code and the spec, is what remembers.

**Overwrite the block below** each time you stop mid-contract. When a contract is fully
done + authorized, clear it and tick the contract in `BUILD-STATUS.md`.

---

## Current

- **Contract:** P0 (Done)
- **Sub-tasks done:** Scaffold folder structure, MCP stubs, P0 tests, CI setup
- **Sub-tasks remaining:** None for P0
- **Current file state / where the code is:** `app/` folder created, test passed, CI wired.
- **▶ NEXT ACTION (the one thing to do on resume):** Run `.agents/workflows/build-P1-A.md`.
- **Open questions / waiting on owner:** —
- **Last commit:** (Pending owner prompt to commit)
- **Machine last worked on:** (Unknown/Current)

---

### Template (copy the shape above)

```
## Current
- Contract: P<id> (Phase <n>)
- Sub-tasks done: <bullet list>
- Sub-tasks remaining: <bullet list>
- Current file state: <which files exist, which are half-written, test red/green>
- ▶ NEXT ACTION: <one concrete next step>
- Open questions / waiting on owner: <...>
- Last commit: <hash / message>
- Machine last worked on: <office | home>
```
