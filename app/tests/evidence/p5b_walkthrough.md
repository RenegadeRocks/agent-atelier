# P5-B v1 Walkthrough — Studio Floor (approachable subset)

Built per contract P5-B + §12.4, parallel track (supervisor-built while P3 ran on the laptop).

## Delivered
- `ui/studio-floor/` — self-contained SPA (no external resources): live agent floor (8 stations + human gate over the §10.1 pipeline; revise return-arcs with R-counters, red + ME escalation edge at cap), Pipeline lanes, Company view, activity feed (deterministic-gate rows visually distinct from CD judgment rows; masked raw drill-down), Needs-You tray → intervene drawer ("where & why" card, R1→R2 mini-timeline), trust ladder (never auto-flips; recommendation banner only), dark/light themes, density toggle, reduced-motion path, loading/empty/error/offline/first-run(DEMO badge) states, follow-a-piece Replay labeled "from audit record — nothing re-runs".
- `tools/export_floor_state.py` — pure `build_state()` projection from as-built Queue/Audit rows + kits; env-leak assertion on every write; creds imported only in `main()`.
- `tools/floor_serve.py` — stdlib server; POST /action writes ONLY Owner-Action + audit (structural guard refuses any status-writing client); creds-absent path queues to `actions.jsonl` (202) applied later by `tools/apply_floor_actions.py`.

## Verification
- `app/tests/test_p5_b.py`: 12/12 deterministic PASS (projection/seq/needs-you/trust math; demo fixture shape-valid; owner-action-never-status; invalid action 400; no-creds queue path; status-client refusal; env-leak refusal x2; UI self-containment scan).
- `node --check app.js` clean; headless-browser run over demo fixture: both themes, tabs, drawer, trust banner, follow-a-piece, offline degradation, 202-queue POST path.

## Deferred (visible-but-honest)
Animated handoff carriers (would fake liveness a snapshot poll doesn't have) · remaining §12.5 verbs · server-side rev optimistic-lock (needs Queue rev column, P5-A) · Replay scrubber (journey timeline only) · conductor box (display-only Orchestrator mode).

## Known risks (flagged for P5-A wiring)
Row lookup by piece_id at write time (add re-read-verify) · last-Owner-Action-write-wins without rev guard (orchestrator first-committed-wins is the backstop) · queued `actions.jsonl` applied without freshness check · env-leak assert is substring-based (fail-closed; may false-positive if an env value legitimately appears in sheet content).
