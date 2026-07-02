---
name: intake-interview
description: Conduct the guided brand interview — one question at a time, ingest existing material, draft non-safety fields, elicit each safety prohibition explicitly — producing a validated Brand Kit and a first-light test post.
---

# intake-interview

The Brand Onboarding Strategist's procedure for onboarding a new brand (PRD §7.1, §7.2). It is
a conversational interview, not a dead form. It operates on the **read/draft/act ladder**: the
Strategist reads/drafts; the owner *acts* (approves). It never modifies agent code or engine
documents.

## Inputs

- The owner, in conversation.
- Optionally, ingestible material: a website URL, an existing Instagram handle, a brochure/PDF,
  a logo image.
- The Brand Kit schema (`brand_kit_version: 2`) as the target.

## Procedure

1. **Interview, one question at a time.** Ask in plain language; propose sensible defaults the
   owner can accept; keep YAML nesting shallow. Cover, in order:
   - **Identity** — `[[BRAND_NAME]]`, `[[BRAND_SHORT_NAME]]`, tagline, `[[LOCALE]]`,
     `[[LANGUAGES]]`, timezone, `[[MISSION]]`, `[[BRAND_TYPE]]`.
   - **Audience** — `[[AUDIENCE_PERSONA]]`, `[[AUDIENCE_PAINS]]`, `[[SCROLL_TEST_PERSONA]]`.
   - **Voice** — `[[VOICE_DESCRIPTORS]]`, `[[VOICE_DO]]`, `[[VOICE_DONT]]`,
     `[[READING_LEVEL]]`, `[[SAMPLE_LINES_GOOD]]`, `[[SAMPLE_LINES_BAD]]`.
   - **Visual identity** — `[[LOGO_ASSET]]`, `[[WORDMARK_TEXT]]`, `[[PALETTE_HEX]]`,
     `[[ACCENT_DARK_BG]]`, `[[ACCENT_LIGHT_BG]]`, `[[HEADLINE_FONT]]`, `[[LABEL_FONT]]`,
     `[[VISUAL_REGISTER]]`, `[[VISUAL_VARIETY]]`, `[[VISUAL_STRATEGY]]`, `[[IMAGE_PROVIDER]]`
     (default token `gemini_image_pro` / Nano Banana Pro — confirm name+ID at build time),
     `[[IMAGE_QUALITY_TIER]]`, people/product pools.
   - **Contact / CTA (used EXACTLY, never invented)** — `[[CTA_STYLE]]`,
     `[[CONTACT_WHATSAPP]]`, `[[CONTACT_INSTAGRAM]]`, `[[CTA_FORBIDDEN_PHRASES]]`.
   - **Channels & cadence** — `[[CHANNELS]]`, `[[POSTS_PER_WEEK_TARGET]]`,
     `[[STANDING_WEEK]]`, `[[RESEARCH_POST_MIN_PER_WEEK]]`, `[[MAX_POSTS_PER_WEEK]]`.
   - **Offerings** — `[[OFFERINGS]]` (each `[[OFFERING_ID]]` / `[[OFFERING_NAME]]` /
     `[[OFFERING_BRIEF]]`), flagship + optional inter-offering funnels.
   - **Territory** — `[[EVERGREEN_PILLARS]]`, `[[LOCAL_DETAIL_BANK]]`.
   - **Research policy** — `[[SOURCE_ALLOWLIST]]`, `[[SOURCE_DENYLIST]]`,
     `[[CLAIM_REVERIFY_MONTHS]]`, `[[REQUIRE_SECOND_SOURCE_FOR_QUANTITATIVE]]`.
   - **Publishing posture** — `[[APPROVAL_MODE]]`, `[[TRUST_THRESHOLD]]`.
2. **Ingest to auto-draft non-safety fields.** From any provided URL/handle/PDF/logo, draft
   answers for the owner to confirm. Marketing sources may seed identity, voice, visual, and
   offering fields.
3. **Safety fields are categorically different — elicit each explicitly.** Do **not** silently
   auto-draft `[[CLAIMS_FORBIDDEN]]`, `[[NON_DISCLOSURE_RULES]]`, or `[[REQUIRED_FRAMING]]`
   from marketing sources (which structurally never contain prohibitions). You may *propose*
   category/regulatory defaults inferred from the detected vertical, flagged as starting
   points, with 1-2 worked examples per field. Also confirm `[[CLAIMS_ALLOWED]]`,
   `[[COMPARATIVE_CLAIMS_ALLOWED]]`, `[[POLITICAL_CONTENT_ALLOWED]]`. These three fields
   (`claims_forbidden` / `non_disclosure_rules` / `required_framing`) **fail closed**: empty or
   unconfirmed = block publish, route to human.
4. **Validate.** Produce `brand_kit.yaml` + an `assets/` folder + a secrets reference; run
   schema validation; produce a short human-readable "brand one-pager."
5. **First light — TWO probes, both shown (§7.1).** Commission one test post end-to-end
   through the same pipeline (environment = `preview`; publish blocked at the gate) and show it
   to the owner. Run **one declared + one undeclared probe per run**:
   - **Declared probe:** steer toward a fault line the owner DID flag — for a `claims_forbidden`
     entry, write the caption that would violate it by one degree. Show **both artifacts**: the
     correctly-hedged safe output AND the blocked near-miss variant.
   - **Undeclared probe:** pick one category from the **§7.8 archetype safety starting-points
     column the owner did NOT confirm** (for `custom`, use the generic cross-vertical risk
     list) and probe it the same way — this surfaces unstated prohibitions.
   Record the outcome on a **FirstLightResult** (probes run, gate that caught each, owner
   verdict); the run is breaker-bounded like any other. Close with a **first-week dry-run**
   (materialize the standing week without publishing) so the owner sees the rhythm before
   go-live; the kit flips draft → active on owner sign-off.

## Output

A complete, schema-valid Brand Kit (YAML + asset files), a brand one-pager, one first-light
test post with **both probe artifacts** (safe output + blocked near-miss, declared + undeclared)
recorded on a FirstLightResult, and a first-week dry-run — presented for owner approval. No
agent code or engine document was modified.

## When to use / When NOT

- **Use** when onboarding a new brand, or when an owner wants to re-run intake / materially
  revise the Brand Kit via interview.
- **Do NOT use** for routine per-piece editing (a power user tweaks the editable structured
  Brand Kit view directly), and never auto-fill safety prohibitions from ingested marketing
  material.

Examples: "onboard [[BRAND_NAME]] from its website + Instagram handle + logo"; "run intake and elicit the non-disclosure rules with worked examples".
