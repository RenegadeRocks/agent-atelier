# BUILD-STATUS — Agent Atelier

> **✅ BUILD COMPLETE (2026-07-06).** All eleven contracts (P0 → P6) are built, verified,
> committed, and **independently validated**. CI green at HEAD. The system is
> feature-complete vs the PRD (CONTRACT P6, clause 9). Remaining work is submission
> material (writeup + ≤5-min video) and owner-approved polish only.

Historical build order was fixed (§19.3), one contract at a time, lock-and-proceed. This
file is kept as the final contract ledger.

## Contracts (P0 → P6)

| # | Contract | Phase | Status | Gate (short) |
|---|----------|-------|--------|--------------|
| 1 | P0   | 0 | ✅ verified + committed + authorized | CI green on stubs; structure approved |
| 2 | P1-A | 1 | ✅ verified + committed + authorized | one idea flows through all six agents, in role |
| 3 | P1-B | 1 | ✅ verified + committed + authorized | one on-brand piece passes both gates + the linter → lands in the Sheets queue |
| 4 | P2-A | 2 | ✅ verified + committed + authorized | P1 brand runs entirely from `brand_kit.yaml`; a 2nd toy brand via kit only; missing-var blocks |
| 5 | P2-B | 2 | ✅ verified + committed + authorized | new brand onboarded by interview, zero code changes, produces a piece |
| 6 | P3   | 3 | ✅ verified + committed + authorized | a full week auto-plans/drafts/reviews/queues; rotation-violating draft rejected pre-CD; §9.5 backpressure pause |
| 7 | P4-A | 4 | ✅ verified + committed + authorized | deterministic safety/claim scenarios pass; breaker fires; CI eval blocks a golden-set regression |
| 8 | P4-B | 4 | ✅ verified + committed + authorized | publish-time referee catches a smuggled-CTA/tone near-miss; degrades to advisory cleanly |
| 9 | P5-A | 5 | ✅ verified + committed + authorized | owner approves via Sheets + app; manual publish works; auto-publish gated, idempotent, audited |
| 10| P5-B | 5 | ✅ verified + committed + authorized | Studio-Floor scenarios pass; live handoff/loop visible; intervention audited; trust never auto-flips |
| 11| P6   | 6 | ✅ verified + committed + authorized | Learning loop & multi-brand proof; audit script runs successfully |

## Evidence

- Per-contract verdicts: `app/tests/evidence/p*_validation.md`
- Post-publication audit (escape rate + CI): `app/tests/evidence/p6_audit_report.md`
- Honest build record (every mock, false green, and fix): `specs/deviation_log.md`
- Deterministic suite: `python -m pytest app/tests -m "not live"`

## Build history (for reference)

- The demo was captured contract-by-contract from P1-B onward; each gate's VERIFY evidence
  is a recorded segment (`specs/demo_playbook.md`, `RECORDING-PLAYBOOK.md`).
- The orchestrator tick + linter take an injectable logical `now` (`--as-of`) so a full week
  can be simulated for the demo and for P3's VERIFY.
- Scope-cut order was never triggered — all eleven contracts shipped. (Had the deadline bitten,
  the planned tail-cut was P6 → P5-B → P4-B, with P4-A and P5-A never dropped.)
