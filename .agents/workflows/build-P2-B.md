<!-- DERIVED — regenerate with `python3 tools/build_view_split.py`. Do NOT hand-edit.
The ten-field contract is specs/contracts/P2-B.md; the PRD (§19.1) is the source of truth. -->

# /build-P2-B — Contract P2-B (Phase 2)

Run this for **one** contract only, in a fresh context. Obey `.agents/rules/build-protocol.md`
and `GEMINI.md`. If you are picking up a half-finished P2-B, run
`.agents/workflows/resume.md` first.

**Prereq:** the previous contract is verified, committed, and the owner authorized P2-B
(check `BUILD-STATUS.md`).

## STEP 1 — Load ONLY these (context-rot discipline)
Read only the following. **Do NOT open the whole PRD.** `GEMINI.md` / `AGENTS.md` are
already always-loaded by the tool.
- `build-view/core.md`  — the always-load core (load every time)
- `build-view/sections/07-the-brand-kit-product-agnostic-configuration.md`  — §7
- `build-view/sections/app-a-worked-example-the-art-of-living-ludhiana-brand.md`  — Appendix A
- `specs/contracts/P2-B.md`  — the ten-field BUNNY contract for this unit

Where the READ-SCOPE names a **subsection** (e.g. §12.2), read only that subsection inside
the loaded file and skip its siblings — a section file can contain later-phase material
(e.g. §12.4 lives in the §12 file but belongs to P5-B).

**Parked for later (do not read now):** §12.4, §15.4 — later phases.

## STEP 2 — Honor the contract
`specs/contracts/P2-B.md` is the contract. Its READ-SCOPE (verbatim from §19.1):
> read §7.1 (intake + first-light), §7.8 (archetype starters), Appendix A.

Follow INTENT · SCOPE · NON-GOALS · INPUTS · INVARIANTS · ACTION exactly. **NON-GOALS are
hard boundaries** — do not build a later phase's work "while you're here."

## STEP 3 — Test-first → build → verify (build-protocol §1)
- Propose the files/structure first; wait for owner OK (no-YOLO).
- Author the contract's ACCEPTANCE/VERIFY behaviour as a **failing** Gherkin suite first
  (red), then implement to green. Add it to the growing regression suite.
- Build component-by-component to SCOPE/ACTION; show diffs; verify model IDs / deps
  against live docs (GEMINI.md §4).
- **VERIFY with captured evidence** (report-is-not-the-repo): run the piece / fire the negative test / capture the run.

## STEP 4 — Gate
GATE = the phase's test suite green **AND** the CI eval gate passes (build-protocol §1.6).
Contract gate (from §19.1):
> **GATE (§19 P2 exit):** new brand onboarded by interview with zero code changes; produces a piece. Authorize P3.

## STEP 5 — Record & hand off (before you stop)
- Commit when the owner asks: `P2-B: <what landed> — <gate state>`.
- Update `BUILD-STATUS.md` — tick P2-B; next = P3.
- Update `WORKLOG.md` (contract, done, remaining, **next action**) — always, even if continuing.
- Log any deviation in `specs/deviation_log.md` (assumption → ground truth → decision).
- Get owner **AUTHORIZATION** to release the next contract (you do not self-authorize).

## Next
On owner AUTHORIZATION, run `.agents/workflows/build-P3.md`.
