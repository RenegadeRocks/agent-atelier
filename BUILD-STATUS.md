# BUILD-STATUS — Agent Atelier

The live build checklist. **Update it at every contract hand-off** (build-protocol §1.7).
Build order is fixed (§19.3) — do not reorder. One contract at a time, lock-and-proceed.

> **▶ NEXT CONTRACT: P0** — run `.agents/workflows/build-P0.md`.

## Contracts (P0 → P6)

| # | Contract | Phase | Status | Gate (short) |
|---|----------|-------|--------|--------------|
| 1 | P0   | 0 | ⬜ not started | CI green on stubs; structure approved |
| 2 | P1-A | 1 | ⬜ | one idea flows through all six agents, in role |
| 3 | P1-B | 1 | ⬜ | one on-brand piece passes both gates + the linter → lands in the Sheets queue |
| 4 | P2-A | 2 | ⬜ | P1 brand runs entirely from `brand_kit.yaml`; a 2nd toy brand via kit only; missing-var blocks |
| 5 | P2-B | 2 | ⬜ | new brand onboarded by interview, zero code changes, produces a piece |
| 6 | P3   | 3 | ⬜ | a full week auto-plans/drafts/reviews/queues; rotation-violating draft rejected pre-CD; §9.5 backpressure pause |
| 7 | P4-A | 4 | ⬜ | deterministic safety/claim scenarios pass; breaker fires; CI eval blocks a golden-set regression |
| 8 | P4-B | 4 | ⬜ | publish-time referee catches a smuggled-CTA/tone near-miss; degrades to advisory cleanly |
| 9 | P5-A | 5 | ⬜ | owner approves via Sheets + app; manual publish works; auto-publish gated, idempotent, audited |
| 10| P5-B | 5 | ⬜ | Studio-Floor scenarios pass; live handoff/loop visible; intervention audited; trust never auto-flips |
| 11| P6   | 6 | ⬜ | escape-rate audit reports CIs; CD↔owner calibration tracked; two brands on the same unchanged code |

Legend: ⬜ not started · 🔨 in progress · ✅ verified + committed + authorized.

## Scaffolding already provided (pre-seeded in this handoff)

These are done — you do **not** re-create them at P0:
- ✅ `specs/` bundle — agents, canon, skills, `policies.yaml`, `resolver.md`, `brand_kit.schema.json` + template, `golden_set.md`, `secrets.md`
- ✅ `GEMINI.md` / `AGENTS.md` — project DNA + skills router + the build loop (§0)
- ✅ `.agents/rules/build-protocol.md` + `.agents/workflows/*`
- ✅ `build-view/` (derived), `specs/contracts/P0…P6.md` (derived), `specs/deviation_log.md` (seeded)
- ✅ `brands/aol/` — the worked-example Brand Kit + two Offering Briefs

What P0 still has to do (its real ACTION): propose the tree for owner approval, add the
**MCP tool stubs** (§16), wire **CI** (include `python3 tools/build_view_split.py --verify`
so a PRD edit can't be committed without its regenerated derived files), confirm the
ADK/Antigravity project layout (conform + log any deviation), commit. Then authorize P1.

> **Naming caveat:** the proposed product source tree must not use directory names the
> `.gitignore` excludes (`build/`, `dist/`, `node_modules/`) — source under those would be
> silently untracked and lost on `git pull`. Use a package dir like `app/`.

## Scope-cut order (only if the July-6 deadline bites; §19.2)

Cut from the tail: **P6** → **P5-B** (Studio Floor console — demo-polish) → **P4-B**
(publish-time semantic referee — the one soft gate). **P4-A** (the falsifiable governance
floor) and **P5-A** (the publish path that must ship) never drop. The gates, not the
time-boxes, are the schedule.
