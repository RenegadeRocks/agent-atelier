<!-- DERIVED — regenerate with `python3 tools/build_view_split.py`. Do NOT hand-edit.
The ten-field contract is specs/contracts/P1-A.md; the PRD (§19.1) is the source of truth. -->

# /build-P1-A — Contract P1-A (Phase 1)

Run this for **one** contract only, in a fresh context. Obey `.agents/rules/build-protocol.md`
and `GEMINI.md`. If you are picking up a half-finished P1-A, run
`.agents/workflows/resume.md` first.

**Prereq:** the previous contract is verified, committed, and the owner authorized P1-A
(check `BUILD-STATUS.md`).

## STEP 1 — Load ONLY these (context-rot discipline)
Read only the following. **Do NOT open the whole PRD.** `GEMINI.md` / `AGENTS.md` are
already always-loaded by the tool.
- `build-view/core.md`  — the always-load core (load every time)
- `build-view/sections/08-the-agent-roster-generic-parameterized.md`  — §8
- `build-view/sections/09-the-canon-engine-documents-the-harness-s-shared.md`  — §9
- `build-view/sections/10-the-content-production-pipeline-state-machine.md`  — §10
- `specs/agents/managing-editor.md`  — authored artifact (PRE-SEEDED: reconcile against the loaded §§ and extend it — do not author a blind duplicate)
- `specs/agents/evergreen-content.md`  — authored artifact (PRE-SEEDED: reconcile against the loaded §§ and extend it — do not author a blind duplicate)
- `specs/agents/research-verification.md`  — authored artifact (PRE-SEEDED: reconcile against the loaded §§ and extend it — do not author a blind duplicate)
- `specs/agents/creative-director.md`  — authored artifact (PRE-SEEDED: reconcile against the loaded §§ and extend it — do not author a blind duplicate)
- `specs/agents/visual-production.md`  — authored artifact (PRE-SEEDED: reconcile against the loaded §§ and extend it — do not author a blind duplicate)
- `specs/agents/publishing-operations.md`  — authored artifact (PRE-SEEDED: reconcile against the loaded §§ and extend it — do not author a blind duplicate)
- `specs/canon/`  — authored artifact (PRE-SEEDED: reconcile against the loaded §§ and extend it — do not author a blind duplicate)
- `specs/skills/`  — authored artifact (PRE-SEEDED: reconcile against the loaded §§ and extend it — do not author a blind duplicate)
- `specs/contracts/P1-A.md`  — the ten-field BUNNY contract for this unit

Where the READ-SCOPE names a **subsection** (e.g. §12.2), read only that subsection inside
the loaded file and skip its siblings — a section file can contain later-phase material
(e.g. §12.4 lives in the §12 file but belongs to P5-B).

**Parked for later (do not read now):** §7 (Brand Kit), §12.4, §14 — later phases.

## STEP 2 — Honor the contract
`specs/contracts/P1-A.md` is the contract. Its READ-SCOPE (verbatim from §19.1):
> read §8 (roster + agent instruction files), §9.1–§9.4 (engine docs + linter), §10.1 (pipeline).

Follow INTENT · SCOPE · NON-GOALS · INPUTS · INVARIANTS · ACTION exactly. **NON-GOALS are
hard boundaries** — do not build a later phase's work "while you're here."

## STEP 3 — Test-first → build → verify (build-protocol §1)
- Propose the files/structure first; wait for owner OK (no-YOLO). **Your proposal MUST
  open with three declarations — a plan missing any of them is invalid:**
  1. **CONSUMES:** every pre-seeded artifact from STEP 1 you will wire in, by path. A plan
     that marks `[NEW]` any path that already exists in the repo is auto-rejected —
     reconcile/extend the existing file, never author a parallel copy.
  2. **NON-GOALS:** restate what this contract does NOT build (from the contract) and
     confirm you will not touch it.
  3. **ON-FAIL:** what you will do when blocked (missing credential, API, SDK, account):
     **STOP and ask the owner.** You never stub silently, never fake a green test, never
     downgrade a SCOPE item to a mock without an owner-approved deviation-log entry
     (§14.3 / §18.4.4 — honest refusal over silent fallback).
- Author the contract's ACCEPTANCE/VERIFY behaviour as a **failing** Gherkin suite first
  (red), then implement to green. Add it to the growing regression suite.
- Build component-by-component to SCOPE/ACTION; show diffs; verify model IDs / deps
  against live docs (GEMINI.md §4).
- **VERIFY with captured evidence** (report-is-not-the-repo): run the piece / fire the negative test / capture the run.

## STEP 4 — Gate
GATE = the phase's test suite green **AND** the CI eval gate passes (build-protocol §1.6).
Contract gate (from §19.1):
> **GATE:** one idea flows through all six agents in role. Authorize P1-B.

## STEP 5 — Record & hand off (before you stop)
- Commit when the owner asks: `P1-A: <what landed> — <gate state>`.
- Update `BUILD-STATUS.md` — tick P1-A; next = P1-B.
- Update `WORKLOG.md` (contract, done, remaining, **next action**) — always, even if continuing.
- Log any deviation in `specs/deviation_log.md` (assumption → ground truth → decision).
- The owner then runs the **Validator pass** (`.agents/workflows/validate.md`) in a fresh
  conversation and applies its findings before closing the gate.
- Get owner **AUTHORIZATION** to release the next contract (you do not self-authorize;
  "authorized" in `BUILD-STATUS.md` is the owner's mark, never yours).

## Next
On owner AUTHORIZATION, run `.agents/workflows/build-P1-B.md`.
