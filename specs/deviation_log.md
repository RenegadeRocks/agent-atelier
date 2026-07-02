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

### 2026-07-02 — Authored /specs bundle caught up to PRD v4 (pre-build drift fix)  [handoff]
- **Assumption:** the specs/ bundle (authored 2026-06-30) matched the PRD.
- **Ground truth / reason:** the PRD's final v4 edit pass (review integration) postdated the
  bundle. Confirmed drift: (a) default-deny `policies.yaml` was missing the §16 tools
  `notify`, `handoff_export`, `instagram_caption_edit`, `instagram_delete` — they would have
  been BLOCKED at build; (b) `brand_kit.template.yaml` + `brand_kit.schema.json` were missing
  the §7.2 fields `max_queue_depth`, `owner_absence_pause_days`,
  `campaign_overrides_backpressure`, `approver_allowlist`, `delegation`, `posting_goal`,
  `weekly_capacity`, `cadence_source`, `quiet_days`, `blackout_dates`, `evergreen_rotation`,
  and the whole `notifications:` block — and the schema's top-level
  `additionalProperties:false` would have REJECTED any kit carrying them; the standing_week
  slot grammar lacked `quiet`/`format`/`channel`; (c) GEMINI.md/AGENTS.md §5 lacked the same
  three §16 tool rows.
- **Decision:** bundle catches up to the PRD (the PRD is the truth; nothing in the PRD
  changed). policies.yaml: tools added to the registry + env blocks (all three live-post/
  send tools blocked in preview) + ME/Ops role allowlists + act_rules (§14.4 checkpoint for
  post-publication corrections) + a new `notify_rules` block (§16.2: dedup/severity/rate-cap/
  audit — NOT a pre-send human gate, which would be circular). Template/schema: all fields
  added as optional-with-defaults (Appendix A stays valid unchanged — `brands/aol/` untouched).
- **Files touched (round 1):** `specs/policies.yaml`, `specs/brand_kit.template.yaml`,
  `specs/brand_kit.schema.json`, `GEMINI.md` §5, `AGENTS.md` §5.
- **Round 2 (same day — full sweep findings, all PRD-grounded):** policies.yaml gained the
  §14.2 continuation block (`claim_trigger_lexicon` exact list + `match_threshold: 90` pin +
  `high_stakes_tools` incl. owner-only `set_publish_mode` + `brand_kit_protected_fields`);
  template+schema gained the §7.2 intent block (`intent_statement`, `desired_feeling`,
  `primary_cta`, `cta_destination`, `off_brand_notes`), the 10-archetype `brand_type` enum,
  the `medium|high` quality-tier enum, `quiet|format|channel` in the slot grammar, and
  `reading_level` demoted to optional (Appendix A omits it); `brands/aol/brand_kit.yaml`
  gained its three `*_confirmed: true` safety flags (owner-confirmed rules, previously
  failing the schema's own fail-closed contract); `canon/content_ledger.md` re-grounded on
  the §17 status vocabulary + the §9.4 RESERVED-at-DRAFT concurrency rule (was contradicting
  both); `agents/managing-editor.md` gained the §15.1 three-disposition escalation protocol +
  the §9.5 Monday-tick compose rule (backpressure precondition + WeekPlan idempotency);
  `canon/cadence_plan.md` gained overlay modes/quiet/blackout/validator/staleness/§9.5;
  `agents/publishing-operations.md` gained the §12.3.1 Post Kit + §12.3.2 mark-as-posted
  discipline; `skills/weekly-digest` gained backpressure/Stale-Dated lines;
  `skills/intake-interview` gained the §7.1 two-probe first-light + FirstLightResult +
  dry-run; `resolver.md` gained invariants 7–8 (version pinning + mid-pipeline fail-closed);
  `tools/build_view_split.py` workflows now list pre-seeded artifacts for P2-A/P4-A
  (reconcile, don't duplicate), scope the standing linter/fail-closed gate note to P3+, and
  carry a subsection-discipline line.

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
