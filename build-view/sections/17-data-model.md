<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §17 (source lines 2189–2265). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 17. Data model

```yaml
# Core entities (storage: Sheets/Drive default, or DB)
Brand:            { id, brand_kit_ref, status, created_at }
BrandKit:         { brand_id, fields per §7.2, assets_ref, secrets_ref, version }
Offering:         { id, brand_id, name, one_liner, is_flagship, funnels_from?, brief_ref, dates?, status(active|paused|retired), retired_at? }   # id is immutable — budget (§13.2), memory (§8.1), cadence, and every LedgerRow are keyed by it; a retired id is never reused
CanonDoc:         { id, brand_id, key, title, body_template, owner_agent, version }   # incl. the frozen golden_set
Agent:            { id, brand_id, role, model_tier, allowed_tools, budget_monthly, status }
Task:             { id, brand_id, piece_id, parent_id?, goal_id?, offering_id?, title, language?, assignee_agent, status, blocked_by[],
                    lint_attempts, render_attempts, cd_render_rounds, reassign_count, owner_change_rounds }
                    # root piece-Task: id == piece_id; children via parent_id. Loop counters are harness-counted caps that bound the non-revise back-edges (§10.3) — every bounded back-edge other than the pre-render CD revise loop (`Review.round`, revise≤2): lint_attempts (draft↔ledger-lint, 2) · render_attempts (OCR-regenerate, 3) · cd_render_rounds (CD render-pass→Visual, 2) · reassign_count (§15.1) · owner_change_rounds (owner Request-changes loop, 2)
Draft:            { id, piece_id, task_id, attempt_no, brand_kit_version, language, idea_sentence, hook, shape, format, caption, hashtags,
                    visual_brief{message, feeling, treatment, image, words, light_mood, check}, compliance_block, claim_refs[] }
                    # attempt_no++ on a re-draft (same piece_id). claim_refs[] = the ClaimBankEntry ids this caption depends on — the explicit caption→claim edge that makes the §10.3 retirement cascade computable. brand_kit_version pinned at PLAN (§7.2.1)
Review:           { id, draft_id, gate0, gate1, render_pass, verdict, round, notes }
Asset:            { id, draft_id, kind(image|carousel_slide), prompt, provider, prediction_id, tier,
                    drive_url, byte_url?, alt_text, slide_no? }
LedgerRow:        { brand_id, date, piece_id, agent, channel_format, idea, hook, shape, visual_label, language, status, brand_kit_version }   # reaches status=Published only when the post is confirmed on BOTH paths (auto adapter / manual mark-as-posted, §12.3.2)
QueueItem:        { id, piece_id, status(Draft|CD Review|Approval Queue|Approved|Published|Archived),
                    exception?, rev, queued_at, owner_action?(Approve|Request changes|Reject|Mark posted),
                    brand_kit_version, language, channel, location_tag?, collaborator_handles?,
                    publish_method?(manual|auto), posted_at?, posted_permalink?, external_media_id?,
                    posted_unverified?, handoff_bundle_ref?, handoff_bundle_stale? }
                    # status = where in the pipeline (the 6-value lifecycle), derived & orchestrator-owned — the orchestrator is the SOLE writer (§12.2). exception = what is wrong, if anything, an orthogonal axis: {Escalated | Lint-Stuck | Render-Stuck | Publish-Failed | Stale-Dated | Safety-Blocked | Breaker-Paused | Run-Failed | Dep-Broken} (publish sub-status: Published-No-Comment). `Run-Failed` = crashed/orphaned run past the attempt cap (§13.2); `Dep-Broken` = a cyclic or dead `blocked_by` edge (§13.2). owner_action is the ONLY human-writable field — the §12.2 Owner-Action model; "Mark posted" is an owner_action value, never a direct Status write. queued_at drives approval-queue aging (§8.2/§12.4). posted_* / external_media_id / handoff_bundle_* carry the publish outcome (manual RECORD proof = posted_permalink+posted_at+publish_method, §12.3.2; external_media_id = the auto path).
ClaimBankEntry:   { id, brand_id, status(PENDING|VERIFIED|RETIRED), locked_sentence, source_url, source_hash, accessed_at, reverify_at }
Run:              { id, piece_id?, agent_id, task_id, status, total_tokens, iterations, cost, trace_ref,
                    lease_until, heartbeat_at, attempt, parent_run_id?, error_class?, error_verbatim?,
                    brand_kit_version, canon_snapshot_ref, judge_model_id?, rubric_version?, environment,
                    agbom[], intent_drift_flag }
                    # total_tokens+iterations → the run-level circuit-breaker (§13.2). lease_until/heartbeat_at/attempt/parent_run_id/error_class/error_verbatim → crashed-run detection & at-least-once re-dispatch (§13.2); error_verbatim is the captured provider error (no silent swap, §14.3). brand_kit_version/canon_snapshot_ref/judge_model_id/rubric_version/environment make Replay (§12.4), trajectory eval (§15.2) and the §15.3 audit reproducible — an unknown brand_kit_version FAILS CLOSED (route to owner). agbom[] = the tools / model-tier / data-sources the run actually touched (Runtime Agent Bill of Materials, surfaced per node on the floor, §12.4). intent_drift_flag = a SOFT trajectory-divergence signal (§14.5 blue-team baseline) that feeds trust decay (§12.3) — the breaker stays the hard backstop.
AuditEntry:       { id, action, actor_agent, approver_human?, operator_id?, target, environment, incident_of?, timestamp }   # append-only / write-once
                    # target is a TYPED ref — "<piece_id>#<stage>" for pipeline actions, a BrandKitRevision id for config saves (§7.7), or "<brand_id>#week:<week_of>" for scheduler/brand-level actions (e.g. the §9.5 backpressure pause). approver_human? is backed by the concrete operator_id (the accountable human; on the Sheets surface, the editing Google account, §12.4). incident_of? links a correction/retraction back to the original publish (§14.3). environment stamps the run context for reproducibility.
```

Notes: `Draft` carries `visual_brief` (mandatory message/feeling/treatment) and **does not** carry `alt_text` (authored on `Asset` in VISUALIZE). `Task.offering_id` carries per-offering routing/budget/memory keying. `Run` tracks `total_tokens` + `iterations` for the circuit-breaker.

**Piece identity & the ID-lineage spine (Day-5 Spec-Driven Development — pin the join key so regenerated code joins consistently).** `piece_id` is **minted once, by the Managing Editor at PLAN**, and carried unchanged through DRAFT→…→RECORD — an opaque, URL-safe, immutable string (shape `<brand_id>-<yyyymmdd>-<slot>-<6char>`; **matched, never parsed**). It is the **only** cross-entity join key: the root piece-`Task` has `id == piece_id` (children via `parent_id`); `Draft`, `Run`, `LedgerRow` and `QueueItem` carry it; `Review`/`Asset` reach it via `draft_id`; `AuditEntry.target` is the typed `"<piece_id>#<stage>"`. `QueueItem.id` stays a surrogate — `QueueItem.piece_id`/`LedgerRow.piece_id` are the join. A **re-draft keeps the original `piece_id`** (a new `Draft` row, `attempt_no++`, same piece) so ledger, audit, trust (§12.3) and Replay (§12.4) stay single-threaded.

**Idempotency is ONE hierarchy, not three.** The §12.2 published-registry tab keyed by `piece_id` is canonical; the §13.2 per-action key `(piece_id, stage, attempt-input-hash)` and the §12.3 per-step sub-keys `<piece_id>#post` / `<piece_id>#comment` are sub-scopes of it.

The recovery/handoff/observability and approval/governance entities other clusters reference are defined **here, once** (storage: Sheets/Drive default, or DB):

```yaml
# Recovery / handoff / notification / trace entities (§12.3–§14.5)
HandoffBundle: { id, piece_id, brand_id, channel, slide_count, folder_url, qr_url?,
                 caption_block, first_comment_block, alt_texts[]{slide_no, text},
                 location_todo?, collaborator_todo?, checklist[],
                 source_draft_version, minted_at, link_expires_at?, stale }   # the manual Post Kit record (§12.3.1); source_draft_version makes stale-detection deterministic (§12.3.2)
Notification:  { id, brand_id, severity(critical|action|digest|ambient), event_type, dedup_key,
                 piece_id?, run_id?, recipients[], channel,
                 state(open|sent|failed|coalesced|suppressed_quiet_hours|acknowledged|snoozed|muted|resolved),
                 recurrences, created_at, last_sent_at?, next_reminder_at?, snooze_until?,
                 acknowledged_by?, acknowledged_at?, resolved_at?, audit_ref }   # dedup_key collapses poll re-detections; first ack among recipients[] → resolved and cancels siblings (§14.4.1)
Span:          { id, run_id, parent_span_id?, kind(session|think|tool), name, tool?, status,
                 start_ts, end_ts, tokens?, redacted, summary }   # §14.5 trace unit; tool args/results stored redacted (§14.6). Run.trace_ref resolves to the Span tree
StudioEvent:   { seq, event_id, brand_id, ts, piece_id?, run_id?, stage?,
                 actor(agent_role|human|system), operator_id?, verb, detail, span_ref?, severity(info|needs_you|alert) }   # the ordered feed/graph stream (§12.4); monotonic seq + stable event_id let a client replay from its last seq
# Approval & governance entities (§12.5 / §9.5) — the §17-canonical definitions other clusters only REFERENCE
Operator:      { id, brand_id, display_name, google_account?, role(owner|delegate), approver, created_at }   # the accountable human on AuditEntry.operator_id
Correction:    { id, piece_id, operator_id, field(caption|hashtags|alt_text),
                 before, after, edit_class(cosmetic|substantive), regate_result(pass|fail), created_at }   # approve-with-edits diff; substantive corrections feed §15.3 false-approve calibration + the golden set
CampaignPlan:  { id, brand_id, name, type(launch|promo|seasonal|collab|ugc|other), offering_id?,
                 starts_on, ends_on, overlay_mode(add|replace|boost), max_posts_per_week_override?,
                 slots[], status(Draft|Approved|Active|Done|Archived), created_at }   # time-boxed overlay on the standing week (§9.5)
ApprovalAction: { id, piece_id, operator_id, verb(approve|approve_with_edits|request_changes|reject|mark_posted),
                  note?, reject_reason?, route_to?(content|visual|cd), slide_actions?, rev_seen,
                  result(recorded|superseded|refused_regate), created_at }   # the audited record every §12.5 owner verb produces
Delegation:     { id, brand_id, delegate_operator_id, scope(approve|request_changes_only|publish),
                  expires_at, granted_by }   # scoped, expiring approval authority (§12.5)
WeekPlan:       { id, brand_id, week_of, task_ids[], composed_at }   # the §9.5 Monday-tick idempotency record (one per brand_id × week_of)
```

Notes: `Span` and `StudioEvent` are a **denormalized projection of** the audit (§14.5) + Sheets SoR (§12.2) and **never override them** — on disagreement the `QueueItem` status wins. `Operator`/`Correction`/`CampaignPlan`/`ApprovalAction`/`Delegation`/`WeekPlan` are defined here once and referenced by §12.5 (approvals) and §9.5 (cadence). There is **no** separate `CadenceSlot` entity — a cadence slot is a `standing_week` entry (§7.2) materialized into a `Task` (§9.5). The onboarding-lifecycle entities `IngestionSource`, `IntakeSession`, `FirstLightResult` (defined inline in §7.1) and `BrandTemplate` (defined inline in §7.8), plus `BrandKitRevision` (defined in §7.7, the post-onboarding edit lifecycle), live outside §17 by design; `AuditEntry.target` may reference `BrandKitRevision`.

---

