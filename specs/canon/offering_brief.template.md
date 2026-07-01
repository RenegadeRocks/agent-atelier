# Offering Brief — [[OFFERING_NAME]] ([[BRAND_NAME]]) — generic canon template

> **Status:** product-agnostic template. One filled copy exists **per offering** in `offerings/<offering_id>.md`; this file is the blank the Strategist fills and the shape the engine validates against. Brand-level values arrive at resolve time from the Brand Kit via `[[VARIABLE]]` substitution (PRD §7.2.1); offering-level values are filled by the Strategist during intake and **owner-confirmed** before first use.
>
> **Owner agent (authors/maintains):** Brand Onboarding Strategist. **Loader (consumes per task):** the single **Offering Content Agent** role — this Brief is **dynamic context selected by `offering_id`** on the task (PRD §7.4, §17), not a per-offering agent. **Approver:** the brand owner (human). **Escalation owner for sensitive/regulated claims:** the brand owner, routed via the Managing Editor.
>
> **Model note (confirm names/IDs at build time):** content reasoning runs on the configured reasoning tier; image production uses the Gemini-native image model token `gemini_image_pro` (Nano Banana Pro), operational steps on alias `gemini-flash-latest`. These are referenced by the Visual Production Agent, not invoked here — confirm exact model names/IDs at build time.

> **Why this document exists.** In the legacy system each program had a hand-written knowledge brief **and** a dedicated agent. Agent Atelier keeps the knowledge, drops the dedicated agent: there is **one** Offering Content Agent role, and *this Brief is what makes it the expert for [[OFFERING_NAME]] for the duration of one task.* Adding an offering means registering a new filled copy of this template plus a cadence slot — **no agent-tree change, no redeploy** (PRD G1). The Brief must therefore be self-contained: everything the agent needs to represent [[OFFERING_NAME]] **accurately — never trivialized** — lives here or in the canon it points to.

---

## 0. Front-matter (machine-keyed; the resolver and ledger read this)

```yaml
offering_id: "[[OFFERING_ID]]"        # stable key; tasks, budget (§13.2), memory (§8.1), pause/status are all re-keyed by this
offering_name: "[[OFFERING_NAME]]"
one_liner: "[[OFFERING_BRIEF]]"       # accurate, never-trivialized; mirrors the Brand Kit offerings[] one_liner
is_flagship: false                    # true for the brand's headline offering
has_dates: false                      # true => campaign mode eligible (§4.1 phase 1); false => standing weekly spotlight only (phase 0)
funnels_from: ""                      # optional offering_id this one matures FROM (cross-offering funnel; see §3.3 and §8)
brand_default_register: "[[VOICE_DESCRIPTORS]]"   # the brand baseline this Brief modulates AGAINST (see §6)
confirmed_by_owner: false             # MUST be true before the Offering Content Agent may ship for this offering
last_confirmed: ""                    # ISO date of the most recent owner confirmation
```

> **Fail-closed.** If `confirmed_by_owner` is not `true`, or any **required** `[[VARIABLE]]` is unresolved, the run blocks and surfaces to the owner (PRD §7.2.1) — nothing is drafted or published for this offering.

---

## 1. What it is

A truthful, concrete description of [[OFFERING_NAME]] in the brand's own terms — what the person actually does, receives, or experiences. Written so a stranger understands it without marketing gloss.

- **Plain definition:** `<one or two sentences; what [[OFFERING_NAME]] actually is>`
- **Category / form:** `<e.g. multi-session course · single workshop · membership · physical product · service>` (this is [[BRAND_TYPE]]-shaped; for a `product_commerce` brand the hero is a real `products/` asset, §10)
- **The heart of it:** `<the one element that, if removed, would make it a different offering — name it plainly>`
- **What it is NOT:** `<the nearest thing people mistake it for, corrected>` — guards against the trivialization failure mode (e.g. "experiential, not 'just journaling'").

> **Accuracy contract.** Every line here must survive the owner reading it aloud. No inflation, no shrinkage. If the true description is unglamorous, the angle work (§7) carries the interest — **never** a softened or exaggerated definition.

---

## 2. Who it's for

### 2.1 Primary audience
Grounded in the brand's [[AUDIENCE_PERSONA]] and the pains in [[AUDIENCE_PAINS]], narrowed to who [[OFFERING_NAME]] specifically serves.

- **This offering's person:** `<the slice of [[AUDIENCE_PERSONA]] this is for>`
- **The pains it actually addresses:** `<subset of [[AUDIENCE_PAINS]] — only what's honestly relevant>`
- **Readiness / fit signals:** `<who is ready for this vs who isn't yet>`

### 2.2 Cross-offering audience (who arrives from elsewhere in the brand)
If `funnels_from` is set, most of this offering's audience are people who matured **from** that prior offering. Describe them as they actually are at the moment they encounter [[OFFERING_NAME]].

- **They come from:** `<funnels_from offering name, or "cold / evergreen discovery" if none>`
- **What they already know / have done:** `<the prior experience to assume, or none>`
- **What's different about addressing a graduate vs a stranger:** `<tone + assumed knowledge shift>`

### 2.3 Maturation & timing guardrails (soft, organic — never numeric global rules)
How and *when* it is appropriate to surface [[OFFERING_NAME]] to a given person. These are **prose guardrails**, kept soft by design (PRD §7.4) — the studio does **not** encode cross-promo timing as global numeric fields.

- **Too early looks like:** `<the premature-pitch failure to avoid — e.g. selling the advanced thing to someone who just arrived>`
- **Ready looks like:** `<the organic moment this becomes welcome rather than pushy>`
- **Cadence feel:** `<how often this offering may lean into promotion vs simply educate — qualitative>`
- **Cross-promo restraint:** introduce only when it reads as the natural next step; **never aggressive**, never guilt-based (retention nudges in §4.1 phase 3 follow the same rule).

---

## 3. Accurate description (the deeper knowledge the agent reasons from)

Expand §1 into the working knowledge the Offering Content Agent draws on — enough that it can write twenty distinct pieces without ever inventing a detail or trivializing the offering.

### 3.1 How it actually works / what happens
`<the honest mechanics, sequence, or experience — to the level disclosure rules permit (see §5 / [[NON_DISCLOSURE_RULES]])>`

### 3.2 What makes it distinct
`<the true differentiators, stated without comparative claims unless [[COMPARATIVE_CLAIMS_ALLOWED]] is set>`

### 3.3 Where it sits in the brand's ladder
`<relationship to other [[OFFERINGS]]; if funnels_from is set, what it deepens or follows>`

> **Never trivialized.** This is the section most prone to "make it sound easy/quick/magic." Resist. Describe the real thing; let the §7 angles make it compelling.

---

## 4. Proof / outcomes (with [[REQUIRED_FRAMING]] hedges)

What [[OFFERING_NAME]] can honestly be said to do — and the exact hedging that must travel with each claim.

- **Outcomes we may speak to:** drawn only from [[CLAIMS_ALLOWED]]; stay strictly inside it.
- **Mandatory framing:** any outcome whose topic appears in [[REQUIRED_FRAMING]] **must** carry the mandated framing in spirit and verbatim where specified (e.g. clinical-population findings stated as "in clinical studies" and **never** implying [[OFFERING_NAME]] replaces professional treatment or care).
- **Quantitative / research-grounded claims:** do **not** originate here. Any statistic, percentage, study year, or research verb must come from a **VERIFIED `locked_sentence`** in the Claim Bank (PRD §8.2) and is enforced deterministically at the publish boundary (§14.2 claim-grounding gate). If `[[REQUIRE_SECOND_SOURCE_FOR_QUANTITATIVE]]` is set, those claims additionally need a second corroborating source before use.
- **Sources are bound** by [[SOURCE_ALLOWLIST]] / [[SOURCE_DENYLIST]]; sensitive/clinical claims are flagged to the owner before first use.
- **Testimonials / lived experience:** vetted by the Research & Verification Agent; experiential or traditional claims are cited to their proper source (teaching, founder, maker) and **never dressed as research**.

> Re-verify cadence for any claim used here follows `[[CLAIM_REVERIFY_MONTHS]]`.

### 4.1 Content phases (emphasis modes through the one feed pipeline — not separate channels)
The Offering Content Agent serves all of these through the same pipeline; which mode is active is a content emphasis, not a channel.

- **(0) Standing weekly spotlight** — always on, even with no dates. Educational, offering-anchored. Required whenever this Brief is attached to a cadence slot.
- **(1) Campaign ladder** — only when `has_dates` is true. Truthful scarcity only (real dates, real seats); never manufactured urgency.
- **(2) In-program emphasis** — intimate, supportive, **zero promotion**, for people currently inside [[OFFERING_NAME]].
- **(3) Retention emphasis** — gentle nudges to keep practising / using / returning. **Never guilt.**

---

## 5. Format & logistics

The practical facts a piece may need to state correctly. Fill only what is true and currently confirmed; leave unknowns blank rather than guessing (fail-closed beats a wrong logistic).

- **Duration / commitment:** `<e.g. sessions × length, or product lead time>`
- **Modality:** `<in-person / online / hybrid / physical good>`
- **Cost / access:** `<state only if owner-confirmed and current>`
- **How to start / where it happens:** `<the real next step; align CTA with §9>`
- **Dates (if `has_dates`):** `<source of truth for campaign-mode dates; must be live-accurate>`
- **Channels this offering publishes through:** subset of [[CHANNELS]] as scheduled in [[STANDING_WEEK]]; respects [[POSTS_PER_WEEK_TARGET]] / [[MAX_POSTS_PER_WEEK]].
- **Language:** chosen per piece at IDEATE+DRAFT (PRD §7.6); default = primary of [[LANGUAGES]] unless a slot pins one.

---

## 6. What not to claim

Hard boundaries. A draft that crosses any of these is **rejected, not softened** (Creative Director Gate 1, PRD §15).

- **Forbidden claims:** never enter [[CLAIMS_FORBIDDEN]]. A line drifting toward a forbidden claim is rejected.
- **Non-disclosure rules:** [[NON_DISCLOSURE_RULES]] bind **both words and image** — never reveal a withheld mechanism, technique, or proprietary detail in caption, carousel, or visual. (E.g. an offering whose method is intentionally unrevealed is described by its *experience*, never its mechanics.)
- **Comparative claims:** permitted only if [[COMPARATIVE_CLAIMS_ALLOWED]] is true; otherwise never compare [[OFFERING_NAME]] to a named or implied competitor.
- **Political content:** permitted only if [[POLITICAL_CONTENT_ALLOWED]] is true.
- **No medical/treatment-replacement implication** for any topic governed by [[REQUIRED_FRAMING]].
- **No manufactured scarcity** — campaign urgency must map to real dates/seats only.

---

## 7. Tone notes (register modulation vs the brand default)

The brand's default voice is [[VOICE_DESCRIPTORS]] (do: [[VOICE_DO]]; don't: [[VOICE_DONT]]; reading level [[READING_LEVEL]]). This section captures **only how [[OFFERING_NAME]] modulates that default** — it does not restate the whole voice canon.

- **Register shift:** `<how this offering sounds relative to brand default — e.g. "the brand voice at half the volume — quieter, more interior" — or "no shift; brand default applies">`
- **Lean into:** `<the [[VOICE_DO]] traits this offering should emphasize>`
- **Pull back on:** `<the [[VOICE_DONT]] traits especially dangerous for this offering>`
- **Sample feel (good):** echo [[SAMPLE_LINES_GOOD]], tilted to this offering's register.
- **Sample feel (avoid):** echo [[SAMPLE_LINES_BAD]], plus any offering-specific anti-pattern.
- **CTA voice:** follow [[CTA_STYLE]]; never use [[CTA_FORBIDDEN_PHRASES]]; route to [[CONTACT_WHATSAPP]] / [[CONTACT_INSTAGRAM]] per the brand's contact conventions.
- **Visual register cue (for the visual ticket):** carries [[VISUAL_REGISTER]] / [[VISUAL_STRATEGY]]; respects [[NON_DISCLOSURE_RULES]] in imagery too.

---

## 8. Spotlight angles / seed-angle list

A **positive** starter set of distinct angles for [[OFFERING_NAME]]. The Offering Content Agent loads these alongside the §9.1 angle lenses and obeys the §9.4 **idea-not-rerun** rule (read the Content Ledger first; never repeat an *idea*, even with new words). These are seeds to spark variety — **not a template to cycle through**; quality and freshness are the only constants (variety-by-message, never a fixed rotation).

| # | Seed angle | Audience moment it speaks to | Phase (§4.1) | Notes / claim dependency |
|---|------------|------------------------------|--------------|--------------------------|
| 1 | `<angle>` | `<who/when>` | 0 | `<draws on §3.x; any VERIFIED claim needed?>` |
| 2 | `<angle>` | `<who/when>` | 0 | |
| 3 | `<angle>` | `<who/when>` | 1 | `<campaign-only if has_dates>` |
| 4 | `<angle>` | `<who/when>` | 2 | `<in-program; zero promo>` |
| 5 | `<angle>` | `<who/when>` | 3 | `<retention; never guilt>` |

> Pull at least one concrete, sensory, or local anchor per piece from [[LOCAL_DETAIL_BANK]] (the §9.1 specificity rule). Generic is rejected. When the seed list is exhausted, generate fresh angles via the §9.1 lenses — the Brief seeds variety, it does not cap it.

---

## 9. funnels_from (optional cross-offering funnel)

Fill **only** if `funnels_from` is set in §0. Defines how [[OFFERING_NAME]] organically follows another offering.

- **Matures from:** `<funnels_from offering name + id>`
- **Natural bridge:** `<the honest reason a graduate of that offering is ready for this one>`
- **Timing guardrail:** introduce only once the prior experience has matured (§2.3); soft and organic, **never** aggressive, **never** before the person is ready.
- **What carries over:** `<assumed knowledge / vocabulary the graduate already holds>`

---

## 10. Visual handoff hints (for the Visual Production Agent)

Not a visual spec (that lives in the visual canon) — just the offering-specific facts the visual ticket needs.

- **Brand visual frame:** logo [[LOGO_ASSET]], wordmark [[WORDMARK_TEXT]], palette [[PALETTE_HEX]] (dark-bg accent [[ACCENT_DARK_BG]], light-bg accent [[ACCENT_LIGHT_BG]]), headline font [[HEADLINE_FONT]], label font [[LABEL_FONT]].
- **Register / variety:** [[VISUAL_REGISTER]] · [[VISUAL_VARIETY]] · [[VISUAL_STRATEGY]].
- **Hero source ([[BRAND_TYPE]]-dependent):** `concept_led` → generate the single feeling-image; `product_led` → real `products/` asset as hero, generation reserved for background/scene.
- **Image provider / tier:** [[IMAGE_PROVIDER]] at [[IMAGE_QUALITY_TIER]] (image default `gemini_image_pro` / Nano Banana Pro; operational alias `gemini-flash-latest`; **confirm names/IDs at build time**). No silent model swaps.
- **Disclosure in imagery:** imagery obeys [[NON_DISCLOSURE_RULES]] exactly as captions do — never depict a withheld mechanism.

---

## 11. Governance

- **Approval mode:** [[APPROVAL_MODE]] (auto-publish, if ever enabled, is gated by [[TRUST_THRESHOLD]] and the master kill-switch; defaults to manual).
- **Per-offering re-keying:** budget (PRD §13.2), memory (§8.1), pause/status all keyed by `offering_id` — pausing this offering does not touch others.
- **Maintenance:** the Strategist updates this Brief on owner request; material changes reset `confirmed_by_owner` to `false` until re-confirmed.
- **Locale / mission anchor:** all of the above is read in the context of [[BRAND_SHORT_NAME]]'s mission ([[MISSION]]), locale [[LOCALE]], and the brand's [[NON_DISCLOSURE_RULES]] / [[CLAIMS_FORBIDDEN]] boundaries — which always win over any angle, claim, or logistic in this Brief.

---

### Filling checklist (Strategist)
- [ ] §0 front-matter complete; `offering_id` stable; `funnels_from` set or empty intentionally.
- [ ] §1–§3 accurate and **non-trivialized**; "what it is NOT" guards the common misread.
- [ ] §4 claims sit inside [[CLAIMS_ALLOWED]] with [[REQUIRED_FRAMING]] hedges; quantitative claims point to VERIFIED Claim Bank entries.
- [ ] §5 logistics current and owner-confirmed (blanks over guesses).
- [ ] §6 forbidden/non-disclosure boundaries restated for this offering.
- [ ] §7 register modulation stated **relative to** the brand default, not a re-spec of voice.
- [ ] §8 ≥ 3 distinct seed angles spanning the relevant phases; none a reskin of another.
- [ ] §9 filled iff `funnels_from` set.
- [ ] Owner confirmed → set `confirmed_by_owner: true` + `last_confirmed`.
