<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §9 (source lines 861–1025). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 9. The canon / engine documents (the harness's shared brain)

Generic, version-controlled documents resolved per brand via `[[VARIABLE]]`. Each has an **owner agent** and an **approver** (the human owner).

### 9.1 Creative Engine (owner: Creative Director)

The system that *generates variety* and prevents drab, samey copy. A **single generic canon doc** (it never changes between brands) carrying multiple **hook/shape archetype packs**; `brand_type` selects the active pack(s), and examples within the active pack are regenerated from Brand Kit voice:

- **Educational/editorial pack** (today's twelve hooks + ten shapes): myth-flip, research-reveal, specific-moment, number-contrast, overheard-line, question-that-indicts-the-default, instruction-as-hook, quote-reframe, season/local-anchor, body-first, contrast-pair, honest-curiosity-gap; shapes: aphorism→practice, mini-story, research-reveal, myth-vs-fact, list-of-three, dialogue, day-anchor, practitioner's-note, quote-card, carousel-narration.
- **Product/Commerce pack:** product-hero, UGC/social-proof, before→after, founder-story, behind-the-scenes, launch/drop, tutorial, testimonial, limited-time-offer, trend-jack.
- Add more packs as real brands need them (ship the two above first).

Cross-pack rules (universal): **one-idea rule**; **angle lenses** to turn a flat topic into an idea; **specificity rule** (≥ 1 concrete, sensory, local detail per caption — generic is rejected); **plain-speech guard** (max one poetic fragment; every sentence must pass a "say it plainly to one real person" test; close concrete; never bend sacred/cultural terms); **format rotation** (single image ≤ ~50%/week, carousel the default for teaching, quote card, reel script); **image-first captions** (image is the message; caption adds one line; first line stands alone; hard length cap; soft CTA from `brand_assets`; tight hashtag set); **format-decision rule** (carousel vs single image, consciously, per idea). The CD rotates **within** the active archetype (rotation limits in §9.4).

**Research-grounded minimum.** Honors `research_post_min_per_week` (including **0**). When 0: drop the standing research slot (remove `flag: research_grounded`), reallocate it, and stop ledger/CD/digest enforcement of a research minimum. The Research & Verification Agent remains a constant role (it still vets any factual claims/testimonials that arise, gated by `citation_required_for_claims`).

### 9.2 Visual Engine (owner: Creative Director; operated by Visual Production Agent)

**Variety by message, not a fixed style** (default). Generic content:

- **The only principle** — a feed lives on variety; the image is decided fresh each time from *this* post's message and the feeling it must spark. **Brand cohesion is non-negotiable and already constant per post** — the brand type system (serif headline, accent rule, kicker, logo, wordmark — §11.2), the fixed `palette_hex`, and `visual_register` apply to every post. "Convergence is the bug" targets **dead sameness** (repeated subject/idea/treatment), **not** the brand's consistent identity. For tight-aesthetic brands, capture it via a prescriptive `visual_register` plus the optional `visual_variety: high` dial (narrows the treatment menu while still rotating subject/angle/composition).
- **Emotion-first decision** — answer (1) what is this post saying? (2) what should a stranger feel in one second? then build the image. The full emotional range is in bounds.
- **Treatment menu (choose, don't cycle)** — real human moment, transformation/before→after, candid joy/belonging, intimate detail, place-with-feeling, physical metaphor (must pass the two-second bridge test), bold typographic statement, research/credibility card, illustrated explainer, carousel, texture/abstract.
- **Quality bar (the real constant)** — alive (not empty), warm/human/local, premium/crafted, emotionally true, scroll-stopping, with words-as-craft typography.
- **Metaphor legibility** — on-image words must bridge a metaphor in two seconds.
- **Non-disclosure** — `non_disclosure_rules` bind both the words on the image and the scene depicted (enforced by the CD's post-render multimodal pass, §15.2).
- **Per-image brief** — MESSAGE / FEELING / TREATMENT / IMAGE / WORDS / LIGHT-MOOD / CHECK (stored on the Draft, §17).
- **Image quality tier precedence** — Brand Kit `image_quality_tier` is the **floor/default**; a CD "premium" tag **upgrades** an individual piece to `high` but never downgrades below the floor (`image_quality_tier: high` → every piece high).
- **Craft laws (hard)** — advertising-polish never raw; typography composited never model-baked; concept legible in 2s (use diptych/metaphor for motion/contrast ideas); nothing suggestive; carousels carry the teaching, the outro carries the CTA.

### 9.3 Research / Claim Bank (owner: Research & Verification Agent)

Status model `PENDING → VERIFIED → RETIRED`; locked-wording rules; source allowlist; the **independent verification protocol of §8.2**; `source_hash` + decay/re-verify. Only VERIFIED entries with locked wording may ship; numeric fidelity is additionally enforced deterministically at the publish boundary (§14.2).

### 9.4 Content Ledger + deterministic linter (append: all content agents; lint/audit: Ops; verify: CD)

One feed = one ledger across **all** agents. Every approved piece appends a row: date, piece id, agent, channel/format, **topic→idea sentence**, hook pattern, caption shape, visual treatment **label**, language, status. Killed/rejected ideas are recorded too.

A **deterministic ledger-linter** (reads the Sheets ledger) runs **before CD review** and hard-blocks drafts violating **countable** rules (over a pinned trailing window, e.g. last ~30 rows / each rule's window):
- hook pattern used within the last 3 posts;
- caption shape == immediately prior;
- aphorism shape exceeding 1-in-5 of the trailing window;
- idea re-run within 30 days;
- weekly research-minimum not met (when `research_post_min_per_week > 0`);
- recorded visual-treatment **label** repeated back-to-back.

The linter is what makes the §3.3 "countable rotation violations = 0" claim true. **Rendered-image "visibly different" judgment is NOT in the linter** — it routes to the CD's post-render multimodal pass (§15.2 dim 3); there is deliberately **no rigid gender/age/clothing/posture/lighting hard-block** (that would fight the variety principle). §9.4 prose scopes "mechanically enforces" to exactly the linter-checked rules.

**Exact, deterministic linter windows (Day-5 SDD: a "deterministic gate" with fuzzy windows is not deterministic).** Pin every window, the ordering, and row eligibility so the §3.3 "countable violations = 0" claim is machine-checkable:
- **Ordering:** by `LedgerRow.date` (brand-local, §13), ties by append order, then `piece_id`.
- **Row eligibility:** the rotation rules (hook-in-3, shape==prior, aphorism-1-in-5, treatment-label back-to-back) count only `status ∈ {Approved, Published}` rows; **idea-rerun-30d** counts shipped **and** killed/rejected rows; `RESERVED` rows (below) count for all rules.
- **Exact windows:** hook-in-3 = the 3 most-recent eligible; shape==prior = the single most-recent; aphorism-1-in-5 = ≤1 among the trailing 5 eligible; idea-rerun = `date` within 30×24h; treatment-label = the single most-recent. **Scope = per `brand_id`, feed-wide across channels.**
- **Research-minimum window:** the brand-local ISO week (Mon–Sun in `timezone`, §13); count `research_grounded` rows with `status ∈ {Approved, Published, RESERVED}`; block a non-research draft that would let the week close below `research_post_min_per_week` (when > 0).
- **Close the parallel-draft hole:** because rows append on *approval*, two in-flight drafts are mutually invisible. A content agent **writes a `RESERVED` Ledger row at DRAFT start** (piece_id, intended hook/shape/idea/treatment); the linter counts RESERVED rows; on reject/kill → `KILLED`, on approval → final status. This makes "=0" true **under concurrency**.

```gherkin
Scenario: Two parallel drafts cannot both ship the same hook
  Given two content agents draft into the same week concurrently, and the first writes a RESERVED row with hook "myth-flip"
  When the second's draft also chooses "myth-flip" within the 3-post window
  Then the ledger-linter counts the RESERVED row and hard-blocks the second pre-CD
```


### 9.5 Cadence Plan (owner: Managing Editor; tracked by Ops)

The standing week (from Brand Kit), **campaign mode**, monthly anchors, who-wakes-whom, on-demand asks. **No first-piece self-pause** — routines keep producing into the queue; the human gate is at publish (bounded by the backpressure rule below).

**Queue backpressure (the one bounded exception — prolonged owner absence).** The no-self-pause rule is capped so the engine can never burn budget into a void. When the **Approval Queue depth** exceeds `max_queue_depth` (cadence config; default `2 × posts_per_week_target`) **and** no `Owner Action` has occurred for `owner_absence_pause_days` (default 7), the Managing Editor **pauses standing-week materialisation** — in-flight pieces finish, but no new *routine* pieces are started — raises a **CRITICAL** alert (§14.4.1), and writes a backpressure `AuditEntry` (target `<brand_id>#week:<week_of>`, §17); the Studio Floor (§12.4) shows a paused-materialisation banner and the weekly digest (§8.2) reports it. Production **resumes automatically on any owner action** (approve / reject / edit — the pause is a condition re-evaluated each tick, so no separate resume control is needed). A dated campaign slot and the research minimum are honoured through a pause only if `campaign_overrides_backpressure` is set. This is deliberate cost-governance (Denial-of-Wallet, Day 4) — a **loud, reversible** pause, never a silent stall. (**Reset event:** `days_since_last_owner_action` = time since the most recent `AuditEntry` with `actor=human` for the brand — **any** owner action counts: an approval-queue verb, a Brand-Kit edit, or a Floor intervention.)

```gherkin
Scenario: Prolonged owner absence with a deep queue pauses routine materialisation
  Given the Approval Queue depth exceeds max_queue_depth
  And no owner action (any actor=human AuditEntry) has occurred for owner_absence_pause_days
  When the Monday tick fires
  Then the Managing Editor emits no new routine slots and in-flight pieces finish
  And a CRITICAL alert and a backpressure AuditEntry (target <brand_id>#week:<week_of>) are written
  And the Studio Floor shows a paused-materialisation banner
  When the owner takes any action
  Then routine materialisation resumes on the next tick
```

**Campaign mode is general:** a campaign may attach to an offering **or stand alone** (catalog-wide/seasonal), with an optional `type` hint (`launch | promo | seasonal | collab | ugc | other`). It reuses the Offering Content Agent + Managing Editor (§8.2 phase-1 is the generic "campaign ladder"). `posts_per_week_target` sets the standing weekly volume and `max_posts_per_week` is the per-brand hard ceiling; `campaign_max_posts_per_week` optionally overrides the ceiling during a campaign. Standalone seasonal campaigns draw from the optional `seasonal_calendar`. (Multi-surface/Stories campaigns are noted future work, not launch.)


**Capturing & editing cadence (no hand-authored YAML).** The Strategist captures cadence in plain language and **proposes a default standing week** from `brand_type` + `posting_goal` + `posts_per_week_target` + `offerings[]` (§7.1.1); the owner accepts/swaps slots on the **Planner** — a weekly/monthly visual calendar rendered as Generative UI (Day 2) on the Brand Desk (§12.4) and persisted as the §7.1 structured view. Plain-language prompts map to fields: "How many posts a week feels sustainable?" → `posts_per_week_target`; "Hard ceiling in a busy week?" → `max_posts_per_week`; "Which days, and what on each?" → `standing_week`; "Anything always covered?" → the research slot (`research_post_min_per_week`) + per-offering spotlights; "Any day in a specific language?" → per-slot `language` (§7.6).

**The deterministic cadence validator (gates every cadence edit, exactly as schema validation gates the kit).** A committed cadence change must pass, or it is blocked with the violation surfaced inline:
- `Σ` active (non-`quiet`, non-`blackout`) slots `≤ max_posts_per_week`;
- if `research_post_min_per_week > 0`, at least that many `research_grounded` slots;
- every `offering:<id>` resolves to a real, **non-retired** `offerings[].id` (§7.4);
- campaign overrides honour `campaign_max_posts_per_week`;
- any per-slot `language ∈ languages[]`;
- a `quiet`/blackout day carries no `track`;
- `max_queue_depth` is `null` or an integer `≥ posts_per_week_target`, and `owner_absence_pause_days` is an integer `≥ 1` (the §9.5 backpressure guards).

A cadence change is a **`material`-class §7.7 Edit-Loop** edit (Impact Preview + owner confirm; the Managing Editor owns the plan). It **takes effect at the next Monday tick** (§13.1), optionally applying to this week's not-yet-drafted slots; **already-drafted or queued pieces are never retroactively moved.**

**Conditional-YAML: the Monday-tick composition rule (Day 5 SDD; §9.5 intent → §13.1 Tasks).** The Managing Editor composes the concrete week deterministically:
```yaml
# Managing Editor — weekly cadence composition (consumed at the §13.1 Monday tick)
when: monday_tick
compose_week:
  precondition: |                                 # §9.5 queue-backpressure gate (prolonged owner absence)
    if approval_queue_depth(brand) > (max_queue_depth or 2*posts_per_week_target)
       AND days_since_last_owner_action(brand) >= owner_absence_pause_days:
    then PAUSE — emit NO routine slots (in-flight Tasks finish); honour a dated campaign slot +
       the research minimum ONLY if campaign_overrides_backpressure; write a backpressure AuditEntry;
       raise CRITICAL (§14.4.1); Studio-Floor shows a paused-materialisation banner.
       Resume (normal compose) on the first tick after any Owner Action.
  base:    standing_week                          # recurring template (Brand Kit)
  remove:  [quiet_days, blackout_dates]           # first-class no-post days; win over everything
  overlay: active_campaigns                       # every CampaignPlan whose starts_on..ends_on covers week_of
    overlay_mode:
      add:     append campaign slots up to (CampaignPlan.max_posts_per_week_override or campaign_max_posts_per_week)
      replace: campaign slots take evergreen days first (total volume unchanged)
      boost:   raise the named offering_id's spotlight frequency for the window
  clamp:   total_slots <= ((CampaignPlan.max_posts_per_week_override or campaign_max_posts_per_week) if campaign_active else max_posts_per_week)
    on_over_ceiling: drop lowest-priority first (evergreen -> non-flagship offering);
                     NEVER drop a research_grounded slot while research_post_min_per_week > 0;
                     then surface the trim to the owner (Planner + Friday digest §8.2)
  pin:     brand_kit_version on every materialized Task   # in-flight pieces never shift on later edits
  emit:    one Task per surviving slot { offering_id?, language, flag?, channel, format, slot_id, campaign_id? }
  guard:   idempotent per (brand_id, week_of) via a WeekPlan record   # re-running the tick never double-materializes
  capability_check: slots whose format lacks an auto-publish adapter -> mark manual_publish_only (§12.3)
```
This is the missing bridge that gives §13.1's "Monday create the editorial-calendar task with slots from `cadence_plan`" its exact idempotent, ceiling-clamped, `brand_kit_version`-pinned definition — §9.5 holds the *intent*, this rule turns it into *Tasks*.

```gherkin
Scenario: The Monday tick materializes the standing week into Tasks idempotently
  Given an approved Cadence Plan with a quiet Monday and a flagship spotlight on Wednesday and no active campaign
  When the Managing Editor's Monday tick composes the week
  Then one Task is emitted per non-quiet slot with its offering_id, language, flag, channel, and format
  And no Task is created for the quiet day or any blackout_date
  And total Tasks do not exceed max_posts_per_week
  And every Task is pinned to the current brand_kit_version
  And re-running the tick for the same (brand_id, week_of) creates no duplicate Tasks via the WeekPlan guard

Scenario: A campaign overlays the standing week within the campaign ceiling
  Given an approved standing week of 4 posts and an offering-launch CampaignPlan with overlay_mode add and campaign_max_posts_per_week 8
  When the campaign window covers the current week
  Then campaign slots are appended to the standing week up to the campaign ceiling
  And if the total would exceed 8, evergreen slots are dropped first and a research_grounded slot is never dropped while research_post_min_per_week > 0
  And the trim is surfaced to the owner on the Planner and in the Friday digest
```

**Stale-piece / slot-expiry (Day-5 HITL: a dated window is a structural correctness check, not a judgment call; Day-1 orchestrator tick). Time-anchored content must never publish silently late.**
- Every piece carries `target_date` (its slot, brand-local, §13). At HUMAN GATE / PUBLISH, if `now > target_date + stale_grace_days` (config, default **2**) the piece is set **`exception=Stale-Dated`** (§17), removed from auto-publish eligibility **even in auto mode**, and routed to the owner: **Re-date** (new slot, re-lint), **Publish anyway**, or **Archive**.
- **Date-anchored content auto-archives** past its window (a campaign past its end, a seasonal hook past its dates) with a logged reason.
- **Idle-queue escalation:** any item sitting in `Approval Queue` past the configured staleness threshold raises a routine reminder (§14.4.1 ACTION tier) and pins it in the §12.4 "Needs You" tray — nothing waits forever for a human.
- Stale pieces surface in the Friday visibility digest (§14.5).

```gherkin
Scenario: An approved piece does not publish silently stale
  Given an auto-publish-enabled brand and a piece whose target_date passed 3 days ago (grace 2)
  When publishing would run
  Then it is held as exception=Stale-Dated and routed to the owner (Re-date | Publish anyway | Archive), never auto-published after its window
```


### 9.6 Brand Voice, Channel Style Guides, Visual Style Guide, Brand Assets

Voice and per-channel mechanics (length, hook position, hashtags — **count delegated to the per-channel Style Guide**, not hardcoded — CTA discipline), visual mechanics, and the brand identity/contact/CTA facts — all resolved from the Brand Kit. Channel Style Guides also instruct authoring the first caption line and alt text to read naturally searchable (light IG-SEO; no keyword-stuffing; still subject to §9.1 rules). The **alt-text authoring rules** (length, what to describe vs omit, and that non-disclosure binds alt text too) live in each channel Style Guide and are **drafted during the build (P3)**, not pre-specified in this PRD.

---

