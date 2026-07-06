# Agent Atelier — Handoff & Quickstart

**State: feature-complete vs the PRD. All eleven contracts (P0 → P6) built and
independently validated.** Evidence: `app/tests/evidence/p*_validation.md` (one
verdict table per contract), `specs/deviation_log.md` (the honest build record),
`BUILD-STATUS.md` / `WORKLOG.md` (state), CI green at HEAD.

## Quickstart — the whole system in five commands

Prereqs: Python 3.11+, `pip install -r requirements.txt`, and a `.env` you were
handed personally (never committed): `GOOGLE_API_KEY`,
`GOOGLE_APPLICATION_CREDENTIALS` (service-account JSON path, outside the repo).
Deterministic parts (4, and the tests) need no keys at all.

1. **Onboard a brand (guided interview, terminal by design)**
   `python onboard_brand.py demo/brand-packs/chuski-club/`
   → The Brand Onboarding Strategist ingests `sources/`, drafts everything
   non-safety, ASKS you for the safety rules (never guessed), probes a
   violation on purpose (first-light), then the CLI — code, not the LLM —
   saves and validates `brands/<slug>/brand_kit.yaml` and flips it ACTIVE.
   Bad kits quarantine as `.draft.yaml`.

2. **Plan a week (deterministic, any date)**
   `python -m app.scheduler --as-of 2026-07-06`
   → The Monday tick composes each active brand's WeekPlan from its kit's
   `standing_week`, honoring §9.5 backpressure (deep queue + absent owner ⇒
   pause).

3. **Produce a piece (live: ~10–15 model calls)**
   → `run_pipeline` drives PLAN→DRAFT→LINT→REVIEW→VISUALIZE→QUEUE: drafts are
   linted deterministically, judged by the Creative Director (revise loop
   capped, then escalation), imaged text-free (OCR gate), composited with the
   brand type system, uploaded to GCS, queued to the Sheet with a stable
   `piece_id`. Every write is audited.

4. **Operate from the console (no keys needed for demo data)**
   `python tools/export_floor_state.py && python tools/floor_serve.py`
   → open http://127.0.0.1:8787 — the Studio Floor: live agent floor, activity
   feed, Needs-You tray, trust ladder (display-only; autonomy is earned, never
   auto-flipped). Approve / Request changes / Reject are real: each click is an
   Owner-Action cell write + audit row. (Double-clicking
   `ui/studio-floor/index.html` opens a demo-data tour, actions disabled.)

5. **Honor the owner's decision (publish path, manual by scope)**
   `python -m app.approval_poller`
   → the poller reads Owner-Action cells (the ONLY human-writable column),
   re-runs the deterministic safety gauntlet on every Approve, exports the
   Post Kit to `brands/<brand>/handoff/<piece_id>/`, and records Mark-posted →
   Published. Instagram auto-publish is intentionally absent at launch
   ("won't auto-publish — hand off by hand").

## The governance spine (what makes this an *agents* project)

- **One source of truth:** the Google Sheet (queue + append-only audit). The
  console is a projection; the orchestrator is the sole writer of Status;
  humans own exactly one column.
- **Deterministic floor, semantic ceiling:** P4-A's gauntlet (fail-closed
  safety fields, claim lexicon, forbidden phrases, breaker) contains zero LLM
  calls; the CD/referee judge above it, and in AUTO mode a judge failure fails
  CLOSED.
- **Fresh-session everything:** builders and validators ran as separate
  sessions over this repo; every contract's exit needed an independent
  validator's PASS plus green CI verified from raw `gh run list` output —
  never from a report's claims.
- **The learning loop:** `app/tools/post_publish_audit.py` (independent judge;
  measured escape rate 5.6% on 18 pieces, 95% CI [1.0%, 25.8%]) and
  `app/tools/monthly_retro.py` (owner corrections → canon amendments).

## Read next, in order

1. `specs/deviation_log.md` — the build's honest history (including the
   fabricated-evidence incident and every mock caught at a gate).
2. `specs/PRD-Agentic-Content-Studio.md` — the source of truth (§19.1 = the
   eleven contracts).
3. `app/tests/evidence/` — validation verdicts + the audit/retro reports.
4. `.agents/rules/build-protocol.md` — the working agreements that kept the
   agents honest.

## Known-and-bounded (sequenced, not missing)

Graphical intake (Brand Desk / conductor box) is Phase-later per the PRD — the
console shows those sockets disabled with honest tooltips; onboarding is the
terminal interview above. Live in-flight streaming (WebSocket relay) is
sequenced behind the snapshot exporter; the connection chip says so. Remaining
minors are enumerated in each validation report. Daily Gemini Pro quota is
250 requests/key — one live piece costs ~10–15.
