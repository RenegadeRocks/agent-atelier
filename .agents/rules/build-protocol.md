# BUILD PROTOCOL — the always-on build loop (read this every session)

> **Scope.** This is the operating rule for **building Agent Atelier in Antigravity**.
> `GEMINI.md` says *what* the product is and *how* to build (DNA, no-YOLO, model-currency,
> conventions, definition-of-done). **This file says how the build LOOP runs** —
> which spec to load when, one contract at a time, and how to hand off between
> sessions and machines. On any conflict about product behaviour, `GEMINI.md` and the
> PRD win; this file only governs the loop. Keep it obeyed literally.

---

## 0. THE ONE RULE — never load the whole PRD

The PRD (`specs/PRD-Agentic-Content-Studio.md`, ~2,840 lines) is the source of truth,
but reading it whole while coding a phase causes **context rot** — attention degrades
and parked sections become distractors. So:

- **Per contract, load only:** `build-view/core.md` **+** that contract's READ-SCOPE
  files. Nothing else. (`GEMINI.md` / `AGENTS.md` are always loaded by the tool — that
  is the whole global layer.)
- Each contract's exact file list is in **`.agents/workflows/build-<id>.md`** and in
  **`build-view/00-index.md`** (the "Per-contract READ-SCOPE → files" table).
- **Start a fresh context for each contract.** Do not carry a finished phase's files
  into the next.
- `build-view/` is a **DERIVED, read-only** view of the PRD. Never hand-edit it. If you
  need a section not in your READ-SCOPE, open the real §§ in the PRD — but prefer the
  parked-until-later discipline: build the phase you are in.

---

## 1. THE LOOP — eleven contracts, in order, lock-and-proceed

Build order (never reorder): **P0 → P1-A → P1-B → P2-A → P2-B → P3 → P4-A → P4-B →
P5-A → P5-B → P6.** For the **next** contract only, run its workflow
(`.agents/workflows/build-<id>.md`). Each contract is one pass of this loop:

1. **Load** `build-view/core.md` + the contract's READ-SCOPE files (from its workflow).
   Read `specs/contracts/<id>.md` — the ten-field BUNNY contract for this unit.
2. **Propose, don't YOLO.** Propose the files/structure you will add; wait for owner OK
   before scaffolding (GEMINI.md §3).
3. **Test-first.** Author the phase's ACCEPTANCE Gherkin as a failing suite **before**
   the code (red), then implement to green. The two mandatory tests must exist before
   any publish path: the ledger-linter test and the fail-closed safety test.
4. **Build** component-by-component to the contract's SCOPE/ACTION; show diffs; match
   conventions; verify model IDs / deps against live docs (GEMINI.md §4, §3.6).
5. **VERIFY with evidence** (report-is-not-the-repo): run the piece, fire the negative
   test, capture the run. A description is not a pass.
6. **Gate = green suite + CI eval gate.** Only then is the contract *locked*.
7. **Record & hand off (every contract, before you stop):**
   - Commit (see §3). Update **`BUILD-STATUS.md`** (tick the contract; name the next).
   - Update **`WORKLOG.md`** (see §2) — even if you are continuing.
   - Log any deviation in **`specs/deviation_log.md`** (see §4).
8. **AUTHORIZATION.** The owner signs off and releases the next contract. You do not
   self-authorize the next phase.

Gates are quality checkpoints, **not** stopping lines — the full P0–P6 scope is the
target. But never open contract N+1 until N is verified, committed, and authorized.

**Scope discipline.** Resist "just add the stub for later." Build the contract you are
in; its NON-GOALS are hard boundaries. Adding P4's Policy Server during P1 is exactly
how phases blur.

---

## 2. STOPPING MID-CONTRACT (and switching PCs)

Antigravity's chat and per-machine memory do **not** travel between PCs (and must not be
relied on for build state), so **the repo must carry the state.** Before you stop — for any
reason, even mid-file:

- Bring **`WORKLOG.md`** current: the contract in progress, sub-tasks done, sub-tasks
  remaining, current file state, and **the single NEXT ACTION**.
- **Commit and push** (§3). The repo — code + WORKLOG + BUILD-STATUS + deviation_log +
  the spec — is the only thing that travels between the office and home PCs.

To resume on the other machine after `git pull`, run **`.agents/workflows/resume.md`**.
Prefer to stop at a green test or a finished file, not mid-edit.

---

## 3. COMMITS (only when the owner asks to commit/push)

Small, per-contract or per-sub-task commits. Suggested message shape:
`P<id>: <what landed> — <gate state>`. Push before switching machines. Never force-push
shared branches. Two PCs (office + home) share one remote; the repo is the single
source of truth — chat history and tool "memories" do NOT travel, only committed files.

---

## 4. CHANGING THE SPEC MID-BUILD (e.g. an agent prompt is wrong)

Code is disposable; the spec is durable — so fix the **spec artifact**, not just the
code:

1. Edit it **where it lives** (`specs/agents/…`, `specs/canon/…`, `specs/policies.yaml`,
   or the owning PRD section). The running system reads that file.
2. **Log it** in `specs/deviation_log.md`: assumption → ground truth / reason →
   decision. This entry carries the intent so any later session (or the other PC) can
   reconcile without this session's context.
3. If you edited the **PRD**, **regenerate** so build-view + contracts + workflows stay in
   sync: `python3 tools/build_view_split.py` (then `--verify` confirms the tree matches the
   PRD and writes nothing — run it in CI / after `git pull`). build-view, `specs/contracts/`,
   and `.agents/workflows/build-*.md` are derived — never hand-edit them.
4. For a **large redesign** (not a tweak), treat it as a spec revision — author it
   focused, re-verify, re-split — then resume the build.

Full procedure: **`.agents/workflows/change-request.md`**.

---

## 5. NON-NEGOTIABLE INVARIANTS (restated; full text in GEMINI.md / §14.2)

- **Fail-closed safety.** `claims_forbidden` / `non_disclosure_rules` / `required_framing`
  block when empty or unconfirmed — "unknown" = block publish, route to a human.
- **Secrets never in prompts.** They resolve **only** into the tool/MCP auth layer,
  never into model-visible context.
- **Security before publish.** Policy Server + sandbox + secrets vault + append-only
  audit are wired **before** any publish tool is enabled. Publish is turned on last.
- **No faked MCP, no silent model fallback.** A genuine conformant MCP server is the
  floor; on any provider error other than a live 404, capture it verbatim, stop,
  escalate.
- **No brand literal hardcoded.** Emit `[[VARIABLE]]` tokens; the resolver fills them.

---

## 6. WHERE TO START, RIGHT NOW

1. Read **`BUILD-STATUS.md`** — it names the next contract.
2. Open **`.agents/workflows/build-<next>.md`** and follow it.
3. If you are picking up a half-done contract, use **`.agents/workflows/resume.md`** first.

---

## 7. COMPLETION REPORTS

Before any completion report: `git push`. Every report ends with the commit SHA and both GitHub Actions run URLs. You MUST verify the conclusion of both runs via `gh run list` and state their conclusion (e.g. "completed success") in the report. A completion claim without pushed, linkable evidence of GREEN/successful runs is a false report and invalid.
