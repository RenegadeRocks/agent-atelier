<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §12 (source lines 1237–1733). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 12. Review, approval, publishing & system-of-record

### 12.1 Built-in Review interface (richer in-product surface, Phase 5)

The **Agent Atelier Review app** is a committed **Phase-5** deliverable — a rich view over the *same* audit trail as the Sheets gate (not part of the minimal set). It exists so an owner can review and act on a piece without touching a spreadsheet, at full parity with the Sheets gate and the §12.5 approval protocol.

**Two surfaces.**
- **Queue list** — one card per pending piece: thumbnail (cover slide for carousels), title, channel, track/offering it funnels to, language, age-in-queue, and a status/exception badge (§17). Sort by age; filter by channel / offering / status; bulk-select for batch approve.
- **Piece detail** — the rendered image(s)/carousel *in order*, the final caption (copy button), first-comment hashtags (copy button), per-slide alt text, the offering link, the CD note + round, and the resolved compliance block (claims + their VERIFIED sources, §14.2). For carousels each slide is individually viewable and, where the protocol allows, individually actionable (partial-carousel approval, §12.5).

**Actions — the §12.5 verb set, at parity with the Sheets `Owner Action` cell.** **Approve · Request changes** (a `route_to` target + note) **· Approve with edits** (inline caption edit → recorded as a `Correction`, feeds the golden set §15.3) **· Reject** (validated `reject_reason`, §15.3 taxonomy) **· Publish / Mark-posted** (the single manual close-the-loop verb, with permalink, §12.3.2). Every action writes the **same append-only audit trail** as the Sheets gate and is read as the same approval signal — the Review app never becomes a second source of truth.

**Invariants.** Human edits **re-run the deterministic gates** (ledger-lint + publish-time Policy Server, §14.2) before the edited piece can ship — the app cannot bypass an invariant the model can't (§12.2/§12.5). Malformed or again-failing input **fails closed**. Actions are **idempotent by `piece_id`** (no double-publish across the Sheets poller and the app).

**Ergonomics.** Mobile-first (the common approval path is a phone); one-tap copy for caption/hashtags; keyboard shortcuts (approve / next / request-changes); explicit **empty · loading · error · offline** states; WCAG AA. Approve-with-edits and batch approve exist to minimise decisions-per-piece (approval-fatigue, Day 5, §14.4).

The **Studio Floor UI (§12.4)** is the live operator console that *deepens* this surface — the live agent graph, the activity feed, stuck-task detection + intervention, and the trust panel. The Review app is the focused **approve/act** view; the Studio Floor is the live **company** view; both act through the one §12.5 protocol. *(Optional: generate either with A2UI / Generative UI, Day 2.)*

### 12.2 Google Sheets/Drive — the MVP/default human gate and system of record

The **system of record is Google Sheets + Drive**: a Calendar/Queue sheet holds one row per piece (Title, Date, Channel, Track/Offering, Status, Owner-Agent, Visual-Status, Language, Phase, Caption, Image links (Drive), Alt text, CD round, Approval notes, Piece id, timestamps, optional geotag/collaborators); assets live in Drive. The owner approves **asynchronously via a human-only `Owner Action` cell** — never by writing the orchestrator-derived `Status` cell (the normative workbook layout and this supersession are pinned below) — from anywhere; Agent Atelier watches the sheet and proceeds. The Sheets gate is the MVP/default; the Review app (§12.1) is the later rich view.

**Integrity discipline (Sheets as SoR):**
- The human-editable Calendar/Queue sheet is **not** the audit trail. `AuditEntry` is a **separate append-only, write-once log** (a protected Sheet/tab, or AuditEntry-in-DB).
- The orchestrator/Agent Atelier is the **sole writer of derived status**; the owner's **Owner-Action** edit (the dropdown defined below) is read as an *approval signal*, never a competing write to `Status`.
- All ledger/Claim-Bank/audit writes use **atomic append** and are **append-only**.
- **Publish is idempotent** via a publish-once guard keyed by `piece_id` (closes the polling double-publish race).
- The documented DB + object-store option is the recommended migration past single-process / single-brand / low-cadence.

**Normative workbook layout + the owner-action column.** One workbook per brand (isolation, §17): named tabs `Queue`, `Ledger`, `ClaimBank`, `Reservations`, `Budgets`, a **protected** `Audit` tab, a canonical **`published`** registry tab (below), and a pinned **`ALERTS`** row (§14.4.1 fallback).
- **Two distinct status columns, never one.** `Status` is **orchestrator-owned, derived** (the QueueItem enum, §17). `Owner Action` is **the only human-writable decision cell** — a Data-Validation dropdown `{ Approve | Request changes | Reject | Mark posted | (blank) }`. This **supersedes "owner sets the Status cell"** everywhere in the PRD (§12.2 head, the §12.3 async Gherkin, §10.2, §12.4): the owner never writes `Status`; the orchestrator never overwrites `Owner Action`.
- **Posted-state columns** (written at mark-as-posted, §12.3.2): **Publish method (manual|auto), Posted at, Permalink.** `Mark posted` *requires* a Permalink or an explicit `posted_unverified` flag.
- **Approval-protocol columns (§12.5):** `route_to` (Request-changes target), `reject_reason` (validated dropdown, §15.3 taxonomy), and `slide_actions` (partial-carousel action) — so the Sheets surface expresses the full §12.5 verb set at parity.
- **Malformed input fails closed** — a value outside the dropdown is ignored and flagged, never guessed.
- **Poll cadence is config** — `poll_interval_seconds` (default 60); the poller debounces on `(piece_id, Owner Action, rev)`.

```gherkin
Scenario: A garbled approval is never interpreted as approval
  Given the owner types "Aproved" into the Owner Action cell
  Then the value is rejected as out-of-enum, the piece stays in Approval Queue, and the owner is flagged
```

**Concurrency & idempotency on Sheets (Sheets has no transactions — pin the mechanism).**
- **Single serialized writer.** The orchestrator tick is the *sole* writer of derived state and **ticks do not overlap** (a tick-in-progress lease makes a second Cloud Scheduler fire no-op); every derived write happens in this single-threaded section — that is what *makes* them atomic.
- **Append via `spreadsheets.values.append` with `insertDataOption=INSERT_ROWS`** — never a computed-row `update`.
- **The canonical idempotency store is the `published` registry tab**, one row per `piece_id`, check-then-append inside the serialized writer. The per-action key of §13.2 `(piece_id, stage, attempt-input-hash)` and the per-step `#post`/`#comment` sub-keys of §12.3 are **sub-scopes of this one registry**, not separate schemes.
- **Optimistic concurrency.** Every Queue row carries `rev` (monotonic) + `updated_at`; a write verifies `rev` unchanged, then writes `rev+1` and re-reads. **Two concurrent human signals** on one piece (console Approve vs Sheets Reject) resolve **first-committed-wins**; the stale write is rejected and re-surfaced to its actor with current state; both land in audit (see §12.5 multi-operator guards).
- **Migrate to the DB + object-store option** past one process / one brand / higher cadence.

```gherkin
Scenario: Publish-once holds under overlapping ticks
  Given a piece already in the `published` registry tab
  When a second Cloud Scheduler fire begins before the prior tick released its lease
  Then the second fire no-ops on the lease, and even if it ran the registry check skips the piece_id
  And no second Instagram post is created
```

**Human edits never bypass the deterministic gates.** An owner edit at the gate — a changed Caption cell, or an `Edit task` on the floor (§12.4) — is an *approval signal for the edited content*, **not** a waiver. Any edit touching publishable fields (caption, claim text, image, alt text, asset URL) **re-runs the deterministic Policy Server gates before publish in both manual and auto modes**: the deterministic ledger-lint (§9.4, on text edits), claim-grounding vs VERIFIED `locked_sentence`s, the fail-closed safety-field check (`claims_forbidden`/`non_disclosure_rules`/`required_framing`), and the byte-serving rule (§14.2/§12.3). A human-introduced unverified statistic or non-disclosure leak is blocked exactly as an agent's, logged with `actor=human`, and routed back with the reason. *(The publish-time LLM referee stays auto-mode-only per §14.2; the deterministic floor binds every path, manual included. The re-gate mechanics and the `Correction` record are specified in §12.5.)*

```gherkin
Scenario: A human-edited unverified claim is blocked on the manual path
  Given approval_mode is "human" and the owner edits the Caption to add a statistic with no VERIFIED locked_sentence
  When manual publish is attempted
  Then the deterministic claim-grounding gate blocks publish (actor=human logged) and routes it back with the reason
```

### 12.3 Publishing

- **Default human-in-the-loop.** Approved → owner publishes (frictionless handoff bundle).
- **Optional auto-publish (per brand), with explicit precedence.** Auto-publish occurs **only when** `auto_publish_enabled == true` **AND** `approval_mode` is `auto` (or `auto_after_trust` with `trust_threshold` met) **AND** all gates pass **AND** a publish adapter exists for the channel; otherwise the piece is queued for manual handoff. `auto_publish_enabled` is a **master kill-switch**.
- **Trust threshold (concrete).** `auto_after_trust` is governed by the Brand Kit `trust_threshold` block (§7.2). The window **resets to 0 only on shipped defects** (owner reject / substantive owner edit of a CD-approved piece, a post-publish policy violation, or a §15.3 audit escape) — **routine CD `reject`/`revise` verdicts do not reset it**; the full reset/decay feeder list is pinned in the disambiguation below. Meeting the threshold only **surfaces a recommendation** to enable auto-publish — it **never silently flips** `approval_mode`/`auto_publish_enabled`, which remains a §14.4 high-stakes action requiring owner sign-off via the **Vibe-Diff** checkpoint.

- **Disambiguate the trust-window reset (a CD reject is the system working, not a trust failure).** The `auto_after_trust` window is the single feeder-listed signal; it **resets to 0 only on** (a) a **post-publish Policy-Server violation**, (b) an **owner Reject or owner substantive Edit** of a CD-approved piece (a false-approve, §12.5), or (c) a **§15.3 audit escape**. It additionally **decays** on an unresolved §15.4 red-team escape, an §17 `intent_drift_flag`, and a **safety same-class freeze** (§14.3); editing `trust_threshold` resets it to 0 (§14.4). **Routine CD `reject`/`revise` verdicts do not reset the window** — they are the gate functioning and the gated piece never shipped. A **Request-changes at the human gate likewise does not reset it** (§12.5). This is the one canonical statement of the reset/decay feeders; it supersedes the literal reading of the §10.3 scenario.

```gherkin
Scenario: A normal CD reject does not reset the trust window
  Given approval_mode auto_after_trust accumulating toward trust_threshold
  When the Creative Director rejects a draft pre-publish (the gate working)
  Then the trust window is unchanged
  But an owner reject / substantive-edit of a CD-approved piece, or a post-publish policy violation, resets it to 0
```
- **Instagram Platform content-publishing API constraints (auto-publish path only; manual handoff unaffected).** Drive remains the studio-hosted record, but for auto-publish the asset must be retrievable as **raw `image/*` bytes from a Google-native public/signed URL** (a public/signed GCS object, or a Drive direct-download byte-serving endpoint) — **not** a Drive viewer page; a pre-publish check asserts the URL returns HTTP 200 with `image/*` content-type. **Prerequisite (verify at build time):** a **Business/Creator account** in all cases; a **linked Facebook Page only on the legacy Facebook-Login path** — prefer the newer **Instagram-Login API path, which needs no linked Page**. Add a **publish-then-comment** step that posts the first-comment hashtags the handoff bundle already produced. Auto-published **carousels respect the platform's current carousel max — confirm at build time** (~20 in-app; the publishing API historically capped children at 10); note the account-level **~50 posts/24h** publishing limit (comfortably above this product's cadence). Reels/Stories auto-publish is **out of launch** (feed single-image + carousel only). (Per-channel rate-cap queue engineering is out of scope at this volume.)
- **Image URL integrity rule (generalized).** The published asset must be a studio-hosted (Drive/GCS) URL satisfying the byte-serving rule above — never a raw provider URL or internal path — a hard check before any publish.
- **Channels.** Instagram is the only publish adapter at launch; other configured channels (e.g. Facebook) are manual-only until an adapter is registered. No per-channel publish MCP tools are added now.

**Publish error handling (the two-phase API's failure modes).** Publishing is two-phase (create container → publish container) plus publish-then-comment; each phase fails independently. The `instagram_publish` adapter classifies and recovers deterministically (the publish-once registry keyed by `piece_id`, §12.2, underwrites all of it):
- **Transient** (429/5xx/timeout/container-not-ready) → bounded exponential backoff (cap N). On exhaustion: `exception=Publish-Failed`, **leave `status=Approved` (never Published)**, raise an **urgent** owner alert (§14.4.1). Never silent.
- **Permanent** (invalid media, Meta policy, expired/insufficient token, restriction) → **no retry**; capture the verbatim error to `Run.error_verbatim`, set `exception=Publish-Failed`, route to owner (the §14.3 capture-verbatim-stop-escalate discipline for the irreversible act).
- **Ambiguous (timed out, success unknown)** → **reconcile before retry**: query recent media for this `piece_id`'s container/marker and publish **only if absent** — never a blind retry of an irreversible act.
- **Per-step idempotency sub-keys** in the registry: `"<piece_id>#post"` and `"<piece_id>#comment"` (sub-scopes of the §12.2 store). A **partial — post up, comment failed** → the piece is `Published`, `exception` shows the **Published-No-Comment** sub-status, and the comment is retried *independently* (comment-only, never re-posting the image); a still-failing comment is a non-blocking warning.
- **The first-comment hashtag text passes the same publish-time Policy Server check as the caption** (§14.2) — hashtags are words; non-disclosure binds words.

```gherkin
Scenario: A timed-out publish is reconciled, not double-posted
  Given an instagram_publish call times out with success unknown
  Then the adapter queries recent media for the piece_id marker before any retry, publishing only if absent

Scenario: Comment failure does not double-post and does not skip the gate
  Given a post published but its first-comment failed, when the next tick runs
  Then only the comment is retried under "<piece_id>#comment" (no second image post) and the hashtag text is re-checked by the Policy Server first
```

```gherkin
Scenario: Async approval from Google Sheets
  Given the owner is away from the Review app
  And a piece is in the Approval Queue with status "Approval Queue"
  When the owner writes "Approve" into the row's Owner Action cell (§12.2; never the derived Status cell)
  Then Agent Atelier detects the change within the polling interval
  And (manual default) builds the handoff bundle, or (auto, if enabled + adapter) publishes once via the idempotency guard
  And records the approver and timestamp in the append-only audit trail
```

### 12.3.1 The Manual Handoff Bundle (the "Post Kit") — the default export path

> **Why.** Manual handoff is the *default*; auto-publish is the trust-gated exception. The owner posts from a **phone**; the studio runs on **Drive/desktop**. The Post Kit bridges that gap. Built by Publishing & Ops at QUEUE (§10.1), modelled as `HandoffBundle` (§17).

**A concrete artifact, not a description.** Per piece: a **channel-named Drive folder** `/<brand>/handoff/<piece_id>/` *and* an in-app **Post Kit view**, containing:
- **Image(s) as downloadable files**, one per slide, **zero-padded slide index** (`01.jpg`, `02.jpg`…) from `Asset.slide_no` (§17); single-image ships `01.jpg`.
- **Final caption** in the piece's language (§7.6), **copy-to-clipboard as one block**, UTF-8, emoji/Indic/RTL + curly-quote + line-break faithful; a **"first line will truncate behind '… more'"** warning if the hook exceeds the channel preview length.
- **First-comment hashtag block**, separately copyable (never merged into the caption).
- **Per-slide alt text**, each separately copyable, labelled by slide index, with a pointer to where it is pasted (IG → Advanced → alt text, per image).
- **A channel + format header**; **`location_tag`/`collaborator_handles` as in-app to-do instructions** (cannot be pre-pasted), with `@handle` validation.
- **A short ordered checklist** (upload 01–0N in order · paste caption · add per-slide alt text · publish · paste first-comment hashtags · return → **Mark as posted**).

**Platform limits are shown, and confirmed at build time.** The kit surfaces the live per-channel caps — caption ~2,200 chars, first-comment hashtags ~30, carousel ~20 slides, per-slide alt-text limit, and image file-size ceiling — as inline warnings; these numbers are the **same set enforced by the §14.2 platform-export gate** and both carry the **"confirm against live platform docs at build time (§0/§14.3)"** flag (rule 10). An over-limit piece bounces at Ops before it reaches the Approval Queue.

**Transport to the phone is first-class:** **(a) "Send to phone"** — a signed link via `notify` (§16) and/or a **QR code**; (b) open the Drive folder; (c) copy-each-element buttons.

**Channel-aware**, resolved per `channel` via `[[VARIABLE]]` (§7.2.1): IG = ordered images + caption + first-comment + per-slide alt; **Facebook** drops first-comment; **YouTube** carries title + description + thumbnail. A channel with no template **fails closed** to a generic "files + caption + alt text" kit and flags the gap.

**Signed-link lifetime must exceed approval latency:** because approvals batch with quiet-hours (§14.4), any signed link is **minted on open, not at build** (or lifetime ≥ the brand's max approve-to-post window); an expired link **regenerates on demand**.

**"Publish (if manual)" (§12.1/§12.4/§12.5) opens the Post Kit — it does not post for you** — then exposes **Mark as posted** (§12.3.2).

### 12.3.2 Closing the loop on the manual path — mark-as-posted, permalink & manual idempotency

**RECORD cannot fire on the manual path until the owner confirms the post.** Without confirmation the `QueueItem` is stranded at **Approved**, RECORD never runs, `LedgerRow.status` never reaches Published, the cadence digest (§8.2) is wrong, and the Gallery stays empty though the piece is live. The fix is one HITL action:
- **Mark as posted** (an `Owner Action` value per §12.2; also on the Review app / Studio Floor). Transitions **Approved → Published**, flips `LedgerRow.status`, runs RECORD (append-only `AuditEntry`, `actor=human`, `publish_method=manual`), counts the cadence slot **as hit at post time, not approval time**, and lifts the card to the Gallery.
- **Capture the permalink.** Optionally accepts the live URL (`posted_permalink`) and stores `posted_at`. If omitted, the piece is `posted_unverified` (still Published, flagged in the digest).
- **Manual idempotency.** A piece already Published shows "Posted on `<posted_at>`" and **disables re-publish**; re-opening the Post Kit warns before any fresh download (the manual analogue of the §12.2 publish-once guard).
- **Stale-bundle invalidation.** If caption/image/brief was edited after a kit was built (an `Edit task`, a post-approval Request-changes), the prior kit is **marked stale (`handoff_bundle_stale`) and regenerated** (`HandoffBundle.source_draft_version` mismatch) before posting.
- **Trust interplay.** The **approval** is the trust event (§12.3/§15.3), *not* mark-as-posted, so `trust_threshold` math is unaffected by where bytes were posted.

```gherkin
Scenario: Manual post closes the loop and records the permalink
  Given a piece is Approved and its Post Kit opened, approval_mode "human"
  When the owner posts and chooses "Mark as posted" with the live URL
  Then QueueItem moves Approved→Published, LedgerRow flips to Published, RECORD stores posted_permalink+posted_at (actor=human, publish_method=manual), the slot counts at post time, and the card lifts to the Gallery

Scenario: Manual double-post is prevented
  Given a piece already Published with a posted_at, when the owner re-opens the Post Kit or re-marks it
  Then the manual publish-once guard keyed by piece_id shows "Posted on <posted_at>" and disables re-publish
```

### 12.4 Studio Floor UI — the live agent-company console (Phase 5)

> **Why this exists.** When this PRD was first built in Antigravity, the generated front end was a *dead form*: the owner entered brand details, pressed submit, and then saw nothing — no sign of the eight agents, the handoffs, the reviews, or where a piece was. That opacity is the failure this section corrects. The **Studio Floor** is the live, visual console of the agent company: the owner watches the agents work, sees files and tasks pass between them, sees the Creative Director send work back, sees exactly where a piece is stuck — and can step in. It serves three goals, in this order: **confidence** (the owner *feels* a real company of specialists at work on their brand, not a black box), **troubleshooting** (nothing is opaque; every handoff, loop, and stall is inspectable down to the underlying span), and **participation** (the owner is a member of the company who can intervene mid-flight). It **deepens — does not replace — the §12.1 Review app**, is a *consumer* of the same `sheets`/`drive` MCP tools and the same append-only audit trail (§12.2, §14.5) rather than a new source of truth, and is delivered in **Phase 5** (§19). It draws on the proven Paperclip operator UI but adopts only its *approachable subset*, deliberately leaving out engineer-grade internals (see "Approachable by design" below) so a non-technical brand owner is never overwhelmed.

**Studio Floor — schematic (dark mode).**

```
═══ AGENT ATELIER · STUDIO FLOOR ═══════════════════════════════════════════
Brand: Art of Living — Ludhiana     Mode: (●) Conductor   ( ) Orchestrator   ☾/☀
Run budget ▓▓▓▓▓▓▓▓▓▓▓░░░ 68%    breaker: OK    2 in motion    ▲ 3 need you
════════════════════════════════════════════════════════════════════════════
RIGHT NOW ▸ Creative Director is reviewing "Breath & Stillness" (revise 2/2) — for YOU

THE FLOOR   [ Floor ▾ | Pipeline | Company ]
   Managing Editor ◆ orchestrating
        │ plan, assigns owner agent
        ▼
   Evergreen ● drafting ───draft───▶ Ledger Lint ⬢ ✓ (deterministic, pre-CD)
   Research ◈ idle  ┄┄ verified claim ┄┄▶ feeds the draft
        │
        ▼ review
   Creative Director ✶ reviewing      ↩ revise 2/2 ───▶ Evergreen   (round 3 → ME)
                                      ◀── render fail ── Visual Production
        │ approve
        ▼
   Visual Production ▣ rendering image + alt text ───▶ CD render pass ───▶ queue
        ▼
   Publishing & Ops ⬡ ──── gate ────▶  ★ YOUR DESK (Human Gate) ▲3
                                        publish ▶ record → ledger + audit

ACTIVITY   [ All ▾ ]   (Narrate ◉ / Detail)
   10:47 ⬡ Publishing & Ops  queued "Morning Light" → Approval Queue ▲ (waiting on you)
   10:46 ✶ Creative Director  render pass ✓ "visibly different" → Publishing & Ops
   10:41 ✶ Creative Director  APPROVED ✓ Scroll Test + Compliance — milestone, sealed
   10:37 ✶ Creative Director  sent it back ↩ revise 1/2: "hook repeats last 3 posts;
                              add one concrete detail"
   10:34 ▢ Evergreen Content  drafted "Breath & Stillness" (Hindi) — hook: question
   10:32 ◈ Research & Verif.  verified a claim → Claim Bank (locked sentence)

NEEDS YOU
   ① "Breath & Stillness" — REVIEW loop ↩ 2/2 ⚠      ② "Morning Light" — HUMAN GATE ▲ ready
TRUST ●●●●●●●●○○  8/10 approved · 0 edits · 0 violations    auto-publish OFF [ Vibe Diff ▸ ]

INTERVENE · "Breath & Stillness"
   what happened: Creative Director & Evergreen went back and forth twice (cap 2/2);
                  next round escalates to the Managing Editor.
   evidence: R1 "hook repeats last 3 posts" · R2 "warmer, add a concrete detail" · 41k tok
   [ Unstick & resume ] [ Edit task ✎ ] [ Re-route ⇄ ] [ Inject note ▸ ]
   [ Approve ✓ ] [ Reject ✕ ]    ·    raising budget → Vibe Diff · every action audited

Legend: ● working · ◆ orchestrating · ✶ reviewing · ⬢ deterministic gate · ↩ review loop
        ▣ rendering · ◈ research · ⬡ ops · ★ you · ▲ waiting on you · ┄ feeder rail
```

**The live agent graph (the floor).** The home screen is a live graph of the **eight agents as stations laid over the exact §10.1 pipeline**, with the **owner present as a ninth seat at the HUMAN GATE** ("Your desk" / the Showrunner's chair) so the gate is a visible handoff *to you*, not an off-screen form.
- **Stations = agents over stages**, verbatim to §10.1 and §8: PLAN (Managing Editor, the orchestrator — does no IC work), IDEATE+DRAFT (Evergreen Content / Offering Content; Research & Verification feeds a VERIFIED claim in on a dotted feeder rail), LEDGER LINT (Publishing & Operations — drawn as a deterministic gate/diamond, *distinct from* CD judgment per §9.4), REVIEW (Creative Director — Gate 0 Scroll Test + Gate 1 Compliance), VISUALIZE (Visual Production), CD RENDER PASS (the Creative Director node highlighted at a second station so the post-render pass is legible), QUEUE (Publishing & Operations), HUMAN GATE (you), PUBLISH (Publishing & Operations or auto), RECORD (Publishing & Operations → ledger + audit). The Brand Onboarding Strategist appears docked/dimmed except during a live §7.1 intake.
- **Handoffs are animated carriers.** When an agent hands off, a small "file" chip carrying the `piece_id` glides along the edge from sender to receiver and "wakes" the receiver (state → working). This is the core confidence signal: you *watch* a draft move Evergreen ▸ Creative Director ▸ Visual Production in real time. `blocked_by` relationships (§17 Task) render as dashed "waiting-on" links so a stall is legible.
- **Review loops are first-class.** The two back-edges this pipeline is structurally prone to are drawn as distinct **amber return arcs**, not the forward beam: Creative Director —revise(≤2)→ content agent (with a live round counter **R1 / R2**), and CD RENDER PASS —fail→ Visual Production. At **round 3 the arc turns red and the escalation edge to the Managing Editor lights** (§15.1) — the graph *predicts* the escalation before it fires. Each in-flight piece carries a small loop meter of revise rounds used.
- **Node state** is shown by **icon + label + colour together** (never colour alone): Idle · Working (an active "studio light" ring that breathes) · Reviewing · Queued/Waiting-on-you · Looping (⟲ + round) · Paused · Breaker-tripped · Fail-closed safety block (shield). Each station also shows its current `piece_id`(s), queue depth, last-heartbeat age, and its token contribution to the run.
- **Three layouts, one live state:** **Floor** (the spatial studio, default — for confidence), **Pipeline/Lanes** (the §10.1 stages as a flat tracker / Kanban over the QueueItem status enum Draft | CD Review | Approval Queue | Approved | Published | Archived, §17 — for triage), and **Company** (the Managing-Editor-at-top org view — the §5.2 factory / §5.4 framing). **Follow-a-piece** filters the floor *and* the feed to one piece's journey (like tracking a package); a **Replay** scrubber (built on durable Sessions + spans, §13.2/§14.5) re-watches how any past piece was made — pride and root-cause in one control.

**Replay is reconstruction, never re-execution.** Replay renders the *persisted* `Span`/`StudioEvent` record (§17) as a timeline scrub — it **never re-invokes an agent, never calls a tool, never re-publishes, and consumes zero new tokens** (so it can neither trip nor be charged against the §13.2 breaker). If a piece's detailed spans were pruned past retention (§14.5), Replay shows the durable audit summary with a "detailed spans expired" notice. It is safe to open on any published piece — a read surface that structurally cannot spend (Day-1 agent=harness boundary; Day-4 observability).
```gherkin
Scenario: Replaying a past piece never re-runs the agents
  Given a published piece with a persisted span/event record
  When the owner opens Replay and scrubs its 10-stage journey
  Then the floor re-renders recorded spans/events only; no run is dispatched, no tool called, no tokens charged
  And if detailed spans expired, the durable audit summary is shown with a "spans expired" notice
```

**The activity feed (the narrative).** A continuous right-rail feed turns the §14.5 OpenTelemetry-style spans and the append-only audit trail into **plain-language narrative** — the anti-opacity surface, and the §8.2 weekly visibility digest made real-time. Each row is `timestamp · actor (agent glyph + signature hue / ★you / ⚙system·breaker) · verb · piece-id chip · stage chip · one-line detail`.
- **Deterministic vs. semantic events are visually distinct:** a LEDGER LINT line names the exact countable §9.4 rule it checked (hook-within-3, shape==prior, aphorism >1-in-5, idea-rerun-30d, treatment-label back-to-back, weekly-research-min); a Creative Director line carries the rubric rationale. The owner can always tell a hard gate from a judgment call.
- **Two layers:** clean headlines by default (approachable for a marketer); a **"raw span / log tail" drill-down** behind any row for troubleshooting (Paperclip's span/log detail is available but hidden, never the default firehose).
- **Filters:** All · Drafts · Reviews · Handoffs · Approvals · Costs · Alerts, plus **"Mine"** (your own actions — your personal audit trail) and **"Needs me."** Live rows arrive over a WebSocket while the source station flashes on the graph — the feed and the graph are two views of one event stream. The **Friday visibility digest** (§8.2) is pinned as a live card (slots hit/missed, paused routines, image spend, CD↔owner agreement) rather than waiting for a weekly message.

**The event stream — how a poll-based backend feeds a live console.** The §13.2 loop is poll-based, so 'real-time' must be *produced*, not assumed (Day-2 — the substrate A2UI renders over; Day-4 — observability).
- **One append-only event log is the single producer.** Every run start/finish, handoff, gate verdict, render pass, breaker action, stall detection, and human intervention appends a `StudioEvent` (§17) to a durable ordered log — a **denormalized projection of** the Sheets SoR + audit (§12.2/§14.5), never authoritative over them.
- **The §13.2 orchestrator tick is the sole emitter of derived/absence events.** Stall, heartbeat-age, >80% budget-pressure, and breaker-tripped are computed by the tick and *written as events* — never inferred client-side — so a stall is caught even with **no console open** (anti-silent-stall, §14.5).
- **A thin relay fans out; the UI is a pure consumer.** A lightweight Cloud Run gateway tails the log and pushes over WebSocket/SSE; it holds no authority and runs **outside** the circuit-breaker (the breaker wraps the *runner*). If the relay is down, the floor degrades to polling the same log.
- **Every event carries** a monotonic `seq`, a stable `event_id` (dedup key when a poll re-reads a row), `piece_id`, `stage`, `actor`, `verb`, `span_ref`, and `ts` (§17) — so the feed orders, de-duplicates, and lets a reconnecting client replay from its last `seq`.

**Liveness honesty & two-tier state (a stale console is the dead form again).**
- A persistent **connection chip**: `● Live` / `◌ Reconnecting (last update 12s ago)` / `▲ Offline — showing last-known`. When not live, in-flight nodes dim to "last-known" so a frozen carrier is never mistaken for a working agent.
- **Reconnect replays the gap, not the world:** the client requests every `StudioEvent` after its last `seq`; the relay backfills from the durable log, then resumes the push.
- **Two tiers, one authority:** (a) **durable status** — QueueItem status + audit in the Sheets SoR (§12.2), **authoritative**; (b) **in-flight live state** — reconstructed from the `StudioEvent`/`Span` stream, **best-effort/presentational**. On any disagreement (a missed "draft complete" leaves a node *drafting* while the SoR reads `CD Review`), **the SoR wins** and the live tier is corrected on reconnect. The console never derives a status the orchestrator did not write.

**The feed is a new exposure surface — the redaction invariants extend to it** (Day-4 — 7-pillar security; observability done safely). The activity feed, the raw-span drill-down, and Replay inherit §14.6 and §14.3:
- **No secret material ever renders.** `[[VARIABLE]]` secrets resolve only into the tool/MCP auth layer; `Span` tool args/results are stored **already redacted** (`redacted:true`, §17) so an auth header, signed-URL token, or vault value never appears in a feed row, drill-down, or Replay.
- **No raw chain-of-thought.** `think` spans surface as a **one-line summary**; the §14.2 semantic-gate referee's internal prompt is never shown — the owner sees the *verdict and reason*.
- **Brand-scoped streams.** A relay connection is authenticated and **scoped to a single `brand_id`** (Phase-6 multi-brand); a cross-brand event is never delivered to the wrong console.
```gherkin
Scenario: The console loses its connection and recovers without losing events
  Given the relay connection drops, then the header shows "Reconnecting" and in-flight stations dim to "last-known"
  When the connection is restored
  Then the client requests all StudioEvents after its last seq, the relay backfills the gap before resuming, and every QueueItem status is reconciled from the Sheets SoR, which wins on any conflict

Scenario: A tool call with a signed URL never leaks into the feed
  Given Visual Production calls drive_upload with a signed-URL credential
  When the call is recorded as a Span and surfaced in the feed
  Then the feed row and its drill-down show the redacted span (no token, no header), and the relay delivers only events scoped to the viewer's brand_id
```

**Stuck / loop / cost detection (nothing silently stalls).** Detection is grounded **only in real PRD mechanisms** and surfaced immediately on the floor (and as sidebar badges + a "Needs You" tray), never deferred:
1. **Run-level circuit-breaker trip** — the per-run token accumulator *or* the hard iteration/step cap is exceeded → run aborted + agent paused (§13.2 / §6.2 R-ORCH-5). Shown honestly as the **run-level** breaker it is — a header gauge tracks tokens-vs-budget and iterations, an **">80% → only-critical-work"** band, and a red "Paused by breaker" badge on trip. This is the encoded ~631k-token runaway made visible; it is **not** the per-call `max_output_tokens` cap.
2. **Review loop maxed** — revise hits round 3 → escalate to Managing Editor (§15.1).
3. **Silent stall** — a task with no new span / no state advance past a gentle threshold (Paperclip's 1h "needs attention" / longer "critical", retuned for content cadence) — honouring the §13.2 anti-silent-pause rule.
4. **Repeated ledger-lint block** — a piece that cannot clear the deterministic pre-CD gate.
5. **Budget pressure** — above ~80% of an agent's / `offering_id`'s monthly budget (§13.2).
6. **Fail-closed safety block** — an unconfirmed `claims_forbidden` / `non_disclosure_rules` / `required_framing` routes the piece to a human (§14.2).

7. **Approved-but-unposted (manual last-mile stall)** — a piece in `Approved` with no mark-as-posted past a gentle, cadence-tuned threshold appears in "Needs You" with an "awaiting your post" badge and a one-tap re-open of its Post Kit (§12.3.2). This is the silent stall the manual handoff is most prone to — surfaced, not deferred.
8. **Publish-time semantic-gate block** — the §14.2 LLM referee BLOCKs an `instagram_publish` in auto mode → the piece surfaces to "Needs You" with the referee's verdict + reason (distinct from the deterministic fail-closed block, item 6).
9. **No publish adapter for the channel** — an approved piece on a channel with no registered adapter (§12.3) is shown as "won't auto-publish — hand off by hand," queued for manual handoff, never a silent stall.
10. **Materialisation paused (owner-absence backpressure)** — when the §9.5 backpressure pause is active (deep queue + prolonged owner absence), a brand-level **"materialisation paused"** banner sits in the run-budget/breaker header with the queue depth + days-absent and an "any action resumes it" hint; it clears automatically on the next tick after any owner action (a CRITICAL out-of-band alert also fires, §14.4.1).

*Budget-gauge scope (never conflated).* The header gauge is the **per-run** accumulator vs the run cap — the breaker (§13.2), **not** monthly; the per-agent and per-`offering_id` **monthly** budgets (the >80% band, item 5) live on the Trust & Budget panel.

Each opens an **honest "where & why it broke" card** at the precise *piece × stage × agent × run* coordinate: what happened, the evidence (the verbatim CD note / the exact linter rule / the breaker's `total_tokens` vs cap from the §17 Run entity), and the consequence ("one more reject → escalates to the Managing Editor"). A loop shows a mini-timeline (R1 → R2 → …).

**When there is *no* verbatim error (the opaque-failure case).** The card's evidence model (CD note · linter rule · breaker `total_tokens`) assumes an error was *emitted*. A silent stall (#3) and a crashed run emit **neither** — the dead-form opacity this section exists to defeat, returning at the worst moment. For these the card **degrades honestly** rather than going blank: it shows the **last successful span + stage**, **elapsed since `heartbeat_at`**, the Run `status` / `attempt` / `error_class` (e.g. `lease_expired`, §13.2), any captured **exception/stack tail** (`Run.error_verbatim`, §17), a **suspected-cause heuristic** (process death vs hung external tool vs `blocked_by` deadlock, §13.2), and the concrete next action ("auto re-dispatch pending (attempt 2/3)" or "needs you"). Every run **wraps its step loop** so an uncaught exception is written to `Run.error_verbatim` *before* the run dies — the floor never shows "stuck, reason unknown" when any trace exists (Day-4 — the diagnostic must be strongest exactly where the failure is most opaque; Day-2 — the floor is the diagnostic surface).

**Intervention — the "Floor Actions" verb set (participation, not just gating).** From any graph node, feed row, stuck card, or queue item, the owner has one consistent set of actions — each writing an `AuditEntry` with `actor = human` and appearing back in the feed as a "you" action:
- **Unstick & resume** — clears the pause and re-dispatches the run (after a breaker trip, this resets the run accumulator before resuming; raising the cap is a high-stakes §14.4 action gated by a Vibe-Diff).
- **Edit task** — rewrite the idea sentence / hook / a concrete detail, the caption, or the visual brief (MESSAGE→FEELING→TREATMENT) mid-flight (conductor participation).
- **Re-route handoff** — reassign to a different agent (e.g. the other content agent) or send back a stage (with a required justification).
- **Inject note / nudge** — drop guidance into the agent's *next* run context (fresh-session-per-run, §13.2); one-shot by default. To make it **standing**, the owner promotes it through the **§7.7 canon Edit-Loop** (a versioned canon/engine-doc amendment with Impact Preview) — durable guidance lives in canon, not a free-form memory write.
- **Approve · Request changes · Reject** (the verbatim §12.1 action set) and **Override-CD** — overturn a Creative Director verdict at REVIEW or the HUMAN GATE. *(An override is the §15.3 calibration signal — it feeds the CD↔owner agreement rate; participation literally trains the auto-publish trust gate. A reject is recorded as a killed idea in the ledger, §9.4.)*

- **Publish (if manual)** — **opens the Post Kit (§12.3.1); it does not post for you.** On the Studio Floor and the Approvals / Light-Table view this surfaces the channel-aware Post Kit (ordered slide files, copy-blocks, per-slide alt text, send-to-phone / QR) and the ordered checklist, then exposes **Mark as posted** (§12.3.2). The "publish lifts the card to the Gallery" motion fires on **mark-as-posted**, not on approval — on the manual path the Gallery is the published archive keyed by `posted_permalink` (Day-2 — turn a Drive folder into a tappable kit; Day-5 — HITL).
- **Hard-stop run** — a manual breaker trip on any run.


**Stop & resume semantics (no half-acts, no human-driven infinite loop).** (Day-4 — Denial-of-Wallet / observability.)
- **Hard-stop takes effect at the next step boundary**, not mid-call. An in-flight **act-tier** call (`instagram_publish`) completes atomically (the `piece_id` publish-once guard, §12.2, prevents a duplicate on resume); draft/visual work simply halts with a "Paused by you" badge + audit entry.
- **Unstick re-dispatches a *fresh* run** (clean session per §13.2) — it does **not** continue the looping conversation that tripped the breaker, so resetting the accumulator cannot silently re-enter the runaway. It resumes from the last idempotency checkpoint (§13.2) and seeds any injected note.
- **Anti-thrash guard:** repeated Unstick of the **same piece** beyond a small cap (e.g. 2) escalates to the Managing Editor and requires a Vibe-Diff (§14.4) — the human cannot become the loop the breaker exists to stop (the ~631k-token lesson).
```gherkin
Scenario: Hard-stop never leaves a half-published piece
  Given a run mid instagram_publish and the owner hits "Hard-stop run"
  Then the publish completes atomically under the piece_id guard and the run halts at the next step boundary with a "Paused by you" badge + audit entry

Scenario: Unstick cannot silently re-enter a runaway loop
  Given a run aborted by the breaker, when the owner chooses "Unstick & resume"
  Then a fresh run with a clean session is dispatched (not the looping conversation), and a third Unstick of the same piece escalates to the ME and requires a Vibe-Diff
```

**No approval is required to interrupt** (any owner can, matching Paperclip's stance), but **high-stakes actions — raising a budget cap, enabling auto-publish, canon/config edits — route through the §14.4 Vibe Diff and never auto-apply.** Every console action maps **1:1 to a Google Sheets *Owner Action* cell write — never a direct Status write (§12.2) — over the same append-only audit trail** (§12.2): the orchestrator stays the *sole writer of derived status*, the console is a rich view, and there is no competing source of truth.


**Multiple operators, one consistent state.** "Any owner can interrupt" implies more than one human (Day-4 — IAM / least-privilege for people; evaluation calibration):
- **Operator identity.** Each human action records `actor=human` *and* a stable `operator_id` (§17, on AuditEntry / StudioEvent) so "Mine" and the personal audit trail are real; each human is an `Operator` (§17).
- **Human authority tiers (least-privilege for people).** Routine **Approve / Request changes / Reject / Edit-task / Inject-note** are open to any operator; **high-stakes** — enabling auto-publish, raising a budget, canon/config edits, **Override-CD** — are gated to an **owner-tier** operator and route through the Vibe-Diff (§14.4).
- **Optimistic-lock per piece.** Each item carries a `rev` (§17); a console write includes the version it read. A stale write is **rejected with a "this piece changed — here's what happened" refresh**; conflicting terminal verdicts (Approve vs Reject, incl. a Sheets edit vs a console action) resolve **first-committed-wins**, and the loser is told — this is the concurrent-human-signal rule shared with §12.2.
- **Edit-task during an active run** is queued as a pending edit applied to the agent's **next** run (fresh-session-per-run, §13.2); the node shows a "pending edit — applies next run" chip. Any edit to publishable content re-runs the deterministic Policy Server gates before publish (§12.2 human-edit re-gating).
- **Override-CD is recorded as a distinct disagreement event**, not a plain Approve, so it feeds the §15.3 CD↔owner agreement rate and the trust gate.
```gherkin
Scenario: Two operators act on the same piece at once
  Given operators A and B both have the piece open at rev 7
  When A submits "Approve" (commits at rev 8) and B then submits "Reject" carrying stale rev 7
  Then B's write is rejected with a refresh showing A's approval, and exactly one verdict is recorded in the audit trail
```

**Human-in-the-loop participation & the two stances.** The owner is the company's principal, with a seat on the floor. A single header toggle moves between the two §5.4 stances:
- **On the floor / Conductor** (real-time): an "Ask the studio" command box spawns an on-demand piece (journey 4) you watch flow through the floor and intervene on at any stage.

 *(**The conductor box submits a request — it does not create the task.** "Ask the studio" does **not** let the UI write a `Task` directly — that would bypass the Policy Server (§14.2) and the sole-writer rule. The box posts an **owner request** that the **Managing Editor** turns into a Task via its `create_task` / `assign_task` capability — the only role permitted; the owner then watches it flow. This keeps the conductor stance (§5.4) inside the same governance path as the scheduled rhythm — the human asks, the orchestrator dispatches. Day-2 — GOTO discipline for human control flow; Day-5 — Policy Server integrity.)*
- **Let it run / Orchestrator** (async, default): the weekly rhythm runs (§13.1); pieces collect at the HUMAN GATE; approvals are **batched with quiet-hours** to defeat approval fatigue (§14.4).

**Ambient vs. out-of-band (the away-owner path).** The WebSocket feed and the 'Needs You' tray are **AMBIENT** (§14.4.1) — they reach only an owner with the console open. The default stance is **Orchestrator (owner away)**, so the stuck / loop / cost detections do **not** rely on the console alone: each is classified by the §14.4.1 catalog and the **CRITICAL** ones (breaker trip, fail-closed block, provider-error stop, adapter-down) **also emit an out-of-band `notify`** (and land on the pinned Sheets `ALERTS` row). Routine "ready to approve" items collect into the next batch; **alerts pierce quiet hours, approvals do not**; each notification **deep-links to the exact `piece × stage` coordinate**. The **'Alerts' feed filter** is the in-app mirror of the same `Notification` stream (§17); an alert is **acknowledged** here (ack / snooze / mute), which resolves it across every channel and stops the re-notification ladder. Day-1 — conductor/orchestrator (async default); Day-5 — HITL / approval fatigue.

The **HUMAN GATE / approval surface deepens §12.1**: each item shows the rendered image(s)/carousel, final caption, hashtags, alt text, channel, the offering it funnels to, and the CD note — *plus* the ops context for a confident decision (the ledger-lint summary, claim-grounding status, the piece's loop history, a thumbnail of its journey) — with the exact actions **Approve · Request changes · Reject · Publish (if manual)**. Publishing obeys the §12.3 precedence exactly and the idempotent publish-once guard keyed by `piece_id`.

A **Trust ladder** governs auto-publish and **never auto-flips**: a meter shows `approval_mode`, the `auto_publish_enabled` master kill-switch (default off), and `trust_threshold` progress (`window_pieces`, `min_approval_rate`, `max_avg_human_edits`, `zero_policy_violations`) with the CD↔owner agreement rate as the headline (§7.2/§12.3/§15.3). When the window is met the console only **surfaces a recommendation** — enabling auto-publish is owner-only and requires signing a plain-language **Vibe Diff**; a single **owner** reject or policy violation **visibly resets the window to 0** (routine CD rejects do not, §12.3). The owner *watches the company earn autonomy* rather than granting it blind.

**Look & feel (dark + light, both first-class).** The aesthetic is a "warm atelier / calm control room," chosen to beat the prior bland UI through craft, not decoration.
- **Themes:** Dark default (warm desaturated near-black ink, e.g. `#12131A`, never pure black; active stations carry a soft brand-accent bloom) and a full Light theme (warm paper off-white, e.g. `#FAF8F4`, with crisp dividers and solid status rings so brightness never washes out state). Theme toggle in the header; respects system preference; persists per user.
- **Semantic colour, learnable in one glance, never the sole signal:** one "active/working" accent (a luminous brass "studio light"); green = approved/verified/healthy; amber = waiting/paused/revise-loop/>80% budget; red = breaker/reject/error/fail-closed; **violet = the human** (every action *you* take is violet across graph and feed, so your fingerprints are visible). Each of the eight agents has a **distinct, accessible signature hue** used identically as node accent, feed actor dot, and content-piece tint. Every state also carries a glyph + text label (WCAG AA, colour-blind safe).
- **Typography:** a humanist sans for UI (e.g. Inter/Geist), an editorial display face for headers/agent names to signal the content-studio identity, and a monospace (e.g. JetBrains Mono, tabular numerals) for `piece_id`s, timestamps, and token/iteration counts so the machine layer reads as machine.
- **Motion is meaningful, never decorative** and ≤~300–400 ms eased: carriers glide along handoff edges; active stations breathe; a revise/render-reject arc flashes once so you catch the loop forming; a breaker trip is a single sharp red flash settling to steady red; clearing REVIEW earns a brief "sealed" milestone; publish lifts the card to the Gallery. **Full `prefers-reduced-motion` path** (motion collapses to instant state changes + badges, losing zero information). A **comfortable/compact density** toggle serves both the relaxed owner and the power user triaging a stall. The graph and all Floor Actions are keyboard-navigable.

**Information architecture.** Six surfaces, all sharing the *piece × stage × agent × run* coordinate so navigation is lossless drill-down:
1. **Brand Intake** — the §7.1 guided interview (explicitly *not* a dead form — the failure this corrects); safety fields elicited explicitly and fail-closed; ends with the first-light near-violation test. On completion the floor comes alive.
2. **Studio Floor (home)** — the live graph + activity feed + "Needs You" tray + run-budget/breaker header.
3. **Approvals / Light Table** — the HUMAN GATE opened up; the §12.1 Review app deepened; Sheets-parity (§12.2).
4. **Piece Dossier** — one piece's full 10-stage journey with timestamps, every CD round + note, the rendered carousel + alt text, lint result, run cost, and Replay (the troubleshooting drill-down and the intervention drawer's home).
5. **History / Trust & Budget** — the Content Ledger (§9.4) + append-only audit (§14.5), the published archive, per-agent/per-offering budgets + breaker incidents, the CD↔owner trend, and the digest archive.
6. **Brand Settings (the kit editor)** — the post-onboarding home for §7.7 edits, distinct from the §7.1 one-time intake. It renders the Brand Kit as grouped, **class-badged** fields (`trivial` / `material` / `safety` / `autonomy`), shows `BrandKit.version` + the `BrandKitRevision` history (§7.7) with one-click **rollback**, and presents the **Vibe-Diff inline** on save (before→after + downstream effects, §14.4). The `autonomy` controls (`approval_mode`, `auto_publish_enabled`, `trust_threshold`) live here **behind the trust ladder** — read-only until the owner signs the Vibe-Diff. A **re-light** button commissions the §7.7 test piece. Every save lands as a violet "you" action in the feed and writes an `AuditEntry` + `BrandKitRevision`. Day-2 — generative UI; Day-5 — Vibe-Diff (defeat the dead form for editing).

**The Brand Desk & the Planner (groupings, not new surfaces).** The **Brand Desk** is the front-office grouping of surfaces 1 + 6 (Brand Intake + Brand Settings) — where §7.1/§7.7/§7.8 send the owner to onboard, edit, clone, or switch a brand. The cadence **Planner** (the weekly/monthly calendar where §7.1.1/§9.5 capture and edit the rhythm) renders **inside Brand Settings** as its cadence view. Both name existing surfaces, so the IA count stays **six**.

Drill-down chain everywhere: floor node → piece → per-task timeline → feed line → raw span/log. The console **reads/writes only through the existing `sheets`/`drive` MCP tools** (§16); the circuit-breaker still wraps the *runner*, not the UI.

**Approachable by design (what we deliberately leave out).** To keep a brand owner from drowning, the Studio Floor adopts Paperclip's useful subset (status lamps, narrative activity stream, recovery prompts, cost bar, sidebar badges, theme toggle) and **omits** its engineer-grade internals: org-ancestry SVG / delegation-path internals, execution-workspace/sandbox-mount controls, liveness-incident-classification keys, per-agent model-profile / recovery-adapter overrides, trust-preset / quarantine mechanics, 100-language syntax-highlighted run logs (plaintext summary by default; full log only on an error drill-down), and DB/migration prompts. Anything advanced lives behind an "Inspector" drawer.

**One role, many in-flight pieces (the Offering Content Agent).** Because one Offering Content Agent serves N offerings (brief by `offering_id`, §7.4), IDEATE+DRAFT can hold several concurrent Offering pieces. They share the agent's signature hue but **each carrier is labelled with its `offering_id` and tinted by that offering's accent**, so two offerings are never confused. The docked Strategist is not a pipeline station (excluded from in-motion / queue-depth counters).

**Cold-start and empty states (no relapse into a dead form).** "Comes alive" is specified for when there is nothing yet: **First light** (before any piece exists) shows eight idle stations + one CTA "Ask the studio to make your first piece" — never a blank canvas; **All-idle** (between scheduled runs) rests with the next wake shown ("Monday — editorial calendar") so quiet reads as *resting*; **loading vs empty vs offline** are three distinct states (skeleton / "nothing yet" / "showing last-known"). **Screen-reader liveness:** the feed is an ARIA live region — **polite** for routine rows, **assertive** for `needs_you` / breaker / fail-closed — so a non-visual operator gets the same anti-stall guarantee without being spammed. Day-2 — generative / accessible UI; Day-1 — one role, parameterized.

**Acceptance scenarios.**
```gherkin
Scenario: A handoff and a review loop are visible live
  Given the owner is on the Studio Floor
  When Evergreen Content hands a draft to the Creative Director
  Then a carrier animates along the edge and the Creative Director station wakes
  And when the Creative Director returns it for revision
  Then an amber return arc shows "revise 1/2" and the activity feed records the reason
```
```gherkin
Scenario: A stuck loop surfaces and the owner intervenes
  Given a piece has reached revise round 2 of 2 (next round escalates)
  Then it appears in the "Needs You" tray with an honest "where & why" card and its evidence
  When the owner injects a note and chooses "Unstick & resume"
  Then the note enters the agents' next run context
  And the intervention is written to the append-only audit trail and shown as a "you" action
```
```gherkin
Scenario: Trust is never auto-flipped
  Given a brand has met its trust_threshold window
  Then the Studio Floor only surfaces a recommendation to enable auto-publish
  And auto_publish_enabled changes only after the owner signs the Vibe Diff
  And a single owner reject or policy violation resets the trust window to 0
```

**A2UI / Generative UI — where the agent emits UI, and where it does not** (Day-2 — A2UI / Generative UI + A2A / Agent Cards; Day-4 — distributed observability).
- **Conventional client (default):** the agent-graph canvas, activity feed, trust/budget panel, and Light Table are a hand-authored client over the §12.4 event stream — not generated per render.
- **Genuine A2UI surfaces (rendered from an agent-emitted, schema-bounded UI description — not free-form HTML):** (1) the **Vibe-Diff card** (§14.4) the Managing Editor emits for sign-off; (2) the **"where & why it broke" intervention card** composed from the stall / breaker `StudioEvent` (§17); (3) the **"Ask the studio" clarifier** — a small structured form when a request is underspecified. Agent-emitted UI is **declarative + whitelisted-component-bounded** (the A2UI analogue of MCP's bounded-tool discipline, §16).
- **A2A Agent Cards power the "Company" view:** once agents split into A2A services (§13.3), each station's panel is sourced from that agent's **Agent Card** (name, bounded domain, allowed tools).
- **Distributed tracing:** across the A2A boundary `Span`s (§17) carry propagated **trace context** so the floor renders one coherent cross-agent journey; a missing link surfaces as a **"trace gap"** on the dossier, not a silently incomplete timeline.



**Build mapping.** Phase 5 (§19), deepening §12.1; component spec registered in Appendix D. Core components: the live **agent-graph canvas** (stations / edges / carriers / loops / states), the **activity-feed stream** (a WebSocket consumer over §14.5 spans + audit), the **"Needs You" / intervention drawer** (the Floor Actions verb set), the **approval / Light-Table view** (Sheets-parity over §12.2), the **trust & budget panel** (run-level breaker gauge + trust ladder), the **theme / density system**, and the **Brand-Intake conversational view** (§7.1).


### 12.5 The approval protocol — one contract across all three surfaces

**Why this exists.** Approvals are where the owner's time is actually spent — and where a clumsy design creates **approval fatigue** (Day 5) or, worse, lets a human edit slip an unverified claim past the fail-closed gates. §12.1/§12.2/§12.4 each describe an approval *surface*; this section defines the single **approval protocol** all three implement identically, so the Sheets gate, the Review app, and the Studio Floor Light Table are interchangeable views over one audited state machine. It **adds** the routing, bounding, re-gating, identity, aging, and parity around the already-consolidated Owner-Action column (§12.2), human-edit re-gate (§12.2), notification/escalation (§14.4.1), and trust-window reset (§12.3).

**The five owner verbs (canonical).** Every surface exposes the same verb set — **Approve · Approve-with-edits · Request-changes · Reject · Publish (manual)** — and each verb resolves to exactly one `ApprovalAction` (§17) written to the append-only audit trail with the acting `operator_id`. The orchestrator stays the **sole writer of derived status** (§12.2); all three surfaces submit *owner signals*, never competing writes.

**Surface-parity contract (a hard requirement; degradation is explicit).**

| Capability | Sheets gate (§12.2) | Review app (§12.1) | Studio Floor Light Table (§12.4) |
|---|---|---|---|
| Approve / Reject | Owner Action = Approve / Reject | button | button |
| Approve-with-edits | edit Caption cell + Owner Action = Approve (re-gated, §12.2) | inline caption editor | inline caption editor |
| Request-changes (+ note, + `route_to`) | Owner Action note + `route_to` column | form | intervention drawer |
| Reject reason (labeled, §15.3 taxonomy) | validated `reject_reason` dropdown | dropdown | dropdown |
| Partial-carousel action | `slide_actions` cell (e.g. `re-render:3`) | per-slide controls | per-slide controls |
| Bulk approve | multi-row Owner Action edit | multi-select | multi-select |
| Manual Publish | Owner Action = Mark posted (after Approve, §12.3.2) | button | button |
| Preview + CD note + ops context | Drive links + columns (thumbnail-limited) | full | full |

The **Sheets surface is the floor of parity** (works offline/mobile, zero build); the two apps **deepen** it but add no capability the append-only audit trail cannot already express. Where a surface can't render a rich control (e.g. a full carousel on a Sheet), it degrades to an explicit textual equivalent — never to a *missing verb*.

**Who-can-approve (operator identity & delegation).** Approval authority is per-brand and explicit:
- An **`Operator`** (§17) is any human who can act — identified on the apps by authenticated session, on the Sheets surface by the **Google account of the cell editor** (harvested from Drive revision metadata). `AuditEntry.operator_id` binds the concrete accountable human.
- Each brand carries an **`approver_allowlist`** (Brand Kit governance block, §7.2) plus an optional **delegation** grant (`delegate_operator_id`, `scope ∈ {approve, request_changes_only, publish}`, `expires_at`) — the §14.1 read/draft/act ladder applied to *approval authority* (Day 3). An action from a non-allowlisted operator is **refused fail-closed** and surfaced ("not authorized to approve for this brand"), never silently accepted.
- **Enabling auto-publish, raising budget caps, and canon/config edits stay owner-only** (§14.4) even under delegation — delegation covers routine gate decisions, not high-stakes actions.

**State-transition guards (no ambiguous, late, or lost decisions).** Owner verbs are legal from `Approval Queue`; from `Approved`, both manual Publish (`Mark posted`) and Request-changes (→ `CD Review`, per §10.1/§12.3.2) are legal. Every submission carries `piece_id + expected_status` (optimistic concurrency over `rev`, §12.2):
- Terminal `Published` / `Archived` **reject every owner verb** ("already published/archived").
- Concurrent actions on one piece resolve **first-committed-wins**; the losing surface is told the piece already moved (`result = superseded`).
- **Reject** → `Archived` and a **killed idea** recorded in the ledger (§9.4). **Request-changes** → back to `CD Review` (loop below), never straight to `Approved`.

**The request-changes loop (owner ↔ studio, bounded).** Request-changes takes (a) a **free-text note** and (b) a **`route_to`** target:
- `content` → the underlying `Task` re-enters the **DRAFT** stage on the owner agent (the `QueueItem.status` stays `CD Review` per §10.1 — a new Draft attempt), note injected into that agent's next-run context (fresh-session-per-run, §13.2), then forward through LEDGER LINT → CD REVIEW.
- `visual` → re-enters at **VISUALIZE** (Visual Production); the CD render-pass re-runs.
- `cd` → back to **CD REVIEW** with the owner note as an overriding rubric input (the owner is telling the judge what it missed).
- **Owner rounds are counted separately from CD revise rounds** (`Task.owner_change_rounds`, §17) and **bounded at 2**: a 3rd owner request-changes on the same piece **escalates to the Managing Editor** (the human-loop analog of §15.1) with a "this piece keeps missing — rethink or kill" card; if the ME cannot clear it, it re-emits as an owner ACTION (§14.4.1). Every owner round **re-runs the full deterministic + CD gates** before returning to the HUMAN GATE, so a reworked piece is never handed back un-vetted. A request-changes does **not** reset the trust window (only shipped defects do, §12.3).

```gherkin
Scenario: Owner requests changes, routed and bounded
  Given a piece is in the Approval Queue
  When the owner selects "Request changes", writes a note, and sets route_to = "content"
  Then Task.owner_change_rounds increments to 1 and the piece's Task re-enters the DRAFT stage (QueueItem.status stays CD Review, §10.1) with the note in the agent's next-run context
  And it flows through LEDGER LINT and CD REVIEW before returning to the HUMAN GATE
  When the owner requests changes a third time on the same piece
  Then it escalates to the Managing Editor instead of looping again
```

**Approve-with-edits (the human edit is re-gated, fail-closed).** The owner may fix caption/hashtags/alt-text inline and approve in one action — **never trusted blindly**. The edit re-runs, in order, the same gates the agent's draft passed (the §12.2 human-edit re-gate):
1. **Deterministic ledger-lint** (§9.4) on the edited text (hook-within-3, shape, aphorism cap, idea-rerun, treatment-label, …).
2. **Fail-closed safety-field check** (§14.2) — `claims_forbidden` / `non_disclosure_rules` / `required_framing` — because a human can paste a forbidden or non-disclosed-mechanism claim as easily as a model can.
3. **Claim-grounding** (§14.2) — any new factual sentence must resolve to a VERIFIED Claim-Bank entry or be blocked.
- **On pass:** → `Approved` (then Publish per §12.3); a **`Correction`** record (§17) captures `before`/`after`/`edit_class` and feeds §15.3.
- **On fail (fail-closed):** the approval is **refused** (`result = refused_regate`); the piece stays in `Approval Queue` with the edit held and an honest "your edit didn't pass: <exact rule>" message — a human edit can never bypass an invariant a model draft couldn't. The owner can fix-and-retry or Request-changes.
- CD re-judgement of a human-edited caption is **not** required by default (deterministic gates + owner authorship are the backstop), but the edited piece is flagged for the §15.3 calibration sample.

```gherkin
Scenario: Approve-with-edits is re-gated and can fail closed
  Given a piece in the Approval Queue whose caption the owner edits inline
  When the owner submits "Approve with edits"
  Then the edited caption is re-run through ledger-lint, the fail-closed safety-field check, and claim-grounding
  And if the edit introduces an unverified or forbidden claim the approval is refused and the piece stays queued with the reason shown
  And if it passes, the piece is Approved and a Correction record (before/after/edit_class) is written for §15.3
```

**Bulk / batch approve (safe by construction).** In the async/orchestrator stance pieces collect at the HUMAN GATE; the owner may multi-select and **Approve-all in one gesture**. Guardrail: bulk-approve **admits only fully-clean pieces** — CD-approved, ledger-lint pass, claim-grounding pass, zero warnings, no unresolved edits. Any piece with a warning, a failing re-gate, or a low CD↔owner-history flag is **held out** (visually separated in the tray) and opened individually. Bulk-approve writes **one `ApprovalAction` per piece** (never a coarse single row), preserving per-piece attribution and the §12.2 idempotency guard. **Bulk Reject/Request-changes is not offered** — a rejection needs its own labeled reason (§15.3).

```gherkin
Scenario: Bulk approve admits only clean pieces
  Given five pieces in the Approval Queue, one with a claim-grounding warning
  When the owner selects "Approve all"
  Then the four clean pieces are approved, each with its own ApprovalAction and idempotent publish
  And the piece with the warning is held out and shown for individual review
```

**Mobile approval.** The Sheets gate is the **zero-build mobile path** — the Google Sheets mobile app already lets the owner change Owner Action / caption cells from a phone with the same audit outcome. The Review app and Light Table ship a **responsive, thumb-reachable approval view** (Day 2 A2UI/Generative UI): a swipeable card stack (image + caption + CD note + the ops one-liners), **one-tap Approve**, tap-to-expand for request-changes/reject, and the "Needs You" count as the home badge. `notify` (§16) links straight to the piece. Heavy surfaces (the live agent graph, Replay, Inspector) degrade to a link on small screens — approvals themselves never require the desktop console.

**Aging & staleness of pending approvals (nothing rots silently).** A pending piece is tracked by **`queued_at`** (§17) and badged fresh (<24h) · aging (24–72h) · **stale (>72h)**, tunable per brand `approval_sla_hours`:
- A **stale** item raises a "Needs You" ACTION escalation (§14.4.1) and pins to the Friday digest's "waiting on you" line (§8.2/§14.5).
- A **dated** piece (campaign/seasonal slot with a target date, §7.4/§9.5) whose target date passes while pending is handled by the **canonical §9.5 mechanism**: past `target_date + stale_grace_days` it is set `exception = Stale-Dated` and routed to the owner (**Re-date · Publish anyway · Archive**) — **never silently published late**. (A per-brand default disposition, if wanted, is an option within §9.5, not a parallel field here.)
- **Content-freshness re-lint:** if a piece sits longer than the ledger's rotation windows, approving it **re-runs the deterministic ledger-lint against the *current* ledger** first, catching staleness (a hook that has since collided) the original lint couldn't see.

```gherkin
Scenario: A stale, dated pending piece is not silently published
  Given a campaign piece with a target date now in the past sits in the Approval Queue
  Then it is set exception=Stale-Dated (§9.5) and routed to the owner with Re-date | Publish anyway | Archive
  And approving a piece older than the ledger rotation window re-runs ledger-lint against the current ledger first
```

**Partial approval of a carousel.** A carousel is one `QueueItem` with N `Asset` slides (`slide_no`, §17). The owner can **approve the piece while sending a single slide back**:
- Per-slide verbs (Light Table controls / `slide_actions` cell): **keep · re-render(note) · drop** — subject to the channel's carousel min/max (§12.3).
- A `re-render` routes **only that slide** to Visual Production; approved slides are **frozen** (not regenerated). The CD render-pass re-runs on the **changed slide + a whole-carousel "visibly-different / coherent set" check** (a new slide must still belong to the set), then the piece returns to the HUMAN GATE.
- The piece **cannot go `Approved`** while any slide is `pending`/`re_render`; slide-level state rolls up to the piece.

```gherkin
Scenario: Approve a carousel but re-render one slide
  Given a 4-slide carousel in the Approval Queue
  When the owner marks slide 3 "re-render" with a note and approves the rest
  Then only slide 3 is regenerated by Visual Production while slides 1, 2, 4 are frozen
  And the CD render-pass re-checks slide 3 and the whole-set coherence before the piece returns to the HUMAN GATE
  And the piece is not marked Approved until every slide is resolved
```

**Minimizing decisions per piece (the anti-fatigue principle).** The design target is **≤1 human decision per shipped piece** (the conductor/orchestrator framing, Day 1):
- **One-tap Approve = approve *and* publish** on the manual path (the Post Kit is built and, if a channel adapter exists, published under the §12.3 precedence + idempotency guard) — the owner never approves *then* separately publishes the same clean piece. A distinct "Approve only (I'll post it)" affordance remains for owners who publish by hand.
- The rich decision context (CD note, lint summary, claim-grounding, loop history — §12.4) exists precisely to make that one decision confident and final, minimizing request-changes round-trips.
- **Bulk approve** collapses N clean pieces into one gesture; the **trust ladder** (§12.3) removes the decision entirely once earned.

---

