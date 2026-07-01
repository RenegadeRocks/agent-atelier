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

## 2. Campaign mode (dates or a seasonal occasion exist)

Campaign mode is **general**: a campaign may attach to an offering from [[OFFERINGS]] **or stand alone** (catalog-wide / seasonal / promo), with an optional `type` hint (`launch | promo | seasonal | collab | ugc | other`).

Triggered by an owner prompt or task carrying the campaign details (offering or standalone occasion, dates where they exist, registration/contact channel, and the per-piece language mix from [[LANGUAGES]]). The Managing Editor activates the **campaign ladder** (awareness → consideration → conversion, per the Offering Content Agent's phases), **layered on top of** the standing week — the steady cadence does not stop during campaigns; it is the trust backdrop that makes campaign posts land. Standalone seasonal campaigns draw from the optional seasonal calendar.

During a campaign week the relevant spotlight slot becomes a campaign slot, and additional campaign posts may be added. The per-brand hard ceiling is **[[MAX_POSTS_PER_WEEK]]**; a campaign may optionally raise it via the campaign override (`campaign_max_posts_per_week`). Beyond a sensible ceiling, engagement cannibalizes — the ceiling is deliberate. Truthful scarcity only; CTAs follow [[CTA_STYLE]] and never use [[CTA_FORBIDDEN_PHRASES]].

## 3. Monthly anchors

- **One research deep-dive** (carousel or long-form) — the Research agent and a Content Agent pair on it; backed by a VERIFIED entry in the Research Bank.
- **One vetted testimonial / proof piece** — consent-flagged pool only; honors [[NON_DISCLOSURE_RULES]] and [[REQUIRED_FRAMING]].
- **Creative Director monthly retro** — reads the ledger, retires tired hooks/shapes, adds new ones to the Creative Engine, and reports to the owner what's working (with engagement numbers only where the owner has shared them).

## 4. Who wakes whom

- The **Managing Editor (orchestrator)** owns a **weekly editorial-calendar task**, created each week: the week's slots, assigned agent roles, and any campaign overlays (including the per-piece language axis from [[LANGUAGES]]). Paused routines resume from here.
- Per-agent routines stay registered but plan against this document's slots.
- **No first-piece self-pause.** Routines keep producing into the approval queue; the human gate is at **publish**, not at production. Nothing publishes without the owner approving in the system of record (Google Sheets/Drive) per [[APPROVAL_MODE]] — so agents can safely keep producing into the queue. A piece without its ledger row, alt text, or a clean lint bounces back before it reaches the queue.

## 5. Owner on-demand asks

The owner can trigger any piece at any time with a prompt to the Managing Editor. Examples (illustrative, brand-resolved): an offering announcement for a dated batch in the brand's language mix, a topical evergreen post tied to current audience pains from [[AUDIENCE_PAINS]], or a seasonal-occasion piece. The Managing Editor routes the ask to the right agent role same-day, keyed by [[OFFERING_ID]] when offering-specific.

---

*Owner: Managing Editor (enforcement); Publishing & Operations Agent (slot tracking + weekly visibility digest). Approval owner: brand owner per [[APPROVAL_MODE]]. Time-of-day windows: [[LOCALE]]. This is a generic, product-agnostic template — bracketed [[TOKENS]] resolve from the Brand Kit registry at build time.*
