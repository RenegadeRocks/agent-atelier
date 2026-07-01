<!-- DERIVED — regenerate with `python3 tools/build_view_split.py`. Do NOT hand-edit.
The ten-field contract is specs/contracts/P4-A.md; the PRD (§19.1) is the source of truth. -->

# /build-P4-A — Contract P4-A (Phase 4)

Run this for **one** contract only, in a fresh context. Obey `.agents/rules/build-protocol.md`
and `GEMINI.md`. If you are picking up a half-finished P4-A, run
`.agents/workflows/resume.md` first.

**Prereq:** the previous contract is verified, committed, and the owner authorized P4-A
(check `BUILD-STATUS.md`).

## STEP 1 — Load ONLY these (context-rot discipline)
Read only the following. **Do NOT open the whole PRD.** `GEMINI.md` / `AGENTS.md` are
already always-loaded by the tool.
- `build-view/core.md`  — the always-load core (load every time)
- `build-view/sections/14-governance-safety-security.md`  — §14
- `build-view/sections/13-orchestration-scheduling.md`  — §13
- `build-view/sections/15-evaluation-quality.md`  — §15
- `build-view/sections/18-tech-stack-build-plan-for-antigravity.md`  — §18
- `build-view/sections/10-the-content-production-pipeline-state-machine.md`  — §10
- `specs/policies.yaml`  — authored artifact
- `specs/contracts/P4-A.md`  — the ten-field BUNNY contract for this unit

**Parked for later (do not read now):** §12.4 and the publish-time referee (P4-B).

## STEP 2 — Honor the contract
`specs/contracts/P4-A.md` is the contract. Its READ-SCOPE (verbatim from §19.1):
> read §14.2 (Policy Server + claim-grounding + fail-closed), §13.2 (circuit-breaker), §15.1–§15.3 + §18.2 (CI eval gate + golden set), §10.3 (blocker scenarios), policies.yaml.

Follow INTENT · SCOPE · NON-GOALS · INPUTS · INVARIANTS · ACTION exactly. **NON-GOALS are
hard boundaries** — do not build a later phase's work "while you're here."

## STEP 3 — Test-first → build → verify (build-protocol §1)
- Propose the files/structure first; wait for owner OK (no-YOLO).
- Author the contract's ACCEPTANCE/VERIFY behaviour as a **failing** Gherkin suite first
  (red), then implement to green. Add it to the growing regression suite.
- **Mandatory before any publish path:** the ledger-linter test (a rotation-violating draft is rejected pre-CD) and the fail-closed safety test must exist and pass.
- Build component-by-component to SCOPE/ACTION; show diffs; verify model IDs / deps
  against live docs (GEMINI.md §4).
- **VERIFY with captured evidence** (report-is-not-the-repo): run the piece / fire the negative test / capture the run.

## STEP 4 — Gate
GATE = the phase's test suite green **AND** the CI eval gate passes (build-protocol §1.6).
Contract gate (from §19.1):
> **GATE (§19 P4-A exit):** deterministic safety/claim scenarios pass; breaker fires; CI eval gate blocks a golden-set regression. Authorize P4-B.

## STEP 5 — Record & hand off (before you stop)
- Commit when the owner asks: `P4-A: <what landed> — <gate state>`.
- Update `BUILD-STATUS.md` — tick P4-A; next = P4-B.
- Update `WORKLOG.md` (contract, done, remaining, **next action**) — always, even if continuing.
- Log any deviation in `specs/deviation_log.md` (assumption → ground truth → decision).
- Get owner **AUTHORIZATION** to release the next contract (you do not self-authorize).

## Next
On owner AUTHORIZATION, run `.agents/workflows/build-P4-B.md`.
