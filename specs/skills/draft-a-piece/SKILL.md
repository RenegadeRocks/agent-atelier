---
name: draft-a-piece
description: Ideate and draft one on-brand feed piece (idea + ledger fields + caption + visual brief + compliance block) from an assigned slot, ready for the ledger-linter and CD review.
---

# draft-a-piece

The core authoring loop for every content agent (Evergreen, Offering, Research-grounded).
Implements the `[IDEATE+DRAFT]` stage of the per-piece pipeline (PRD §10.1). One run
produces one `Draft` entity (PRD §17) for a single slot in the standing week.

Brand facts resolve from the Brand Kit at runtime. Mission: `[[MISSION]]`. Brand type:
`[[BRAND_TYPE]]` (selects the active hook/shape pack). Audience: `[[AUDIENCE_PERSONA]]`
with pains `[[AUDIENCE_PAINS]]`. Voice: `[[VOICE_DESCRIPTORS]]`, do `[[VOICE_DO]]`, don't
`[[VOICE_DONT]]`, at `[[READING_LEVEL]]`. Good/bad exemplars: `[[SAMPLE_LINES_GOOD]]` /
`[[SAMPLE_LINES_BAD]]`.

## Inputs

- `slot`: `{ day, track, language?, flag? }` from `[[STANDING_WEEK]]`. `track` is
  `evergreen`, `offering:[[OFFERING_ID]]`, or carries `flag: research_grounded`.
- Read access to the Content Ledger (Sheets), Creative Engine canon, Brand Voice canon,
  and (for offering slots) the Offering Brief for `[[OFFERING_NAME]]` — `[[OFFERING_BRIEF]]`.

## Procedure

1. **Read the ledger first (trajectory-critical).** Pull the trailing ~30 rows. Write down
   explicitly what NOT to repeat: the last 3 hook patterns, the immediately-prior caption
   shape, the back-to-back visual-treatment label, and any idea run in the last 30 days.
   This list is what keeps the linter (`ledger-lint`) green.
2. **Choose the language** per the per-piece rule (PRD §7.6). Default to the slot's
   `language`; else the primary of `[[LANGUAGES]]` for locale `[[LOCALE]]`.
3. **Find the idea.** Apply an angle lens to a flat topic.
   - Evergreen: draw from `[[EVERGREEN_PILLARS]]`; ground a `research_grounded` slot in a
     VERIFIED Claim-Bank `locked_sentence` (run `verify-a-claim` if none exists yet).
   - Offering: load `[[OFFERING_BRIEF]]` spotlight angles; represent `[[OFFERING_NAME]]`
     accurately, never trivialized; honor non-disclosure and funnel/timing guardrails.
   - Anchor with ≥1 concrete, sensory, local detail from `[[LOCAL_DETAIL_BANK]]` (generic
     copy is rejected by the CD).
4. **Choose hook + shape + format** from the active `[[BRAND_TYPE]]` pack, staying inside
   rotation limits: hook not in last 3 posts; shape ≠ immediately prior; aphorism shape
   ≤ 1-in-5 of the window; single image ≤ ~50%/week (carousel is the default for teaching).
   Make the carousel-vs-single decision consciously, per idea.
5. **Write the caption.** One idea only. Image-first (the image is the message; the caption
   adds one line). First line stands alone. Respect the channel length cap (delegated to the
   per-channel Style Guide). Soft CTA in `[[CTA_STYLE]]` style using only `[[CONTACT_WHATSAPP]]`
   / `[[CONTACT_INSTAGRAM]]`; never use `[[CTA_FORBIDDEN_PHRASES]]`. Tight hashtag set.
   Plain-speech guard: max one poetic fragment; every sentence passes "say it plainly to one
   real person"; never bend sacred/cultural terms (`[[NON_DISCLOSURE_RULES]]`).
6. **Write the visual brief onto the Draft** (handoff to `per-image-brief`): at minimum
   MESSAGE → FEELING → TREATMENT (+ image, words, light_mood). Treatment label must not
   repeat the immediately-prior ledger label.
7. **Assemble the draft doc:** idea sentence + ledger fields (hook, shape, format, visual
   treatment label, language, status), caption, hashtags, `visual_brief`, and a ≤8-line
   compliance block (claims used → VERIFIED `locked_sentence` ids; `[[REQUIRED_FRAMING]]`
   applied; `[[CLAIMS_FORBIDDEN]]` / `[[NON_DISCLOSURE_RULES]]` checked;
   `[[COMPARATIVE_CLAIMS_ALLOWED]]` / `[[POLITICAL_CONTENT_ALLOWED]]` honored).

## Output

A `Draft` ready for `[[CHANNELS]]`. Do not generate images here. Emit the draft, then the
pipeline runs `ledger-lint` (hard block on countable violations) BEFORE CD review. Do not
self-pause; produce into the queue.

## When to use / When NOT

- **Use** when a Managing-Editor slot is assigned and you are the owning content agent, or
  when an on-demand single piece is requested.
- **Do NOT use** for image generation/compositing (use `per-image-brief` + `compose-caption`),
  for verifying a statistic (use `verify-a-claim`), or to bypass the linter — drafting does
  not approve or queue anything.

Examples: "draft Tuesday's offering:[[OFFERING_ID]] piece in `[[LOCALE]]`"; "write Wednesday's research_grounded evergreen post from a VERIFIED claim".
