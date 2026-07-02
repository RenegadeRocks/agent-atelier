# Cadence & Operating Rhythm — [[BRAND_NAME]] ([[BRAND_SHORT_NAME]])

> The studio's primary job is **always-on, on-brand content on a steady drumbeat** that keeps [[CHANNELS]] alive and credible regardless of any offering schedule. On top of that: **weekly offering spotlights even when nothing is dated** (education builds the audience that campaigns later harvest), and **campaign mode on demand** when dates or a seasonal occasion exist. This document is the schedule the agents plan around. The Publishing & Operations Agent's time-of-day windows continue to govern *when* within a day a slot publishes (in [[LOCALE]]); this document governs *what* fills the week.

## 1. The standing week (default, no active campaign)

The standing week is resolved from **[[STANDING_WEEK]]** in the Brand Kit and written into the system of record (Google Sheets/Drive) as the week's slot map. Each slot names a day, a content emphasis, and an owning agent role. A typical resolved shape:

| Slot | Emphasis | Owner role | Notes |
|------|----------|------------|-------|
| Evergreen slot(s) | Any pillar from [[EVERGREEN_PILLARS]] | Pillar Content Agent | Rotate per the Creative Engine; never repeat last week's hook/shape (enforced by the deterministic ledger-linter). |
| Offering spotlight slot | One spotlight per active offering in [[OFFERINGS]] | Offering Content Agent (brief-per-task, keyed by [[OFFERING_ID]]) | Education / curiosity / FAQ / vetted testimonial about the offering — **no dates needed.** Loads the relevant [[OFFERING_NAME]] / [[OFFERING_BRIEF]] as per-task context. |
| Research-grounded slot | Pillar content carrying a VERIFIED claim | Pillar Content Agent + Research agent | The week's anchor of credibility. **At least [[RESEARCH_POST_MIN_PER_WEEK]] per week** must be a research-grounded piece (enforced by the ledger-linter's research-min rule). |
| Optional weekend / community slot | Lighter register, community / quote / behind-the-scenes | Content Agent (Managing Editor discretion) | Not mandatory; drawn from [[LOCAL_DETAIL_BANK]] where it adds texture. |

This yields a steady evergreen drumbeat plus one spotlight per active offering per week — hype without dates, exactly as intended. The standing weekly volume targets **[[POSTS_PER_WEEK_TARGET]]** posts and never exceeds the per-brand ceiling of **[[MAX_POSTS_PER_WEEK]]** (§2). Cross-post each piece to the other surfaces in [[CHANNELS]] using each channel's style adaptation where it adds value — never a blind copy-paste of captions or hashtags.

**First-class no-post days.** `quiet_days` (recurring weekday tokens, `track: quiet`) and `blackout_dates` (dated brand-closed windows) are honored at materialization and **win over everything** — a quiet/blackout day carries no track. They are distinct from `weekend: optional` (which MAY fill).

**The cadence validator (gates every cadence edit, PRD §9.5).** A committed cadence change must pass or it is blocked with the violation named inline: Σ active slots ≤ `max_posts_per_week` · at least `research_post_min_per_week` research-grounded slots when > 0 · every `offering:<id>` resolves to a real, non-retired offering · campaign overrides honor `campaign_max_posts_per_week` · any per-slot language ∈ [[LANGUAGES]] · quiet/blackout days carry no track · `max_queue_depth` is null or ≥ `posts_per_week_target` and `owner_absence_pause_days` ≥ 1. A cadence change is a `material`-class edit (Impact Preview + owner confirm) and **takes effect at the next Monday tick** — already-drafted or queued pieces never retroactively move.

## 2. Campaign mode (dates or a seasonal occasion exist)

Campaign mode is **general**: a campaign may attach to an offering from [[OFFERINGS]] **or stand alone** (catalog-wide / seasonal / promo), with an optional `type` hint (`launch | promo | seasonal | collab | ugc | other`).

Triggered by an owner prompt or task carrying the campaign details (offering or standalone occasion, dates where they exist, registration/contact channel, and the per-piece language mix from [[LANGUAGES]]). The Managing Editor activates the **campaign ladder** (awareness → consideration → conversion, per the Offering Content Agent's phases), **layered on top of** the standing week — the steady cadence does not stop during campaigns; it is the trust backdrop that makes campaign posts land. Standalone seasonal campaigns draw from the optional seasonal calendar.

During a campaign week the relevant spotlight slot becomes a campaign slot, and additional campaign posts may be added. Overlays apply per the campaign's **`overlay_mode`** (§9.5): **`add`** appends campaign slots up to the campaign ceiling · **`replace`** lets campaign slots take evergreen days first (total volume unchanged) · **`boost`** raises the named offering's spotlight frequency for the window. The per-brand hard ceiling is **[[MAX_POSTS_PER_WEEK]]**; a campaign may optionally raise it via the campaign override (`campaign_max_posts_per_week`, or a per-campaign `max_posts_per_week_override`). **On over-ceiling, drop lowest-priority first (evergreen → non-flagship offering), NEVER a research-grounded slot while the minimum > 0, and surface the trim to the owner** (Planner + Friday digest). Beyond a sensible ceiling, engagement cannibalizes — the ceiling is deliberate. Truthful scarcity only; CTAs follow [[CTA_STYLE]] and never use [[CTA_FORBIDDEN_PHRASES]].

**Dated pieces go stale, never silently late (§9.5).** A piece whose `target_date` + grace has passed while it waited (e.g. in the approval queue) is set `exception = Stale-Dated` and routed to the owner with three choices — **Re-date · Publish anyway · Archive** — never auto-published late.

## 3. Monthly anchors

- **One research deep-dive** (carousel or long-form) — the Research agent and a Content Agent pair on it; backed by a VERIFIED entry in the Research Bank.
- **One vetted testimonial / proof piece** — consent-flagged pool only; honors [[NON_DISCLOSURE_RULES]] and [[REQUIRED_FRAMING]].
- **Creative Director monthly retro** — reads the ledger, retires tired hooks/shapes, adds new ones to the Creative Engine, and reports to the owner what's working (with engagement numbers only where the owner has shared them).

## 4. Who wakes whom (the Monday tick)

- The **Managing Editor (orchestrator)** composes the week **deterministically at the Monday tick** (§9.5): backpressure precondition → base `standing_week` → remove quiet/blackout → overlay active campaigns → clamp to the ceiling → pin `brand_kit_version` on every Task → emit one Task per surviving slot — **idempotent per (brand_id, week_of) via a WeekPlan record** (re-running the tick never double-materialises). Slots whose format lacks an auto-publish adapter are marked `manual_publish_only` (§12.3). Paused routines resume from here.
- Per-agent routines stay registered but plan against this document's slots.
- **No first-piece self-pause — with ONE bounded exception (§9.5 backpressure).** Routines keep producing into the approval queue; the human gate is at **publish**, not at production. Nothing publishes without the owner approving in the system of record (Google Sheets/Drive) per [[APPROVAL_MODE]] — so agents can safely keep producing into the queue. **Exception:** when queue depth exceeds `max_queue_depth` AND no owner action for `owner_absence_pause_days`, the Monday tick pauses routine materialisation — loud (CRITICAL alert + backpressure AuditEntry + Studio-Floor banner + digest line), reversible (any owner action resumes it), never a silent stall. A piece without its ledger row, alt text, or a clean lint bounces back before it reaches the queue.

## 5. Owner on-demand asks

The owner can trigger any piece at any time with a prompt to the Managing Editor. Examples (illustrative, brand-resolved): an offering announcement for a dated batch in the brand's language mix, a topical evergreen post tied to current audience pains from [[AUDIENCE_PAINS]], or a seasonal-occasion piece. The Managing Editor routes the ask to the right agent role same-day, keyed by [[OFFERING_ID]] when offering-specific.

---

*Owner: Managing Editor (enforcement); Publishing & Operations Agent (slot tracking + weekly visibility digest). Approval owner: brand owner per [[APPROVAL_MODE]]. Time-of-day windows: [[LOCALE]]. This is a generic, product-agnostic template — bracketed [[TOKENS]] resolve from the Brand Kit registry at build time.*
