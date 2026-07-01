# /resume — pick up a half-finished contract (same PC or the other one)

Use this when a contract was **left mid-way** — you stopped and switched machines, or a
session ended before the contract's gate. Antigravity's chat/memory is per-machine and
does not travel between PCs, so you rebuild your understanding from the repo, not from
memory. (If a contract is *finished and authorized*, don't use this — just run the next
`build-<id>.md`.)

## Do this, in order

1. **Sync.** `git pull` (if you switched PCs). The repo is the single source of truth —
   code + spec + `WORKLOG.md` + `BUILD-STATUS.md` + `specs/deviation_log.md`. Chat
   history and any tool "memory" do **not** travel between machines.
   Then confirm the derived view matches the spec you just pulled:
   `python3 tools/build_view_split.py --verify`. If it reports drift, run
   `python3 tools/build_view_split.py` to regenerate before doing any contract work
   (someone edited the PRD without re-splitting).
2. **Read the state, not the whole PRD:**
   - `BUILD-STATUS.md` — which contract is in progress (call it `P<n>`).
   - `WORKLOG.md` — sub-tasks done, sub-tasks remaining, current file state, and the
     single **NEXT ACTION**.
   - `specs/deviation_log.md` — any ground-truth decisions already taken this build.
3. **Re-open only `P<n>`'s scope** (context-rot discipline): `build-view/core.md` +
   the files listed in `.agents/workflows/build-P<n>.md` STEP 1 + `specs/contracts/P<n>.md`.
4. **Re-read the code already written for `P<n>`** so you match what exists (conventions,
   half-done files, existing tests). Run the phase's test suite to see current red/green.
5. **Continue from WORKLOG's NEXT ACTION.** Do **NOT** restart the contract or re-scaffold
   what already exists. Do **NOT** jump ahead to `P<n+1>`.
6. When you next stop, update `WORKLOG.md` and commit+push again (build-protocol §2).

## The one-liner to paste when resuming

> Resuming mid-contract on another machine. Read `BUILD-STATUS.md` + `WORKLOG.md`;
> re-open `build-view/core.md` + contract P\<n>'s READ-SCOPE files
> (`.agents/workflows/build-P<n>.md`) + `specs/contracts/P<n>.md`; re-read the code
> already written for P\<n>; continue from WORKLOG's "Next action" — do NOT restart the
> contract.
