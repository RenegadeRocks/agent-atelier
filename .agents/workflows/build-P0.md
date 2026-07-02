<!-- DERIVED — regenerate with `python3 tools/build_view_split.py`. Do NOT hand-edit.
The ten-field contract is specs/contracts/P0.md; the PRD (§19.1) is the source of truth. -->

# /build-P0 — Contract P0 (Phase 0)

Run this for **one** contract only, in a fresh context. Obey `.agents/rules/build-protocol.md`
and `GEMINI.md`. If you are picking up a half-finished P0, run
`.agents/workflows/resume.md` first.

**Prereq:** the previous contract is verified, committed, and the owner authorized P0
(check `BUILD-STATUS.md`).

## STEP 1 — Load ONLY these (context-rot discipline)
Read only the following. **Do NOT open the whole PRD.** `GEMINI.md` / `AGENTS.md` are
already always-loaded by the tool.
- `build-view/core.md`  — the always-load core (load every time)
- `build-view/sections/18-tech-stack-build-plan-for-antigravity.md`  — §18
- `build-view/sections/16-integrations-interfaces-mcp-first.md`  — §16
- `build-view/sections/app-d-specs-brands-file-map-authored-artifacts.md`  — Appendix D
- `specs/schemas/mcp_tool_outputs.schema.json`  — authored artifact (PRE-SEEDED: reconcile against the loaded §§ and extend it — do not author a blind duplicate)
- `specs/schemas/notify_payload.schema.json`  — authored artifact (PRE-SEEDED: reconcile against the loaded §§ and extend it — do not author a blind duplicate)
- `specs/contracts/P0.md`  — the ten-field BUNNY contract for this unit

Where the READ-SCOPE names a **subsection** (e.g. §12.2), read only that subsection inside
the loaded file and skip its siblings — a section file can contain later-phase material
(e.g. §12.4 lives in the §12 file but belongs to P5-B).

**Parked for later (do not read now):** §7–§15 — later phases.

## STEP 2 — Honor the contract
`specs/contracts/P0.md` is the contract. Its READ-SCOPE (verbatim from §19.1):
> read §18 (build workflow + governance), §16 (MCP contracts), Appendix D (file map).

Follow INTENT · SCOPE · NON-GOALS · INPUTS · INVARIANTS · ACTION exactly. **NON-GOALS are
hard boundaries** — do not build a later phase's work "while you're here."

## STEP 3 — Test-first → build → verify (build-protocol §1)
- Propose the files/structure first; wait for owner OK (no-YOLO).
- **Naming:** the proposed product source tree must NOT use directory names the repo `.gitignore` excludes (`build/`, `dist/`, `node_modules/`) or that source would be silently untracked and lost on `git pull`. Prefer a named package dir (e.g. `app/`) and scope any build/dist ignores under it.
- Author the contract's ACCEPTANCE/VERIFY behaviour as a **failing** Gherkin suite first
  (red), then implement to green. Add it to the growing regression suite.
- Build component-by-component to SCOPE/ACTION; show diffs; verify model IDs / deps
  against live docs (GEMINI.md §4).
- **VERIFY with captured evidence** (report-is-not-the-repo): run the piece / fire the negative test / capture the run.

## STEP 4 — Gate
GATE = the phase's test suite green **AND** the CI eval gate passes (build-protocol §1.6).
Contract gate (from §19.1):
> **GATE:** CI green on stubs; structure approved. Authorize P1.

## STEP 5 — Record & hand off (before you stop)
- Commit when the owner asks: `P0: <what landed> — <gate state>`.
- Update `BUILD-STATUS.md` — tick P0; next = P1-A.
- Update `WORKLOG.md` (contract, done, remaining, **next action**) — always, even if continuing.
- Log any deviation in `specs/deviation_log.md` (assumption → ground truth → decision).
- The owner then runs the **Validator pass** (`.agents/workflows/validate.md`) in a fresh
  conversation and applies its findings before closing the gate.
- Get owner **AUTHORIZATION** to release the next contract (you do not self-authorize;
  "authorized" in `BUILD-STATUS.md` is the owner's mark, never yours).

## Next
On owner AUTHORIZATION, run `.agents/workflows/build-P1-A.md`.
