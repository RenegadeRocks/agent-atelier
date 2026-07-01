<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §7 (source lines 233–791). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 7. The Brand Kit — product-agnostic configuration (core innovation)

This is the heart of the rebuild. Everything that is brand-specific lives here; the agents and engine reference it via placeholders and dynamic retrieval. The mechanism is based on the course's **context-resolver pattern** (Day 5): canon and agent text contain `[[VARIABLE]]` placeholders resolved at runtime from the Brand Kit (with environment fallback).

**Two resolution targets, one mechanism.** The resolver substitutes into **two distinct destinations**: (a) **brand facts / voice / canon values** → substituted into model-visible prompt and canon text; (b) **secret references** (image-provider / Google / Instagram tokens) → resolved **only into the tool/MCP auth layer** (env vars / request headers) at call time, **never into model-visible context**. This doubles as context hygiene (§14.6): secrets and PII are never inlined into prompts.

### 7.1 Intake experience — a guided brand interview, not a dead form

Per owner direction, onboarding must be **intuitive**, not a static form. Design:

- **Primary: a conversational Brand Onboarding Agent ("the Strategist").** It interviews the owner in plain language, asks **one question at a time**, proposes sensible defaults the owner can accept, and can **ingest existing material** (a website URL, an existing Instagram handle, a brochure/PDF, a logo image) to auto-draft answers the owner then confirms. It uses the **read/draft/act ladder**: it reads/drafts the Brand Kit; the owner *acts* (approves).


**Five on-ramps, one converged kit (widest net, lowest friction).** Onboarding must fit a brand with a polished brand guide and a brand with nothing but an idea. The Strategist opens with a fork; all five converge on the same validated Brand Kit and the same explicit safety interview: **(a) website URL · (b) Instagram/social `@handle` · (c) PDF/brochure brand guide · (d) uploaded assets** (logo, fonts, product shots) **· (e) start-from-scratch.** On-ramps (a)–(d) are **multi-modal ingestion**: each is fetched through a **sanitized, non-interactive `source_ingest` tool** (Day 2 MCP; §14.3 — no free-browsing of arbitrary pages) that **auto-drafts the NON-safety fields as PROPOSED values**, each tagged with **provenance** and a **confidence**. The owner then confirms a **diff**, never a blank form — the read/draft/act ladder (Day 3): sources + Strategist *draft*, the owner *acts*.

**Source → field drafting map (safety is never on this map).**

| Source | Auto-drafts (proposed, non-safety only) | Never touches |
|---|---|---|
| **Website** | `brand_name`, `tagline`, `mission`, `offerings[]` (name/one_liner), `evergreen_pillars` candidates, `contact_*`, `palette_hex` | the three fail-closed fields |
| **Social `@handle`** | `voice_descriptors` + `sample_lines_good` (from real captions), `visual_register` + `palette_hex`, observed `posts_per_week`, `desired_feeling` hint | the three fail-closed fields |
| **Brand-guide PDF** | `voice_do/dont`, `palette_hex`, fonts, `wordmark_text`, `visual_register`, `tagline`, `mission` — the richest source | the three fail-closed fields |
| **Uploaded assets** | `palette_hex`, `accent_dark_bg`/`accent_light_bg`, `headline_font`/`label_font`, `visual_strategy: product_led`, `people_pool`/`product_pool` seeding | the three fail-closed fields |

- **Provenance + confidence per field.** Every drafted value records `field_provenance` (`ingested_web|ingested_social|ingested_pdf|ingested_asset`) + a confidence; the Readiness Report and later Vibe Diffs (§7.7) show *where a value came from* ("drafted from your website — confirm?" vs "you typed this").
- **Confirm-a-diff, not a form.** One-tap **accept all high-confidence**; field-by-field for low-confidence — the owner *reacts* to a pre-drafted brand.
- **Multi-source merge.** Conflicts are **surfaced, never silently merged** (default precedence brand-guide PDF > website > social > asset-derived, always owner-confirmed).
- **Graceful partial failure.** A 404, a private handle, or an unparseable PDF **degrades to the interview** for those fields and is recorded on an **`IngestionSource`** (defined inline: `status: failed|partial|unsupported`, verbatim error) — ingestion is best-effort **acceleration, never a dependency**; nothing blocks.
- **THE SAFETY FIREWALL (load-bearing, Day 4 supply-chain).** No ingestion path — **not even a brand guide that literally contains a "never say" list** — may *confirm* a fail-closed field. A source's prohibitions may be surfaced as **proposed-unconfirmed starting points** into the explicit safety interview, but always pass the §7.1 worked-example elicitation before they gate publish. Marketing sources describe what to **DO**; the fail-closed fields are what a brand must **NEVER** do, and that is elicited from the human, consciously, every time (§14.2).

```gherkin
Scenario: The safety firewall keeps an ingested prohibition unconfirmed
  Given an uploaded PDF brand guide that literally contains a "never say" list
  When the Strategist parses it
  Then any prohibition it finds is surfaced as a proposed-unconfirmed starting point into the explicit safety interview
  And no fail-closed field is auto-confirmed from the PDF
  And the owner must pass each prohibition through the worked-example elicitation before it can gate publish

Scenario: Ingestion partial-failure degrades gracefully and never blocks
  Given the owner provides a website URL that 404s and a private social handle
  When the Strategist attempts ingestion
  Then each attempt is recorded as an IngestionSource with status failed or unsupported and the verbatim error
  And the affected fields fall back to the archetype defaults and the interview
  And onboarding continues without blocking on the failed sources
```
- **Safety fields are categorically different (see §14.2 and §15.1).** The Strategist must **not silently auto-draft** `claims_forbidden`, `non_disclosure_rules`, or `required_framing` from ingested marketing sources (which structurally never contain prohibitions). It may *propose* category/regulatory defaults inferred from `regulatory_notes` / the detected vertical, but must flag them as starting points and **elicit each prohibition explicitly**, with 1–2 worked examples per field. **First-light deliberately generates a near-violation** to surface unstated prohibitions before go-live — **by pattern:** it steers a seed toward a **representative** declared prohibition (e.g. a `claims_forbidden` entry) and writes a caption that crosses it by **exactly one degree** (clearly over the line), plus one **undeclared probe** — a category from the archetype's §7.8 safety table the owner did *not* confirm (for a `custom`/blank archetype — or any `brand_type` lacking a §7.8 safety row — draw from a generic cross-vertical risk list: political tie-in, comparative/superiority claim, medical/financial guarantee, minors). **One declared + one undeclared probe per run**, bounded by the §13.2 breaker; the safe hedge **and** the blocked near-miss are both shown to the owner (full spec in the first-light two-artifact section below).


**The safety interview (always LAST, always explicit, never ingested).** The three fail-closed fields are elicited in three short guided passes; each carries an **archetype-scoped worked example** (proposed-unconfirmed, §7.8) and requires an **active confirmation** — even to say "none":
- **Pass 1 — `claims_forbidden` ("What must we never claim?").** *"What promises must your brand NEVER make — the ones that would be untrue, unsafe, or land you in trouble?"* Worked example (clinic archetype): *"e.g. 'cures anxiety', 'guaranteed results', 'FDA-approved' — do these apply? Add your own."* `comparative_claims_allowed` and `political_content_allowed` are asked here as explicit yes/no (default `false`).
- **Pass 2 — `non_disclosure_rules` ("What must never be shown or spelled out — in words OR image?").** *"Anything proprietary, private, or sacred that must never appear — a secret recipe, a client's identity, a technique's mechanism, a minor's face?"* Reinforces that the rule binds **both the words and the depicted scene** (§9.2/§15.2).
- **Pass 3 — `required_framing` ("What can we discuss only with a caveat?").** *"Any topics you CAN cover but only with a hedge — 'results vary', 'in studies', 'consult a professional'?"* Captured as `{topic, framing}` pairs.

**Discipline (fail-closed, Day 5 HITL).** **Empty ≠ none** — a blank field is *unknown* and publish **fails closed** (§14.2); the owner must actively confirm "yes, nothing here," which records an attestation the Readiness Report shows as ✅ (distinct from an untouched ⛔ blank). **Archetype proposals are starting points, never satisfaction** (§7.8) — the archetype cannot close the gate for you. **Ingestion never populates these** (the §7.1 safety firewall).

```gherkin
Scenario: Empty is not none — a safety field requires a conscious pass
  Given the owner reaches the claims_forbidden pass and has typed nothing
  When the owner tries to advance without acting on the field
  Then the Readiness Report shows claims_forbidden as safety-unconfirmed (block), not optional-empty
  And advancing requires the owner to explicitly confirm "yes, nothing here" which records an attestation
  And an archetype safety proposal alone never satisfies the field
```
- **Output:** a complete, validated **Brand Kit** (YAML + asset files) plus a short human-readable "brand one-pager."
- **Editable structured view (secondary):** the Brand Kit is also exposed as an editable structured view (a Google Sheet/Form-backed surface is acceptable) so a power user can tweak fields directly without the interview.


**The intake script (ordered; one decision per turn; defaults pre-filled; any step skippable/returnable).** The Strategist runs the read/draft/act ladder (Day 3) with progressive disclosure (Day 1). Cadence sits in the **middle** (step 6) so it can draw on goals and offerings already gathered; the three fail-closed safety fields stay **last** and categorically separate.
0. **Pick a starting point** — the on-ramp fork above.
1. **Identity & mission** — `brand_name`, `brand_short_name`, `tagline`, `locale`, `timezone`, `languages[]`, `mission`, `brand_type` (drafted from sources; confirmed).
2. **Audience & voice** — via the **intent spine** below (Q1–Q3).
3. **Visual identity** — `logo_asset`, `palette_hex`, fonts, `visual_register` (drafted from the logo/site).
4. **Offerings (one at a time)** — each yields an Offering Brief (§7.4); the Strategist asks "weekly education, or a dated launch?" so cadence already knows which offerings need a spotlight vs a campaign.
5. **Intent & capacity** — intent-spine Q4–Q6 → `posting_goal`, `weekly_capacity`, `primary_cta`, `evergreen_pillars`. These plus `brand_type` and the offerings list are the **entire** input to the cadence proposal.
6. **The Cadence Studio (the centerpiece, §7.1.1)** — propose-or-state → previewable calendar → drag-edit → approve in one decision.
7. **Safety fields (LAST, fail-closed, never auto-drafted)** — the three-pass worked-example elicitation below.
8. **Publishing prefs** — `approval_mode` default `human`; `auto_publish_enabled` stays off (§12.3).
9. **First light** — the near-violation safety probe + the first-week dry-run below.
10. **Output** — a validated Brand Kit (YAML + assets), the human one-pager, the approved Cadence Plan, and the first-week preview.

**The intent spine (six questions; one per turn; every answer pre-filled and echoed back).** It captures **intent — outcome and feeling, not config**; each answer is proposed (ingestion → archetype default → tenant default), echoed for confirmation, and mapped to fields (defined in §7.2):
1. *"In one sentence — what do you make or do, and who is it for?"* → the elevator line → identity + an `offerings[]` hint.
2. *"Who exactly is the one person you're talking to?"* → `audience_persona`, `audience_pains`, `scroll_test_persona`.
3. *"When that person sees your post and **doesn't** keep scrolling — what do you want them to feel?"* → `desired_feeling`, which seeds `voice_descriptors` **and** the §9.2 Visual Engine's "what should a stranger feel in one second." *The pivotal intent question — feeling, not features.*
4. *"What's the job of this account right now — get known, build community, or get signups?"* → `posting_goal` (`awareness|community|conversion`), the read-in for the §7.1.1 cadence proposal.
5. *"When someone's ready, what's the one thing you want them to do — and where does it go?"* → `primary_cta` + `cta_destination` + `cta_style` (used **EXACTLY**, never invented — §7.2 contact rule).
6. *"What could you talk about all day without running out — and what's simply not you?"* → `evergreen_pillars` + `off_brand_notes` (taste-level "not us," **distinct from the fail-closed safety fields**).

**The north-star `intent_statement`.** The six answers assemble into **one sentence**, shown back for confirmation and stored: *"[Brand] helps [audience] [outcome] so they feel [feeling]; the next step we ask for is [CTA]."* Every agent that makes a judgment call — the Creative Engine (§9.1), the Visual Engine (§9.2), the Creative Director (§15.1) — reads it, so **"on-brand" has one explicit referent** instead of vibes. Editing it later is a judged-target change that stales the golden set (§15.3).

**Progressive disclosure (novice and expert on the same script).** The spine + one offering + the explicit safety pass (~12 decisions) plus archetype defaults (§7.8) is enough to first-light in minutes — the **novice fast-path** ("I've filled the rest from your [archetype] starter — review any of it, or shall we light it up?"). An **expert** expands any section to its full field set ("show me everything in voice") or edits the structured view directly. Always **one decision per turn**; a skipped optional field stays archetype-default and shows ⚠ optional-empty on the Readiness Report (non-blocking).

**Resumable, recoverable interview.** The interview is checkpointed to a durable **IntakeSession** (defined inline) after every answer (`step_cursor`, answered/drafted/confirmed fields, `pending_safety_fields[]`, `ingested_sources[]`, `resume_token`). The owner may stop and resume from a link; the Strategist replays "we left off at Visual identity — shall I continue?" A half-finished brand is `Brand.status = draft` and schedules **no** production (§13.2) until first light passes; an abandoned draft surfaces as a "Resume draft brand" card on the Brand Desk (§12.4).

**Live Readiness Report ("what's missing").** At any point the Strategist and the Brand Desk render a deterministic checklist over the schema's required/optional split (§7.2.1), the confirmed `intent_statement`, and the three fail-closed fields, with three states: ✅ confirmed · ⚠ optional-empty (fine) · ⛔ required-missing **or** safety-unconfirmed. It distinguishes an untouched safety blank (⛔) from a conscious empty-with-attestation (✅). **First light requires zero ⛔; publish requires the safety fields confirmed** (fail-closed).

**Editing a brand after onboarding (three governed entry points, one save path — §7.7).** Onboarding is the *first* capture; editing is forever. All edits funnel through the §7.7 Edit Loop: (1) **re-enter the Strategist** scoped to the field(s) you name ("change my voice", "add an offering", "I'm closed for two weeks"); (2) the **editable structured view** for power users; (3) the **Brand Desk / Planner** (§12.4). No surface writes `brand_kit.yaml` by any other route.

```gherkin
Scenario: The intent spine assembles and confirms a north-star statement
  Given the owner answers the six intent-spine questions one at a time
  When the Strategist assembles the answers
  Then it shows one sentence in the form "[Brand] helps [audience] [outcome] so they feel [feeling]; the next step is [CTA]"
  And on confirmation it stores intent_statement and sets desired_feeling, primary_cta, and cta_destination
  And the Creative Engine, Visual Engine, and Creative Director read intent_statement as the on-brand referent

Scenario: Resume an interrupted brand interview
  Given an owner began onboarding and the interview reached the Visual identity section
  And the owner closed the session before confirming the safety fields
  When the owner returns via the resume link
  Then the Strategist restores the IntakeSession at step_cursor with all answered and drafted fields intact
  And the brand remains status=draft and has scheduled no production runs
  And the Readiness Report still shows the safety fields as unconfirmed (block)

Scenario: Readiness Report gates first light but tolerates optional gaps
  Given a brand with all required fields confirmed, the safety fields attested, and seasonal_calendar left empty
  When the owner requests first light
  Then the Readiness Report shows zero required-missing or safety-unconfirmed items and the optional-empty item does not block
  And first light proceeds to commission the end-to-end test post
```
- **First-light confirmation:** after compiling the kit, the Strategist commissions one test post end-to-end and shows it to the owner.


**First light is a safety PROOF, not a demo — two artifacts.**
- **The near-violation probe (online eval, Day 4).** The Strategist commissions the end-to-end test post and **deliberately steers the idea toward the brand's declared fault lines** — **one representative probe per run** (if `claims_forbidden` includes "cures anxiety," the seed is a stress-relief post a careless writer would over-claim), showing **both** the correctly-hedged safe output **and** the **blocked near-miss variant** so the Policy Server / CD guard **visibly fires** (§14.2/§15.1). It also runs **one undeclared probe** — an idea in a category the owner did *not* flag (a common archetype risk: a political tie-in for an NGO, a comparative claim for a SaaS); if the owner recoils ("we'd never post that"), the **newly-surfaced prohibition loops back** through the safety interview. First light thus doubles as an **intent-completeness check**. The probe is a single piece + its blocked variant, bounded by the **run cost circuit-breaker** (§13.2) so it can never become a Denial-of-Wallet surface.
- **The first-week dry-run.** The Managing Editor materializes the *upcoming* week's slots from the just-approved cadence into draft Tasks (no publish, §9.5) so the owner watches the Studio Floor populate with their **actual** calendar, not a template — the floor "coming alive" (§12.4) is the cadence made concrete.

A passed first light flips `Brand.status` **draft → active** and unlocks scheduling (§13.2); a surfaced gap returns the brand to **draft** until re-attested. A **`FirstLightResult`** (defined inline) records the declared/undeclared probes, surfaced prohibitions, and cost.

```gherkin
Scenario: First light probes a declared field and surfaces an undeclared one
  Given a brand whose claims_forbidden includes "cures anxiety" and a passed Readiness Report
  When first light runs
  Then the Strategist presents both a correctly-hedged safe output and a blocked near-miss for the declared field
  And it additionally probes a common archetype category risk the owner did not flag
  And if the owner recoils the new prohibition loops through the safety interview and Brand.status stays draft
  And total generation stays within the run cost circuit-breaker and a FirstLightResult is recorded

Scenario: First light includes a first-week dry-run of the cadence
  Given the owner has just approved the Brand Kit and Cadence Plan
  When first light runs
  Then the Managing Editor materializes the upcoming week's slots into draft Tasks with no publish
  And the Studio Floor populates with the owner's actual calendar rather than a template
```

```gherkin
Scenario: Onboard a brand by interview with optional source ingestion
  Given a new owner with a product to market
  And optionally a website URL, an existing social handle, and a logo file
  When the Brand Onboarding Agent conducts the intake
  Then it asks one question at a time and proposes defaults
  And it drafts non-safety answers from any provided sources for the owner to confirm
  And it elicits each safety-prohibition field explicitly with worked examples
  And it produces a Brand Kit that passes schema validation
  And it generates one end-to-end "first light" test post (including a deliberate near-violation) for approval
  And no agent code or engine document was modified
```

### 7.1.1 The Cadence Studio — capturing and negotiating the rhythm

Cadence is captured the way a producer plans a season, not the way a form collects a number. Owners never hand-author `standing_week` YAML. Two doors, one outcome (a confirmed `standing_week`):

**Door A — STATE it.** The owner types or says the rhythm in plain language; the Strategist parses it into a draft `standing_week`, **echoes it back for confirmation** ("3 feed posts + 1 Sunday reel, Mon/Thu/Sat quiet — right?"), then shows the calendar — a confirmed handoff, never a silent guess. Worked example — *"3x a week, plus a reel on Sundays, keep Mondays quiet"*:
```yaml
standing_week:
  mon: { track: "quiet" }
  tue: { track: "evergreen" }
  wed: { track: "offering:<flagship-id>" }
  thu: { track: "quiet" }
  fri: { track: "evergreen" }
  sat: { track: "quiet" }
  sun: { track: "evergreen", format: "reel" }   # reel -> manual_publish_only at materialization (§12.3/§19)
posts_per_week_target: 4
```

**Door B — PROPOSE it.** If the owner has no rhythm in mind, the Strategist proposes one from `brand_type` + `posting_goal` + `weekly_capacity` + the offerings list, drawing the starter shape from the **Cadence Template** attached to the brand archetype (§7.8). **Every proposed slot carries a one-line reason** ("Wed = flagship spotlight because you said conversion is the goal"; "1 research-grounded slot because `research_post_min_per_week: 1`"). The owner accepts, dials volume up/down, or drags slots. Read/draft/act (Day 3): the Strategist drafts; the owner acts.

**What the capture covers (all editable on the calendar, rendered as A2UI, Day 2):**
- **Standing week** — per-day `{ track, language?, flag?, format?, channel?, notes? }` where `track ∈ evergreen | offering:<id> | quiet | optional`. The **research slot stays the existing `flag: research_grounded`** on an evergreen track (preserving §9.4 enforcement); the Planner renders it as its own "research" lane. **`quiet` is a new first-class track** — an explicit no-post day, distinct from `optional` (may post if capacity allows).
- **Per-offering rhythm** — each offering's spotlight frequency (defaults: `is_flagship` → weekly; others → fortnightly); the Planner shows each offering as its own lane.
- **Topical mix** — the evergreen/offering ratio shows as a mix bar ("60% evergreen · 30% offerings · 10% research"). `evergreen_rotation` is the *intent*; the deterministic ledger-linter (§9.4) is the *enforcement*. **Cadence proposes variety; the linter guarantees it.**
- **Language per slot** — a slot may pin `language` (§7.6); otherwise default = primary.
- **Quiet days & blackout dates** — `quiet_days` (recurring weekday tokens) and `blackout_dates` (holidays, closures, founder travel). Blackouts always win at materialization (no post, no Task).
- **Channels per slot** — defaults to the brand's `channels[]`; a slot can target a subset. Slots whose `format` has no auto-publish adapter (e.g. `reel`) are flagged `manual_publish_only` (§12.3/§19).

**The campaign overlay (standing week vs campaign, made precise).** A campaign is **not** a different standing week — it is a **time-boxed overlay** captured after the standing week is approved ("Anything time-boxed coming — a launch, a sale, a season?"). It persists as a `CampaignPlan` (§17) with `starts_on`/`ends_on`, an optional `offering_id` (or standalone/seasonal, §9.5), a `type` hint (launch|promo|seasonal|collab|ugc|other), and an `overlay_mode`:
- `add` — append campaign slots on top of the standing week, up to `campaign_max_posts_per_week`.
- `replace` — campaign slots take evergreen days first (total volume unchanged — for capacity-constrained brands).
- `boost` — raise the named offering's spotlight frequency for the window.
Standalone seasonal campaigns draw from `seasonal_calendar`. Campaigns are also addable later from the Planner without re-onboarding.

**Cost-aware approval (Day 1 economics / Day 4 Denial-of-Wallet, moved upstream into planning).** The Cadence Preview shows a projected **weekly image spend + token budget** for the planned volume (from per-agent / per-`offering_id` budgets, §13.2). A campaign that would push the week past ~80% of budget shows the projection in **amber before approval** — the owner sees the economic consequence of a cadence, not the bill afterward. Approving a whole week's plan is **one decision replacing 5–8** (Day 5 HITL, against approval fatigue); a spend-raising cadence change routes through the §14.4 Vibe Diff.

**Mid-week edits (timing rule).** Cadence edits are non-safety config changes (a `material`-class §7.7 edit). By default they apply at the **next Monday tick** (next `WeekPlan`, §9.5), never retroactively — already-materialized Tasks keep running, pinned to their `brand_kit_version`. The owner may choose "apply to this week," which re-composes the **remaining** days additively (never deletes a Task already in REVIEW/QUEUE).

```gherkin
Scenario: Propose a cadence from brand type and goals, then tweak and approve in one decision
  Given an owner who has given brand_type, posting_goal, weekly_capacity, and one flagship offering
  And the owner has no fixed rhythm in mind
  When the Cadence Studio runs
  Then the Strategist proposes a standing_week from the matching Cadence Template
  And every proposed slot shows a one-line reason and the research_grounded slot is included
  And the proposal renders as an editable weekly calendar with a projected weekly spend
  When the owner drags the flagship spotlight from Wed to Tue and marks Monday quiet
  Then the standing_week and posts_per_week_target update live and stay within max_posts_per_week
  And approving the calendar writes the Cadence Plan in one decision

Scenario: The owner states a rhythm in plain language
  When the owner says "3 times a week plus a reel on Sundays, keep Mondays quiet"
  Then the Strategist drafts a standing_week with 3 feed slots, a Sunday reel slot, and Monday quiet
  And it echoes the parsed rhythm back for confirmation before saving
  And the Sunday reel slot is flagged manual_publish_only because no auto-publish adapter exists for reels

Scenario: A mid-week cadence edit applies next week and never disturbs in-flight pieces
  Given a piece already in QUEUE for the current week pinned to its brand_kit_version
  When the owner changes the standing week on the Planner on Wednesday
  Then the cadence validator confirms the week stays within max_posts_per_week
  And the in-flight piece is unchanged
  And the change first takes effect at next Monday's WeekPlan
  And choosing "apply to this week" only adds remaining-day slots and deletes no existing Task
```



### 7.2 Brand Kit schema

Stored as `brand_kit.yaml` plus an `assets/` folder (logo, fonts, a `people/` pool and a `products/` library) and a secrets reference. Flat where possible (course guidance: keep YAML nesting ≤ 3).

```yaml
# brand_kit.yaml — the entire product-specific configuration surface
brand_kit_version: 2

# --- Identity ---
brand_name: "<e.g. Acme Coffee Roasters>"
brand_short_name: "<full brandmark line, e.g. Acme · Ludhiana>"   # distinct from wordmark_text (the short locator under the logo)
tagline: "<one line>"
locale: "<primary locale, e.g. en-IN / Ludhiana, Punjab>"
languages: ["<primary>", "<secondary, optional>"]   # primary = first entry (see §7.6 language rule)
timezone: "<IANA tz, e.g. Asia/Kolkata>"
mission: "<1-2 sentences: why this brand exists; anchors agent judgment>"
brand_type: "educational"      # content-strategy archetype: educational | product_commerce | ... (selects hook/shape packs, §9.1)


# brand_type archetypes (§7.8 BrandTemplate) — each maps to exactly ONE §9.1 pack (educational_editorial | product_commerce); archetype breadth != pack count:
#   educational | product_commerce | nonprofit_ngo | saas_b2b | hospitality_local | clinic_health | coaching_creator | ecommerce_dtc | school_education | custom

# --- Audience ---
audience_persona: "<the one reader in the writer's head; concrete>"
audience_pains: ["<pain 1>", "<pain 2>"]
scroll_test_persona: "<who must stop scrolling — used by the quality gate>"


# --- Intent (north-star capture, §7.1) ---
intent_statement: "<[brand] helps [audience] [outcome] so they feel [feeling]; the next step is [CTA]>"   # the single explicit 'on-brand' referent; read by §9.1/§9.2/§15.1; editing it stales the golden set (§15.3)
desired_feeling: "<the one feeling a stranger should have in 1s>"   # seeds voice_descriptors + the §9.2 'feel in one second'
primary_cta: "<the one action; used EXACTLY, never invented (contact rule)>"
cta_destination: "dm"            # dm | whatsapp | link | visit | call
off_brand_notes: ["<taste-level 'not us' — DISTINCT from the fail-closed safety fields; never gates publish>"]

# --- Brand voice (seeds brand_voice canon) ---
voice_descriptors: ["warm", "practical", "never preachy"]
voice_do: ["lead with value", "name the life specifically"]
voice_dont: ["fear hooks", "listicle slop", "fake urgency", "medical claims"]
reading_level: "<e.g. plain, conversational>"
sample_lines_good: ["<1-3 exemplar on-brand lines>"]
sample_lines_bad: ["<1-3 off-brand lines to avoid>"]

# --- Visual identity (seeds brand_assets + visual canon + Caption-Composer) ---
logo_asset: "assets/logo.png"
wordmark_text: "<text under logo>"
palette_hex: ["#F07020", "#F2C12E"]      # the accent-rule gradient
accent_dark_bg: "#F2C12E"                  # scrim/type accent on DARK photos
accent_light_bg: "#B8800E"                 # scrim/type accent on LIGHT photos
headline_font: "<serif>"
label_font: "<small-caps>"
visual_register: "<premium, warm, real-life; NOT stock/spa>"
visual_variety: "balanced"                 # balanced | high (narrows the §9.2 treatment menu for tight-aesthetic brands)
visual_strategy: "concept_led"             # concept_led (default, generative) | product_led (real product hero)
people_pool: "assets/people/"              # real-person/leader pool (was preapproved_photo_pool)
product_pool: "assets/products/"           # per-SKU / reference product images (used when visual_strategy = product_led)
image_provider: "gemini_image_pro"         # stable token (Gemini-native default → Nano Banana Pro / Gemini 3 Pro Image) | imagen | replicate_<model> — confirm name+ID at build time (§14.3)
image_quality_tier: "medium"               # FLOOR/default; CD "premium" tag may upgrade a piece, never downgrade (§9.2)

# --- Contact / CTA (used EXACTLY; never invented) ---
cta_style: "soft"
contact_whatsapp: ["<number>"]
contact_instagram: "<@handle>"
cta_forbidden_phrases: ["register now", "book now", "sign up", "limited spots"]

# --- Channels & cadence (seeds cadence_plan) ---
channels: ["instagram", "facebook"]
posts_per_week_target: 5
standing_week:                              # keys mon..sun (or the 'weekend' aggregate for sat+sun); value = the §7.1.1 slot grammar { track, language?, flag?, format?, channel?, notes? }
  mon: { track: "evergreen" }
  tue: { track: "offering:<id-A>" }
  wed: { track: "evergreen", flag: "research_grounded" }   # present only if research_post_min_per_week > 0
  thu: { track: "offering:<id-B>" }
  fri: { track: "evergreen" }
  weekend: { track: "optional" }
research_post_min_per_week: 1              # 0 disables the standing research slot + its enforcement (§9.1/§9.4/§8.2)
max_posts_per_week: 6
campaign_max_posts_per_week: 8            # brand-level default campaign ceiling; a per-campaign override lives on CampaignPlan.max_posts_per_week_override (§17/§9.5)
seasonal_calendar: []                      # optional [{name, dates}] for standalone seasonal campaigns
max_queue_depth: null                      # backpressure cap (§9.5); null → default 2 × posts_per_week_target
owner_absence_pause_days: 7                # §9.5 — pause standing-week materialisation after N days with no Owner Action + a deep queue
campaign_overrides_backpressure: false     # if true, a dated campaign slot + the research minimum still materialise through a backpressure pause


# --- Intent & capacity (feed the §7.1.1 cadence proposal) ---
posting_goal: "awareness"        # awareness | community | conversion | launch — biases the cadence proposal
weekly_capacity: "sustainable"   # owner's sustainable volume; the proposal stays at/below this
cadence_source: "proposed_archetype"   # owner_stated | proposed_archetype | edited — provenance of standing_week
# --- Cadence shape (extends standing_week / posts_per_week_target / max_posts_per_week) ---
# standing_week slot grammar: { track, language?, flag?, format?, channel?, notes? };
#   track ∈ evergreen | offering:<id> | optional | quiet  (quiet = first-class no-post day; the research slot stays flag: research_grounded on an evergreen track);
#   a slot whose format lacks an auto-publish adapter is materialized manual_publish_only (§12.3)
quiet_days: []                   # recurring no-post weekday tokens; first-class, distinct from weekend:optional
blackout_dates: []               # [{name, dates}] brand-closed windows (holidays, closures); win at materialization (§9.5)
evergreen_rotation: "no_repeat_within: 3"   # cadence INTENT for pillar variety; the §9.4 ledger-linter ENFORCES

# --- Compliance & safety (seed safety hard-rules + Policy Server). These three fields FAIL CLOSED. ---
# claims_forbidden / non_disclosure_rules / required_framing MUST be explicitly owner-confirmed
# to pass schema validation. Empty/unconfirmed = "unknown" = block publish, route to human (§14.2, §15.1).
claims_allowed: ["<e.g. 'reduces stress, with citation'>"]
claims_forbidden: ["<MUST be elicited explicitly>"]
comparative_claims_allowed: false          # compiles to a 'no comparative claims' hard-rule (§14.2)
political_content_allowed: false           # compiles to a 'no political content' hard-rule (§14.2)
non_disclosure_rules:                       # bind words AND image; MUST be elicited explicitly
  - "<e.g. the proprietary technique's exact mechanism>"
required_framing:                           # mandatory hedges; MUST be elicited explicitly
  - { topic: "<e.g. clinical-population claims>", framing: "<e.g. 'in clinical studies' + no treatment-replacement implication>" }
regulatory_notes: "<e.g. wellness; no medical advice>"

# --- Research policy (seeds research_bank) ---
source_allowlist: ["<domain-appropriate authoritative/primary sources>"]   # e.g. PubMed/journals for health/regulated brands
source_denylist: ["blogs", "forums", "reddit", "unverified social"]
citation_required_for_claims: true
require_second_source_for_quantitative: false   # high-stakes brands set true (§8.2 verification)
claim_reverify_months: 6

# --- Offerings (replaces hard-coded program briefs; see 7.4) ---
offerings:
  - { id: "<id-A>", name: "<offering name>", one_liner: "<accurate, never-trivialized>", is_flagship: true }
  - { id: "<id-B>", name: "<offering name>", one_liner: "<...>", funnels_from: "<id-A>" }   # optional inter-offering funnel

# --- Topical territory for the evergreen agent (replaces wellness.md pillars) ---
evergreen_pillars: ["<pillar 1>", "<pillar 2>"]
local_detail_bank: ["<concrete local anchors writers may use>"]

# --- Notifications & alerts (seeds the §14.4.1 model). All optional; safe defaults below. ---
notifications:
  channel: "none"                  # none | email | chat  (none = Sheets ALERTS row + floor only; §6.3 minimal mode)
  recipients: ["<owner email/space>"]   # all notified; FIRST acknowledgement resolves for everyone
  severity_floor: "action"         # critical | action | digest — lowest tier pushed out-of-band (the scheduled digest below always sends on its own schedule regardless)
  quiet_hours: { tz: "<defaults to brand timezone>", start: "21:00", end: "08:00" }   # CRITICAL always breaks through
  digest: { day: "fri", hour: "16:00" }   # the §8.2 digest schedule (was hardcoded 'Friday')
  batch_max_wait_minutes: 120
  batch_max_items: 6
  reminder_after_hours: 24         # an unacked ACTION re-notifies once, then folds into the digest
  critical_reminder_minutes: 60
  max_sends_per_hour: 12           # rate cap (Denial-of-Wallet); excess non-CRITICAL coalesces
# --- Publishing & approval ---
approval_mode: "human"                       # human | auto | auto_after_trust
auto_publish_enabled: false                  # MASTER kill-switch (§12.3 precedence)
approver_allowlist: []                        # google accounts/emails allowed to approve for this brand (§12.5); [] ⇒ owner-only. A non-allowlisted operator is refused fail-closed
delegation: null                              # optional {delegate_operator_id, scope ∈ {approve|request_changes_only|publish}, expires_at} — §12.5 delegated approval authority
system_of_record: "google_sheets"            # google_sheets | builtin_db
trust_threshold:                             # gates auto_after_trust -> auto recommendation (§12.3, §14.4)
  window_pieces: 20
  min_approval_rate: 0.95
  max_avg_human_edits: 0
  zero_policy_violations: true
```

Secrets (API tokens for image provider, Google, Instagram) live in a **secrets vault**, referenced by name, resolved **only into the tool/MCP auth layer** (§7 intro, §14.6) — never inlined.

#### 7.2.1 Resolver contract (buildability)

- **Timing.** Substitution happens at **prompt assembly (runtime)**, not baked into stored docs. Engine docs remain templates resolved per-use. ("Compile at brand instantiation" in §7.3 means field→canon/agent **wiring**, not freezing text.)
- **Serialization.** Scalars inline; lists comma-joined inline *or* bulleted (state which per use site); objects/maps via a defined per-key format; **no raw YAML dumped into prompts**.
- **Precedence.** Brand Kit value → environment default → error. (This defines the "environment fallback.")
- **Missing variable.** **Fail-closed** on any unresolved *required* variable: block the run and surface to the owner. Optional variables may resolve empty.
- **Recursion.** Resolved values are treated as literals (no re-resolution).

- **Version pinning (edit-safety, Day 5 context hygiene).** A piece resolves `[[VARIABLE]]`s against the **`brand_kit_version` captured when it entered the pipeline at PLAN** (recorded on `Draft`/`QueueItem`/`Run`/`LedgerRow`, §17), not against whatever the kit is at each later stage — preventing a mid-pipeline edit (§7.7) from producing a self-inconsistent artifact (caption resolved under the old voice, image under the new palette). **The three fail-closed safety fields are the deliberate exception** — `claims_forbidden`/`non_disclosure_rules`/`required_framing` (and the Policy Server, §14.2) always resolve to the **latest** value, so a tightening can never be out-run by a piece already in flight.
- **Runtime resolution failure is fail-closed mid-pipeline too.** An unresolvable *required* variable **does not silently substitute empty string** — the piece is set `exception` and routed to the owner (treated like an unconfirmed safety field, §14.2). Unknown/absent `brand_kit_version` on replay also fails closed.

```gherkin
Scenario: Unresolved required variable blocks the run
  Given a canon template references a required [[VARIABLE]] absent from the Brand Kit and environment
  When an agent assembles its prompt
  Then the run is blocked and the gap is surfaced to the owner
  And nothing is drafted or published
```

### 7.3 How the Brand Kit seeds the studio

At brand instantiation, Agent Atelier **wires** the Brand Kit into the harness (resolution still happens per-use, §7.2.1):

| Brand Kit field(s) | Seeds / resolves into |
|---|---|
| identity, contact, logo, palette, fonts | `brand_assets` canon + Caption-Composer config |
| voice_*, sample_lines_*, reading_level | `brand_voice` canon + channel style guides |
| audience_*, scroll_test_persona | the specificity rule + the "two-second scroll test" persona in the Creative & Visual engines |
| brand_type | which hook/shape **pack(s)** the Creative Engine activates (§9.1) |
| channels, standing_week, cadence, languages | `cadence_plan` canon (incl. the §7.6 language rule) |
| claims_allowed/forbidden, comparative_claims_allowed, political_content_allowed, non_disclosure_rules, required_framing | safety hard-rules + the Policy Server's structural & semantic gates (§14.2) — the three fail-closed fields gate publish |
| source_allowlist/denylist, citation rules, require_second_source_for_quantitative | `research_bank` policy + verification (§8.2) |
| offerings[] | one **Offering Brief** per offering (dynamic context for the single Offering Content Agent role, §7.4) |
| evergreen_pillars, local_detail_bank | the Evergreen Content Agent's territory + the anti-drab anchor bank |

The **generic engine documents themselves never change between brands** — only their resolved `[[VARIABLE]]` values, the active hook/shape pack, and the attached Offering Briefs do. That is the property that makes onboarding a config action (G1).

### 7.4 The Offerings model (replaces hard-coded program briefs)

In the AOL system, each "program" had a hand-written knowledge brief and a dedicated agent. Agent Atelier generalizes this:

- Each **Offering** yields an **Offering Brief** (a structured knowledge doc: what it is, who it's for — *including cross-offering audience and maturation/timing guardrails*, accurate description, proof/outcomes with required hedges, format/logistics, what-not-to-claim, **tone notes** that capture per-offering register modulation vs the brand default, and a positive **spotlight_angles / seed-angle list**). Drafted by the Strategist during intake from owner input + ingested sources, then owner-confirmed.
- There is **one code-defined Offering Content Agent role**; the relevant Offering Brief is **dynamic context selected per task** (keyed by `offering_id` on the task — §17). Adding an offering registers a new Brief and a cadence slot — **no agent-tree change, no redeploy** (G1). Per-offering budget (§13.2), memory (§8.1), and pause/status are re-keyed by `offering_id` so per-offering granularity is preserved.
- Offerings with dates (or a standalone seasonal/promo campaign) trigger **campaign mode**; offerings without dates still get **weekly spotlight education**.
- Inter-offering funnels are expressed by the optional `funnels_from` field; timing/tone guardrails for cross-promo live in the Offering Brief prose (kept soft/organic, not numeric global fields).

```gherkin
Scenario: Add a new offering to an existing brand
  Given a running brand studio
  When the owner adds an offering via the Strategist
  Then an Offering Brief (incl. tone notes and seed angles) is drafted from owner input and confirmed
  And the cadence plan gains a weekly spotlight slot for that offering
  And no agent tree change or redeploy occurs; the new Brief is registered as selectable dynamic context
```

**Editing, renaming, and retiring offerings.** Adding is only half the lifecycle; real brands rename and sunset offerings constantly, and that must stay a pure config action (G1, Day 1 factory model under mutation):
- **`offering_id` is immutable.** Renaming edits `name`/`one_liner`/`brief_ref`/`is_flagship`/`funnels_from`/`dates` only; the id — which keys per-offering budget (§13.2), memory (§8.1), every cadence slot, and every `LedgerRow` — **never changes**, so history stays intact. A retired id is never reused.
- **Retiring** sets `Offering.status = retired` (§17): its standing-week slot is **reallocated by the Managing Editor** (not left dark), its in-flight pieces continue to the HUMAN GATE (or are reject-and-recorded if the owner chooses), its Offering Brief is **frozen** (kept for audit, no longer selectable as dynamic context), and its per-offering budget stops accruing.
- **Dangling `funnels_from`.** Retiring offering X while offering Y has `funnels_from: X` is surfaced at save time; the owner must re-point or clear Y before the save completes — a **validation error, not a silent no-op**.
- **Editing the Offering Brief** (spotlight_angles, tone notes, what-not-to-claim) is a versioned edit (§17 `brief_ref`): `material`-class by default, but **what-not-to-claim changes are `safety`-class** (§14.4) and re-confirm exactly like the kit's fail-closed fields.

```gherkin
Scenario: Retire an offering without orphaning the feed or rotting funnels
  Given an offering with a weekly spotlight slot, a piece in CD Review, and another offering whose funnels_from points at it
  When the owner retires it via the Strategist
  Then Offering.status becomes retired, its offering_id is unchanged, and its Brief is frozen (no longer selectable)
  And the Managing Editor reallocates its standing-week slot rather than leaving it dark
  And the in-flight piece proceeds to the HUMAN GATE
  And the dangling funnels_from is a validation error the owner must re-point before the save completes
```

### 7.5 Independent claim verification (research)

See §8.2 (Research & Verification Agent) and §9.3 — verification is split from authorship and grounded, per blocker F33/F34.

### 7.6 Per-piece language rule

- The piece's language is chosen at **IDEATE+DRAFT** (before the caption, §10.1), recorded on the Draft, on `QueueItem.language` (§17), and in the Sheets `Language` column.
- **Default = primary = first entry of `languages[]`.** Single-language brands need nothing further.
- An optional per-slot `language` key in `standing_week` pins a slot's language (e.g. `tue: { track: "offering:<id>", language: "Punjabi" }`).
- For multi-language brands without a per-slot pin, the **Managing Editor treats language as an additional variety axis** and distributes it across the week, logging the choice. (Language is **not** a fixed per-channel default — that would fight variety-by-message.)


### 7.7 The Brand Kit lifecycle — editing, versioning, race-safe re-resolution (the Brand Desk)

Onboarding (§7.1) is the *first* capture; almost all real brand-intent work happens *after* it — a tagline changes, a prohibition is discovered, cadence shifts, a font is swapped, a person withdraws consent. The Brand Kit is a **living, versioned document**, edited only through one governed path (the **Edit Loop**) and surfaced on the **Brand Desk** — the front-office companion to the §12.4 Studio Floor. Editing brand intent must be **as fail-closed and auditable as creating it**, and a kit edit must never silently change a piece mid-flight **nor** let a piece publish under stale-looser safety.

**Revisions (versioning + audit).** Every committed change bumps the monotonic **`brand_kit_version`** — the instance counter pieces pin (§7.2.1), system-managed and append-only, held by §17 `BrandKit.version` — and yields an immutable **`BrandKitRevision`** (defined here in §7.7) recording `parent`, `diff`, `change_summary`, `editor_human`, `edit_class`, `changed_fields[]`, `prior_values{}`, `safety_fields_touched[]`, a `safety_attestation{by_human, at, fields[]}`, and `vibe_diff_ref?`. HEAD is the active kit; superseded revisions are retained for audit and rollback (append-only, §12.2/§14.5).

**One save path, three surfaces (read/draft/act, Day 3).** Edits originate from (a) a Strategist re-interview (the Strategist *drafts* the delta, the owner *acts*), (b) the editable structured view (Sheet/Form), or (c) the Brand Desk / Planner (§12.4). All three resolve to one transaction and **never mutate HEAD directly**:
1. **Stage** into a draft revision parented to HEAD; edits batch.
2. **Validate** — the whole kit must re-pass `brand_kit.schema.json` *in full* (enums, required-present, the three fail-closed fields still owner-confirmed) plus the §9.5 cadence validator and the Readiness Report. A save leaving a safety field empty/unconfirmed is **rejected at save time**.
3. **Classify risk** — `trivial` (apply + audit) · `material` (Impact Preview + confirm + offer re-light) · `safety` (Vibe Diff that **names any loosening** + in-flight re-check + mandatory re-light) · `autonomy` (`approval_mode`/`auto_publish_enabled`/`trust_threshold` — owner-only, **never settable from the structured view**). The class→gate table is §14.4.
4. **Impact Preview / Vibe Diff** (Day 5) — plain-language before→after per field; which canon docs/agents re-resolve (§7.3); which in-flight pieces + cadence slots are affected; and a **dry-run re-resolution** (§7.2.1) of 1–2 sample prompts so the owner sees the downstream wording change *before* committing.
5. **Fail-closed safety re-confirmation** — touching any of `claims_forbidden`/`non_disclosure_rules`/`required_framing` flips that field to **unconfirmed**; the owner re-attests with worked examples (§7.1/§15.1). A revision with an unconfirmed safety field may be staged but **cannot become the publish HEAD** (§14.2). **Even *removing* a prohibition requires attestation** — safety is never quietly loosened — and a *narrowing* edit (a new prohibition) additionally fires a targeted first-light near-violation to prove the new rule blocks. Emptying a safety field via the structured view **fails schema validation**.
6. **Commit** — idempotent (draft-revision id + content hash, mirroring the §12.2 publish-once guard) and under **optimistic concurrency**: a commit whose parent is no longer HEAD is rejected, forcing re-review so two operators cannot silently clobber each other. HEAD advances; `brand_kit_version` bumps; the prior revision → superseded; an `AuditEntry` (`actor = human`) is written.
7. **Rollback** — restores any prior revision as a **new forward** revision (revisions are immutable); if the rollback touches a safety field, attestation re-fires (rolling back can re-weaken safety).

**Re-resolution timing (the race-safe invariant — the single most important robustness rule in the edit story).** Resolution happens at prompt assembly (§7.2.1), so edits are not retroactive — with one deliberate exception:
- **New pieces** resolve against HEAD immediately.
- **In-flight pieces pin the `brand_kit_version` they started under** (recorded at PLAN/IDEATE) and resolve **non-safety** `[[VARIABLE]]`s against that pinned version for their whole pipeline — so voice/visual stay coherent DRAFT→caption and no piece becomes a Frankenstein artifact.
- **The three safety fields and the Policy Server always evaluate HEAD** from LEDGER LINT through the publish boundary — a tightened prohibition **retroactively protects pieces already in motion**. A tightening immediately re-checks every not-yet-published piece (Draft / CD Review / Approval Queue / Approved) against the latest rules; newly-violating pieces drop out of auto-publish eligibility and route to the human; already-**published** pieces surface in the next visibility digest (§14.5) for owner review.
- **Cadence edits** take effect at the next Monday tick (§9.5/§13.1), never mid-pipeline.

**Asset edits are config edits too.** Replacing the bytes at an asset path (a new `logo.png`, a swapped font) is invisible to field-level diffing but changes every future render; it is a `material`-class edit and runs the same Edit Loop with a re-light. **Removing a person from the `people/` pool** (a consent withdrawal, §14.3 no-deepfake) invalidates any not-yet-published piece that uses that person — those pieces route to the human, never publish silently.

**Partial update / re-onboard / re-ingest.** Partial update = a scoped Strategist session over one section. Re-onboard = the full interview pre-filled from HEAD (rebrand) → one consolidated revision + Vibe Diff. Re-ingest = point at a refreshed URL/`@handle` to re-draft **non-safety** fields; re-drafted fields land **proposed** again (`field_provenance.confirmed → false`) until the owner re-confirms the diff — a stale website can never silently overwrite a confirmed value, and safety is never auto-touched (§7.1 firewall).

```gherkin
Scenario: A low-stakes edit commits without a Vibe Diff but is versioned and audited
  Given an active brand at brand_kit_version N
  When the owner changes the tagline
  Then the edit is staged into a draft revision parented to N and passes full schema validation
  And on commit brand_kit_version becomes N+1 and a BrandKitRevision + AuditEntry record actor and diff
  And no safety field was touched so no re-attestation is required

Scenario: Editing a safety field re-confirms fail-closed and protects in-flight work
  Given a live brand with confirmed safety fields and a piece in REVIEW pinned to brand_kit_version N
  When the owner adds or removes a claims_forbidden entry
  Then that field flips to unconfirmed and the staged revision cannot become the publish HEAD
  And the Strategist re-elicits the field explicitly with worked examples
  And on re-attest brand_kit_version becomes N+1 and a BrandKitRevision is appended
  And the in-flight piece resolves non-safety variables against N but the new rule (HEAD) is enforced at its publish boundary
  And adding a new prohibition fires a targeted first-light near-violation that must block

Scenario: A stale concurrent edit is rejected, not silently clobbered
  Given owner-1 and owner-2 both stage edits from brand_kit_version N
  When owner-1 commits first and HEAD becomes N+1
  And owner-2 attempts to commit a revision still parented to N
  Then owner-2's commit is rejected as out-of-date and owner-2 is shown the N+1 diff to re-base onto
  And nothing is silently overwritten
```

### 7.8 Onboarding at scale (archetypes, Cadence Templates, clone-a-brand, switching, isolation)

G1 promises "onboarding is a config action"; this makes onboarding **many** brands a config action too — fast, without weakening safety or leaking across brands.

**The archetype library (data, not code — G1, Day 1 factory model).** An archetype is a `BrandTemplate` **file** (defined inline below); adding a vertical is a new file, **no agent-tree change, no redeploy**. Each ships a coherent bundle: a **§9.1 `pack` pointer** (`educational_editorial | product_commerce`), **voice defaults**, a **visual register + `visual_strategy`**, a **Cadence Template** (the shape §7.1.1 Door B proposes), **topical-territory seeds**, a **source policy**, a **`cta_style`**, and **category safety starting-points flagged proposed-unconfirmed** (never pre-satisfied). A new brand arrives **60–70% filled**; the interview collapses to the intent spine + offerings + the explicit safety pass.

| Archetype (`brand_type`) | `pack` | Voice default | Visual register | Cadence shape | Safety starting-points (proposed-unconfirmed) |
|---|---|---|---|---|---|
| `nonprofit_ngo` | educational_editorial | earnest, hopeful; never guilt-trip | dignified beneficiaries (no poverty-porn) | evergreen-heavy + 1 impact-story/wk + appeal campaigns | consent for faces (esp. minors); no political endorsement; donation claims need proof |
| `saas_b2b` | product_commerce | clear, credible, jargon-light | clean product-UI, explainer | thought-leadership + product-spotlight + launch | no unsubstantiated ROI; comparative default false; no customer logos w/o permission |
| `hospitality_local` | product_commerce | warm, sensory, neighbourly | real food/place, appetite-forward | menu-spotlight + weekend optional + seasonal | no allergen/health claims w/o basis; customer faces need consent; no exact recipe |
| `clinic_health` | educational_editorial | reassuring, precise, non-alarmist | clean, human; no fear imagery | education + 1 research-grounded/wk + service-spotlight | NO outcome guarantees; 'not medical advice' framing; patient privacy; no before/after w/o consent |
| `coaching_creator` | educational_editorial | personal, direct; not preachy | founder-forward, authentic | thought-leadership + offer-launch | income claims need 'results not typical'; no guarantees; client stories need consent |
| `ecommerce_dtc` | product_commerce | punchy, benefit-led | product-hero, UGC, before→after | offering-spotlight + UGC + drop/sale (add mode) | no unsubstantiated efficacy; comparative default false; UGC needs rights; price stated exactly |
| `school_education` | educational_editorial | warm, parent-reassuring | real campus (consent), bright | education + admissions spikes + events | student/minor faces need explicit consent (strict); no ranking/outcome guarantees; family privacy |

*(The existing `educational`/`product_commerce` types map onto this catalog; `custom` starts blank. Archetype breadth ≠ pack count — every `brand_type` resolves to one of the two §9.1 packs.)*

**The scaling principle: speed on the non-safety 80%, rigor on the safety 20%.** Archetype defaults collapse voice/visual/cadence/territory/source-policy to **review-and-accept**, but the three fail-closed fields **always** run the full worked-example elicitation (§7.1) — an archetype's safety proposals accelerate the conversation and can never close the gate.

**Cadence Templates.** Each archetype ships an opinionated rhythm (educational = evergreen-heavy with one research slot; product_commerce = spotlight-heavy with a weekend optional slot) — the proposals Door B draws from (§7.1.1).

**Clone-a-brand.** "Create like `<existing brand>`" copies a brand's HEAD kit into a fresh draft revision under a **new `brand_id`** (`parent_brand_id` recorded), copying structure + voice/visual scaffolding but **forcing**: (a) re-entry of identity + contact + `secrets_ref` — **secret *values* are never copied**, only the schema of which keys are needed (§14.6); and (b) re-attestation of **all three safety fields**, which land **proposed-unconfirmed (fail-closed)**. The cloned cadence copies but is **re-presented in the Cadence Studio for approval**. You can never inherit another brand's safety confirmation or credentials. Use case: an agency clones one "golden" brand to stand up 20 chapters/franchises, editing only identity + offerings and re-attesting safety per brand.

**The per-brand isolation invariant (Day 4 — least-privilege, blast-radius).** Every Brand has an `isolation_key`; all canon resolution, the Content Ledger (§9.4), the Claim Bank (§9.3), the queue, Memory (§8.1), budgets (§13.2), secrets, and Drive folders are partitioned by `brand_id`. **No agent run may read or write across brands.** The `[[VARIABLE]]` resolver is **brand-scoped** — it only ever resolves the active run's `brand_id`, so cross-brand resolution is impossible *by construction* (extends §7.2.1). The §13.2 scheduler tick iterates brands, each tick scoped to one `brand_id`; per-`offering_id` keying nests under `brand_id`.

**Brand switcher.** A header brand-selector on the Brand Desk / Studio Floor (§12.4) changes only the **view** and active brand context; because every run is brand-scoped, switching can never cause a cross-brand write — the switcher is a lens, not a mutation. Draft brands appear with a "Resume" affordance; archived brands are hidden by default.

**Tenant defaults (light).** An operator managing many brands can set tenant-level defaults (timezone, default `approval_mode: human`, default `auto_publish_enabled: false`, source allow/deny lists) inherited by new brands and overridable per brand.

```gherkin
Scenario: Clone a brand re-confirms safety, re-enters secrets, and re-approves cadence
  Given an existing active brand "Chapter A" with confirmed safety fields, a secrets_ref, and a Cadence Plan
  When the owner chooses "Create like Chapter A" for "Chapter B"
  Then Chapter B copies voice and visual scaffolding and records parent_brand_id
  And identity, contact, and secrets_ref must be re-entered and no secret values are copied
  And all three safety fields land proposed-unconfirmed and block validation until re-elicited and re-signed
  And the cloned standing_week is presented in the Cadence Studio as a proposal for approval
  And no agent code or engine document is modified

Scenario: Brand isolation prevents cross-brand resolution by construction
  Given two active brands A and B running on the same unchanged agent code
  When an agent run is dispatched for brand A
  Then the [[VARIABLE]] resolver resolves only brand A's Brand Kit, ledger, Claim Bank, and secrets
  And no value from brand B is reachable in that run
  And the scheduler tick that dispatched it was scoped to brand A's brand_id
```

---

