<!-- DERIVED build-view file — do NOT hand-edit. Regenerate with `python3 tools/build_view_split.py`. Source of truth: specs/PRD-Agentic-Content-Studio.md -->

# build-view/core.md — the always-load build core

> Load THIS file for **every** contract, alongside `GEMINI.md`/`AGENTS.md` (which Antigravity always loads) and the contract's own READ-SCOPE files. It is the shared vocabulary — orientation, the goals/metrics bar, the conceptual model, and the data-model / `piece_id` spine. Nothing else is global; everything else loads per contract.

> Core = §0, §3, §5, §17. Each also exists individually in `build-view/sections/`.

---

## PRD preamble

# Agent Atelier — PRD (Agentic Social-Content Studio, Product-Agnostic)

**Product name:** Agent Atelier · **Target build platform:** Google Antigravity (Gemini 3 + ADK)
**Document type:** Product Requirements Document + Spec-Driven Development blueprint
**Status:** Draft **v4** for build · **Date:** 2026-06-30 · **Author:** Satbir (satsin20@gmail.com)
**Context:** Capstone project for the Kaggle 5-Day "Vibe Coding" AI Agents course

> **Revision note (v2).** This version incorporates a structured 8-lens adversarial review (fidelity to the real system, course-concept correctness, internal consistency/buildability, plus skeptic / scientist / researcher / marketer / AI-expert personas). 53 confirmed findings, applied as 54 edits; 9 were blockers (safety fail-open, the auto-publish byte-serving gap, deterministic claim-grounding, the read/draft/act ladder, the unmodeled visual-brief handoff, per-piece language, the ledger linter, the circuit-breaker re-spec, and measurable escape-rate metrics). Changes are woven into the relevant sections.
>
> **Revision note (v3 → v4).** Two additive changes: **(a)** the build is now governed by the **BUNNY build-governance harness** — the §18 build plan and §19 roadmap are merged into one gated, contract-driven sequence (the eleven 10-field prompt-contracts P0–P6 in §19.1), with validator/executor/authorizer separation, lock-and-proceed, conscious-deviation logging, and ON-FAIL fallbacks named in **§18.4**; a **§21 Capstone submission** section folds in the Kaggle writeup skeleton + checklist. **(b)** A new **§12.4 Studio Floor UI** specifies the live agent-company console — a visual graph of the eight agents and their handoffs/review-loops, a real-time activity feed, stuck/loop/breaker detection with a "Floor Actions" intervention set, a trust ladder, and dark/light theming — so the system is observable, participatory, and never a dead form. Full scope preserved; nothing removed. **(v4 — review integration):** Phases 1/2/4/5 are each split into two gated contracts → **eleven** prompt-contracts (§19.1), each with a READ-SCOPE preamble; **durable cross-run memory** is Resolved as Sheets-keyed (§8.1/§20); a **§9.5 queue-backpressure** rule and an explicit **§15.1 "dead"-indicator** rubric were added; the Review app (§12.1) was fleshed out. Still additive; nothing removed.
>
> **Revision note (v4) — the foolproofing pass.** A multi-agent adversarial audit (8 robustness dimensions + a course-technique-maximization pass grounded in the Day 1–5 whitepapers) surfaced **22 blocker / 51 major / 28 minor** gaps, closed as **82 additive, cross-checked edits** honoring one canonical data model and 12 consistency rules. Headlines: a `piece_id` data-model spine + a declared `exception`/recovery axis (§17); crashed-run **leases + heartbeats** and per-action **idempotency** (§13.2); the round-3 **escalation resolution** (§15.1); the **notification & escalation model** + **dead-man's switch** (§14.4.1, §14.5); **human-edit re-gating**, the **Owner-Action model**, and the **cross-surface approval protocol** (§12.2, §12.5); the manual **Post-Kit** export + **mark-as-posted** (§12.3.1–2); **post-publication take-down/correction** (§14.3); a deepened, honest **Studio Floor** (§12.4); and the full **brand-intake / Cadence Studio / brand-editing / onboarding-at-scale** lifecycle (§7.1–§7.8, §9.5). New course-technique sections: **untrusted-content / Confused-Deputy** (§14.7), **Red/Blue/Green** adversarial eval (§15.4), **MCP + `notify` contracts** (§16.1–2), a **sample Agent Card** (§13.3), and the dynamic **"Examples"** context type (§5.3). Every change additive; full scope preserved.

---

## 0. How to read this spec

This document is written as a **spec-driven development (SDD)** artifact, following Day 5 of the course ("Spec-Driven Production-Grade Development"). The spec — not the code — is the **Architectural North Star** and the source of truth. The implementing agent (Antigravity / Gemini CLI / ADK) should treat this as the `/specs` root and regenerate code from it; the code is disposable, the spec is durable.

Per the course's Gemini-optimal formatting guidance, this spec uses a **hybrid Markdown + conditional YAML** style:

- **Markdown** carries narrative, intent, and "the why."
- **YAML blocks** carry structured configuration and schemas (kept flat, nesting ≤ 3, to avoid the reasoning "format tax").
- **Gherkin (`Scenario / Given / When / Then`)** carries acceptance behaviour, so the builder implements behaviour, not vibes.

**Build posture for the implementing agent:** Architect mode, **no YOLO**. Propose the folder structure and tech stack first for confirmation; generate tests, docs, and logging alongside features. **Model and library versions are deliberately deferred to build time** (see §14.3, §18.1): pin every library/model version then, and verify the *current* Gemini / ADK / image-model (Nano Banana / Imagen) / Instagram Graph API identifiers and limits against live docs before using them — do not trust the training cutoff.

---

## 3. Goals, non-goals, success metrics

### 3.1 Goals

- **G1 — Product-agnostic.** Stand up a fully working content studio for a brand-new product by supplying only a Brand Kit, with **zero changes to agent code or engine docs**.
- **G2 — Faithful reproduction.** Reproduce the AOL engine's agent roster, pipeline, craft rules, and governance — generalized, not weakened.
- **G3 — Intuitive onboarding.** Capture a brand through a guided, conversational intake (not a dead form) that a non-technical owner can complete, producing a valid Brand Kit.
- **G4 — Human-in-the-loop by default, autonomous-capable.** Default to a human approval gate; allow per-brand opt-in to auto-publish once trusted.
- **G5 — Google-native, simple.** Prefer Google tools (Gemini, Nano Banana / Imagen, Drive, Sheets, ADK, Agent Engine) and keep the stack as simple as the job allows; pluggable where a non-Google option is genuinely better (e.g., Replicate image models).
- **G6 — Governed & evaluated.** Every shipped piece passes safety/compliance gating and an automated quality evaluation before reaching a human.

### 3.2 Non-goals (YAGNI)

- Not rebuilding Paperclip's full multi-company SaaS control plane. Agent Atelier needs a *minimal* orchestration layer, not a generic agent-business platform.
- Not building a general social-media scheduler/analytics suite. Publishing is a thin, optional last step.
- Not auto-running paid ad campaigns or handling payments/commerce (this also rules out Instagram Shopping product tags).
- Not multi-language NLG research; channel/locale language is a Brand Kit field, not an R&D problem.
- Not a public marketplace of agents. Single-owner, possibly multi-brand, deployment.
- **Static assets only (v1).** The studio produces single images, carousels, and static 9:16 covers via the Caption-Composer; it **writes Reel scripts** (§9.1) but does **not** generate motion video, and does **not** produce interactive Stories (polls/stickers/link stickers). This is a known reach/discovery ceiling. Image-to-motion/b-roll Reels and interactive Stories are explicit out-of-scope (future) items — cross-referenced from §9.2 and §11.
- **No participant/cohort messaging.** Private/cohort messaging (WhatsApp/Telegram broadcasts, email/LMS sequences) is out of scope. Where an offering has "in-program" or "retention" phases (§8.2), these are content-emphasis/timing **modes delivered through the same feed pipeline**, not a separate delivery system or channel type.

### 3.3 Success metrics

Two kinds of targets: **hard `=0`** only where a deterministic structural check makes it observable, and **measured escape rates with confidence intervals** where the only honest measurement is an independent audit (because a `=0` "escapes" claim measured by the same gate that produced the content is unfalsifiable — see §15.3 for the independent post-publication audit that produces these numbers).

| Metric | Target |
|---|---|
| Time to first on-brand draft for a new brand | < 1 hour from completed intake |
| Brand-specific **code/engine-doc** changes to onboard a new brand | 0 (hard; structural) |
| Posts shipped to the approval queue per week, at quality bar | meets the brand's configured cadence |
| Countable rotation-rule violations reaching a human (all linter-checked rules: hook, shape, aphorism 1-in-5 cap, idea-rerun, visual-treatment-label, research-min) | 0 (hard; enforced by the deterministic ledger-linter, §9.4) |
| "Repetition reaching a human" — semantic/visual sameness | measured escape rate (north-star 0), via §15.3 audit |
| Factually unverifiable claims published | measured escape rate **< 2%** (95% CI), north-star 0; deterministic claim-grounding (§14.2) makes numeric overclaims structurally `=0` |
| Safety / non-disclosure violations published | measured escape rate **< 1%** (95% CI), north-star 0 |
| Runaway-cost incidents (circuit-breaker fired but loop not contained) | 0 (hard; structural) |
| **Creative-Director ↔ owner agreement rate** (judge calibration) | tracked; false-approve rate (CD-approved → owner-edited/rejected) trending down. Computed in §15.3, surfaced in the Friday digest (§14.5) and monthly retro; **this is the explicit trust signal gating `auto_after_trust → auto`** (§12.3) |
| Owner edits per approved piece | trending down quarterly (directional, not an SLA; baseline = current AOL system's first weeks). Optional one-word edit tag (cosmetic / substantive / rejection) on the Review row |

| **Approved pieces that actually reach Published** (manual path) | tracked; approved-but-unposted **aging** surfaced in the Friday digest (§8.2) and the §12.4 tray; north-star: no piece stranded > one cadence cycle |
| **Approve → posted latency** (manual) | tracked, directional — the last-mile of "can the owner actually post" |
| Cadence slot counted as hit | only at **post time** (mark-as-posted, §12.3.2), never at approval |
| **Time-to-owner for a CRITICAL alert** (breaker / fail-closed / adapter-down / no-heartbeat) | reaches the owner within one tick + one send attempt; **0 CRITICAL conditions undetected beyond the dead-man's-switch grace window** (hard; structural, §14.4.1/§14.5) |
| **Out-of-band sends per owner-day** | within the configured rate cap; trending toward the batched ideal (approval-fatigue guard) |

---

## 5. Conceptual model

### 5.1 Agent = Model + Harness (Day 1)

Agent Atelier is built on the course's central equation: **a raw model is not an agent; it becomes one when wrapped in a harness** — instructions/rule files, tools (MCP), sandboxes, orchestration logic, guardrails/hooks, memory, and observability. ~10% of behaviour is the model; ~90% is the harness. **Almost all of Agent Atelier's value and almost all of this spec is harness**: the canon documents, the per-agent instructions, the pipeline, the gates, the budgets. The model underneath (Gemini) is swappable.

### 5.2 The factory model (Day 1)

The owner's output is **not posts** — it is **the system that produces posts**. The owner (and the Managing Editor agent) operate the factory: define specs (the Brand Kit + canon), design guardrails, review/approve output. The agent "factory floor" plans → drafts → illustrates → verifies, looping failures back. This framing drives the whole architecture: invest in the harness, give agents *success criteria* (the quality bar) not keystroke instructions.

### 5.3 Context engineering: static vs dynamic (Day 1)

The studio's "knowledge" is engineered as six context types — **instructions, knowledge, memory, examples, tools, guardrails** — split into:

- **Static context** (always loaded, expensive): each agent's identity/instructions (`AGENTS.md`-style), the brand's voice/safety rules, persona.
- **Dynamic context** (loaded on demand, cheap): the relevant engine doc section, the relevant Offering Brief, a skill's body, a research entry — pulled per task via **progressive disclosure** (Day 3) so a hundred capabilities cost only their metadata until triggered.

This separation is *how* Agent Atelier stays product-agnostic and token-efficient: the static layer is generic engine + brand identity; the brand specifics are dynamic, retrieved from the Brand Kit and canon store as needed.

**The sixth context type — *Examples* (dynamic few-shot) (Day 1).** Of the six types (instructions · knowledge · memory · **examples** · tools · guardrails), *examples* is the one not to leave static. The Brand Kit's `sample_lines_good/bad` seed a *fixed* few-shot, but the studio accumulates the highest-signal corpus there is: **owner-approved (and owner-edited) published pieces.** At **IDEATE+DRAFT** a content agent retrieves a small, *dynamically selected* few-shot set — the K most-recent owner-approved pieces for this **track/offering/language**, plus 1–2 owner-*edited* pairs (draft → owner's edit) as "do-it-this-way" demonstrations — loaded as dynamic context. This makes the §15.3 improvement loop a **context-engineering loop**: approvals re-seed the writers, not just calibrate the judge. Selection reuses the Content Ledger + corrections log (§8.1/§9.4) — **no vector store** (recency + track/offering/language keys), consistent with §8.3's "Knowledge = keyed Sheets/Drive access, no semantic index."

### 5.4 Conductor and orchestrator (Day 1)

The human moves between **conductor** (real-time: "write me a post about X", approving a draft) and **orchestrator** (async: let the weekly routine run, check the queue later). The **Managing Editor agent** is itself an orchestrator over the other agents. Agent Atelier must support both human modes and the agent-orchestration mode.

---

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

