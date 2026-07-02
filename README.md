# Agent Atelier — build handoff folder

This is a **ready-to-go project folder** for building Agent Atelier in **Google
Antigravity**. Everything the build needs is here: the whole PRD (the spec), the authored
`/specs` artifacts, the project DNA (`GEMINI.md`), and a **build harness** that drives the
build one gated contract at a time so a ~2,840-line spec never has to be loaded whole
(which would cause "context rot" and degrade quality).

You don't have to set anything up by hand. Antigravity reads these files **in place** and
writes product code as it builds — it does not need to scaffold the governance.

---

## What's in here (short version)

- **`GEMINI.md` / `AGENTS.md`** — project DNA + conventions + the build loop. Antigravity
  loads these first, every session. **Start by reading `GEMINI.md` §0.**
- **`.agents/rules/build-protocol.md`** — the always-on build-loop rule (the "how").
- **`.agents/workflows/build-P0.md … build-P6.md`** — one `/command` per contract.
  Plus `resume.md` (switch PCs / pick up mid-contract) and `change-request.md` (change the
  spec mid-build).
- **`specs/PRD-Agentic-Content-Studio.md`** — the whole PRD, the source of truth.
- **`specs/`** — the authored artifacts (agents, canon, skills, policies, resolver,
  schema, golden set, secrets) + the derived `contracts/` + the `deviation_log.md`.
- **`build-view/`** — a *derived* progressive-disclosure view of the PRD (core + per-section).
- **`tools/build_view_split.py`** — regenerates `build-view/`, `specs/contracts/`, and the
  per-contract workflows from the PRD. Re-run after any PRD edit.
- **`BUILD-STATUS.md`** — which contract is done / next. **`WORKLOG.md`** — mid-contract
  hand-off notes.
- **`brands/aol/`** — a worked-example Brand Kit.

(Full annotated tree: `GEMINI.md` §9.)

---

## 1. Put it on GitHub (once)

1. Create an **empty** private GitHub repo (no README/gitignore — this folder has them).
2. Unzip this folder locally, then from inside `agent-atelier/`:
   ```
   git init
   git add .
   git commit -m "Agent Atelier build handoff (P0-ready)"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

## 2. Build in Antigravity

1. Open the **`agent-atelier/` folder** as the project in Antigravity.
2. It auto-loads `GEMINI.md`, whose §0 tells the agent to read
   `.agents/rules/build-protocol.md` first (each `build-*.md` workflow points there too).
   So Antigravity already **knows the plan** the moment you open the folder — you just give
   it the go-signal. **Your first message can be exactly:**
   > *Read `GEMINI.md` and `.agents/rules/build-protocol.md`, check `BUILD-STATUS.md` for the
   > next contract, then run `.agents/workflows/build-P0.md`.*

   (After P0 is verified and you authorize the next one, the same message with `build-P1-A.md`,
   and so on down `BUILD-STATUS.md`.) You never have to re-explain the project — it's all in
   the repo.
3. Check `BUILD-STATUS.md` for the next contract (it starts at **P0**), then run its
   workflow — e.g. tell Antigravity: **"Run `.agents/workflows/build-P0.md`."**
4. The workflow tells it exactly which files to load (a small slice, not the whole PRD),
   to write tests first, build, VERIFY with evidence, then stop at the gate.
5. **You authorize each next contract.** When P0's gate is green and committed, release
   P1 by running `.agents/workflows/build-P1-A.md`. Repeat P0 → P6, in order.

## 3. Two PCs (office ↔ home)

The repo is the single source of truth — Antigravity's chat/memory does **not** travel
between machines, but committed files do.

- **Before you stop:** update `WORKLOG.md`, then `git add -A && git commit && git push`.
- **On the other PC:** `git pull`, then `python3 tools/build_view_split.py --verify` (it
  confirms the derived view matches the PRD you just pulled — if it reports drift, run
  `python3 tools/build_view_split.py` to regenerate). Then run
  **`.agents/workflows/resume.md`** if you were mid-contract (it re-loads only that
  contract's scope and continues from WORKLOG's *next action* — it does not restart).

## 4. Two rules that keep it clean

- **`build-view/`, `specs/contracts/`, and `.agents/workflows/build-*.md` are DERIVED.**
  Never hand-edit them. If you edit the PRD, regenerate — and verify the tree is in sync
  (the verify writes nothing; wire it into CI / a pre-commit hook so a PRD edit can't be
  committed without its regenerated derived files):
  ```
  python3 tools/build_view_split.py            # regenerate after a PRD edit
  python3 tools/build_view_split.py --verify   # check the tree matches the PRD (CI / after git pull)
  ```
  Optional but recommended — install the pre-commit guard so this can't be forgotten
  (one command, works on Windows / macOS / Linux):
  ```
  git config core.hooksPath tools/git-hooks
  ```
  **Windows note:** wherever these docs say `python3`, use `python` (the splitter runs on
  either; the hook auto-detects).
  **CI already enforces this server-side:** `.github/workflows/verify-build-view.yml` runs
  `--verify` on every push/PR, so a PRD edit committed without its regenerated derived files
  fails the check.
- **Change the spec, not just the code.** If output is wrong, fix the spec artifact where
  it lives and log it in `specs/deviation_log.md` — see `.agents/workflows/change-request.md`.

## Requirements

- **Antigravity** (with Gemini + ADK) for the build.
- **git** for the two-PC workflow.
- **Python 3** (standard library only) to run the splitter.
