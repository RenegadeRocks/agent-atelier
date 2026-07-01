# Conscious-deviation log

Every time the tool's actual layout/convention differs from the spec's assumption, or a
spec artifact is changed mid-build, **conform to ground truth and record it here** — never
silently (build-protocol §4, PRD §18.4.4). Deviations are part of the audit surface
(§14.5): conscious and visible.

**Entry format:**
```
### <date> — <short title>  [<contract or "handoff">]
- Assumption: <what the spec/contract expected>
- Ground truth / reason: <what was actually found, or why the change was needed>
- Decision: <what was done>
- Files touched: <paths>
```

---

### 2026-07-01 — Antigravity governance layout + pre-seeded build scaffolding  [handoff]
- **Assumption:** PRD §18.3 / P0 name `/.agent/skills` for reusable workflows and imply the
  build scaffolding (`/specs/contracts/`, `deviation_log.md`) is created *during* P0.
- **Ground truth / reason:** Antigravity's always-loaded governance lives in
  `.agents/{rules,workflows}/` (plural). The product's Agent Skills are the authored
  artifacts at `specs/skills/` (GEMINI.md §8 router), which is where they already exist.
  To make the two-PC handoff truly ready-to-go, the derived build scaffolding was
  pre-generated rather than left to P0.
- **Decision:** (1) Build-time governance → `.agents/rules/build-protocol.md` +
  `.agents/workflows/*`; product skills stay at `specs/skills/`. (2) `build-view/`,
  `specs/contracts/P*.md`, `.agents/workflows/build-*.md`, and this log are pre-seeded and
  **derived** from the PRD via `tools/build_view_split.py` (re-run after any PRD edit).
  P0's remaining ACTION is MCP stubs + CI + confirming the live ADK/Antigravity layout.
- **Files touched:** `.agents/**`, `build-view/**`, `specs/contracts/**`,
  `tools/build_view_split.py`, `GEMINI.md` §0/§9, `AGENTS.md` §0, `BUILD-STATUS.md`.

<!-- Add new entries below, newest first. -->
