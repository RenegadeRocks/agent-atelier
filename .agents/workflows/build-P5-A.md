<!-- DERIVED — regenerate with `python3 tools/build_view_split.py`. Do NOT hand-edit.
The ten-field contract is specs/contracts/P5-A.md; the PRD (§19.1) is the source of truth. -->

# /build-P5-A — Contract P5-A (Phase 5)

Run this for **one** contract only, in a fresh context. Obey `.agents/rules/build-protocol.md`
and `GEMINI.md`. If you are picking up a half-finished P5-A, run
`.agents/workflows/resume.md` first.

**Prereq:** the previous contract is verified, committed, and the owner authorized P5-A
(check `BUILD-STATUS.md`).

## STEP 1 — Load ONLY these (context-rot discipline)
Read only the following. **Do NOT open the whole PRD.** `GEMINI.md` / `AGENTS.md` are
already always-loaded by the tool.
- `build-view/core.md`  — the always-load core (load every time)
- `build-view/sections/12-review-approval-publishing-system-of-record.md`  — §12
- `specs/contracts/P5-A.md`  — the ten-field BUNNY contract for this unit

Where the READ-SCOPE names a **subsection** (e.g. §12.2), read only that subsection inside
the loaded file and skip its siblings — a section file can contain later-phase material
(e.g. §12.4 lives in the §12 file but belongs to P5-B).

**Parked for later (do not read now):** §12.4 (Studio Floor → P5-B).

## STEP 2 — Honor the contract
`specs/contracts/P5-A.md` is the contract. Its READ-SCOPE (verbatim from §19.1):
> read §12.1 (Review app), §12.3 (publishing + Post Kit + mark-as-posted), §12.5 (approval protocol), §12.2 (Sheets integrity).

Follow INTENT · SCOPE · NON-GOALS · INPUTS · INVARIANTS · ACTION exactly. **NON-GOALS are
hard boundaries** — do not build a later phase's work "while you're here."

## STEP 3 — Test-first → build → verify (build-protocol §1)
- Propose the files/structure first; wait for owner OK (no-YOLO).
- Author the contract's ACCEPTANCE/VERIFY behaviour as a **failing** Gherkin suite first
  (red), then implement to green. Add it to the growing regression suite.
- **Standing gate (GEMINI §3.3):** the ledger-linter test (a rotation-violating draft is rejected pre-CD) and the fail-closed safety test must both exist and pass **before any publish path is wired (P5-A)** — author each in the phase that builds its gate (linter: P3; fail-closed: P4-A) and keep both green from then on.
- Build component-by-component to SCOPE/ACTION; show diffs; verify model IDs / deps
  against live docs (GEMINI.md §4).
- **VERIFY with captured evidence** (report-is-not-the-repo): run the piece / fire the negative test / capture the run.

## STEP 4 — Gate
GATE = the phase's test suite green **AND** the CI eval gate passes (build-protocol §1.6).
Contract gate (from §19.1):
> **GATE (§19 P5-A exit):** owner approves via Sheets + app; manual publish works; auto-publish gated, idempotent, audited. Authorize P5-B.

## STEP 5 — Record & hand off (before you stop)
- Commit when the owner asks: `P5-A: <what landed> — <gate state>`.
- Update `BUILD-STATUS.md` — tick P5-A; next = P5-B.
- Update `WORKLOG.md` (contract, done, remaining, **next action**) — always, even if continuing.
- Log any deviation in `specs/deviation_log.md` (assumption → ground truth → decision).
- Get owner **AUTHORIZATION** to release the next contract (you do not self-authorize).

## Next
On owner AUTHORIZATION, run `.agents/workflows/build-P5-B.md`.
