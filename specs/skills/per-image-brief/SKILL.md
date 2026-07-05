---
name: per-image-brief
description: Turn an approved draft's intent into a complete per-image brief (MESSAGE / FEELING / TREATMENT / IMAGE / WORDS / LIGHT-MOOD / CHECK) that generates a variety-true, text-free, brand-cohesive image.
---

# per-image-brief

The Visual Production Agent's procedure for authoring the per-image brief that drives
generation (PRD §9.2, §10.1 `[VISUALIZE]`). Variety is decided fresh per post from THIS
message; brand cohesion is the constant (the brand type system, fixed `[[PALETTE_HEX]]`, and
`[[VISUAL_REGISTER]]` apply to every post). Convergence (dead sameness of subject/idea/
treatment) is the bug — not the brand identity.

Visual policy resolves from the Brand Kit: register `[[VISUAL_REGISTER]]`, variety dial
`[[VISUAL_VARIETY]]`, strategy `[[VISUAL_STRATEGY]]` (`concept_led` default | `product_led`),
provider `[[IMAGE_PROVIDER]]`, quality floor `[[IMAGE_QUALITY_TIER]]`.

## Inputs

- An approved `Draft` carrying the seed `visual_brief { message, feeling, treatment }`.
- For `product_led`: a real hero image from the product pool (`[[OFFERINGS]]` assets).

## Procedure

1. **Emotion-first.** Answer two questions before anything else: (1) what is this post saying?
   (2) what should a stranger feel in one second? Build the image from those answers.
2. **Choose a treatment (don't cycle).** Pick from the §9.2 menu (real human moment,
   transformation, candid joy/belonging, intimate detail, place-with-feeling, physical
   metaphor, bold typographic statement, research/credibility card, illustrated explainer,
   carousel, texture/abstract). If `[[VISUAL_VARIETY]]` is `high`, narrow the treatment menu
   while still rotating subject/angle/composition. The chosen treatment **label** must not
   repeat the immediately-prior ledger label.
3. **Author the seven fields** (stored on the Draft, PRD §17):
   - **MESSAGE** — the one idea the image carries alone.
   - **FEELING** — the one-second emotional target.
   - **TREATMENT** — the chosen menu item + its label.
   - **IMAGE** — concrete scene/subject. For `concept_led`, describe the single generated
     image that delivers the feeling; for `product_led`, name the real `products/` hero and
     reserve generation for background/scene only.
   - **WORDS** — the headline/kicker to be composited later (NOT baked by the model).
   - **LIGHT-MOOD** — lighting and palette intent, true to `[[VISUAL_REGISTER]]`.
   - **CHECK** — the pass criteria: text-free generation, clean space reserved in the lower
     ~40% band, metaphor bridges in 2 seconds, nothing suggestive, non-disclosure honored.
4. **Bind non-disclosure to the scene.** `[[NON_DISCLOSURE_RULES]]` constrain both words and
   the depicted scene; never depict a proprietary mechanism. `[[CLAIMS_FORBIDDEN]]` and
   `[[REQUIRED_FRAMING]]` apply to on-image words.
5. **Generation guardrails.** Generate a **text-free** photo via `[[IMAGE_PROVIDER]]` (default
   token `gemini_image_pro` / Nano Banana Pro — confirm name+ID at build time). One unified, single-camera scene. Never split-screen, collage, diptych, or multi-panel compositions — express contrast within a single scene. Honor the
   quality floor: `[[IMAGE_QUALITY_TIER]]` is the default; a CD "premium" tag upgrades a
   single piece to `high`, never downgrades. No silent model swaps — on provider error, stop
   and escalate. A deterministic OCR check on the raw image enforces the text-free invariant.
6. **Carousel briefs.** One brief per slide; the slides carry the teaching, the outro carries
   the CTA.

## Output

A complete `visual_brief` on the Draft plus generation parameters (prompt, provider, tier),
ready to generate and then hand to `compose-caption`. Generation attaches prompt + provider +
prediction id + tier to the `Asset`.

## When to use / When NOT

- **Use** after CD approval, once per image/carousel slide, before generation.
- **Do NOT use** to write captions or composite typography (that is `compose-caption`), to
  approve craft quality (the CD's post-render pass does that), or to bake text into the image.

Examples: "author the per-image brief for the approved Wednesday research post"; "brief each slide of the 5-slide teaching carousel".
