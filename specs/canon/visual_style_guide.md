# Visual Style Guide — [[BRAND_NAME]]

> **Template status.** This is a GENERIC, product-agnostic canon document for Agent Atelier. Every `[[TOKEN]]` is resolved from the Brand Kit at build/resolve time. Do not hand-edit resolved brand values into the body — keep this file as a clean template.

This is the canonical rule set for **how every image is made**. The Visual Production Agent produces against it; the CreativeDirector (CD) reviews every visual against it. If a visual fails any **hard rule**, it is rejected on sight.

This guide is **subordinate to [`visual_engine`](./visual_engine.md)**. `visual_engine` governs the visual *strategy and feeling* ([[VISUAL_STRATEGY]], [[VISUAL_REGISTER]]) — the higher-order decision of what a piece should make a viewer feel and how variety is achieved across the feed ([[VISUAL_VARIETY]]). This guide governs the *mechanical craft* of executing that decision into a shippable asset. Where the two appear to conflict, `visual_engine` wins on strategy; this guide still governs execution mechanics (overlay, branding, OCR gate, aspect ratio, hosting). **Scoping (live-engine reconciliation):** the person-photo sections (demographics, gesture formulas, person-shot skeleton and checklist) apply **ONLY when a person is the subject** — drop them entirely for typographic / research-card / detail / place / metaphor / illustrated / abstract treatments.

Pair this with:

- [`brand_voice`](./brand_voice.md) — the image carries the same voice the caption carries ([[VOICE_DESCRIPTORS]]). Voice do: [[VOICE_DO]]. Voice don't: [[VOICE_DONT]].
- [`visual_concepts`](./visual_concepts.md) — loaded **alongside this guide for every visual decision**. It governs *what the picture is of* (concept selection); this guide governs *how it is made*. Where `visual_concepts` and the demographic/diversity section (§5a) overlap, `visual_concepts` wins on concept selection; §5a still governs subject demographics and variation whenever a person is in frame.

---

## 1. Scope

- Governs all static images for the configured channels: [[CHANNELS]].
- **In scope:** single-frame photographic/asset images; carousels.
- **Out of scope (deferred):** Reels/video and short-form video thumbnails. These get their own appendix once a test is run per format.
- When a piece ships to a channel where the caption sits below the image card, the overlay rules still apply — the image must work **standalone in feed and as a forward/share**.
- **Carousel note:** each carousel slide is governed by the same hard rules below. One subject/template is held consistent across all N slides (carousel consistency). Slide-specific layout guidance (title slide vs. body slides vs. closing slide) is deferred to a §13 appendix pending the first carousel test.
- **Brand type ([[BRAND_TYPE]]):**
  - `concept_led` — the Visual Production Agent generates the single image that delivers the feeling.
  - `product_led` — a real asset from [[OFFERINGS]] is the hero; generation is reserved for background/scene, with the real hero composited in. §5a (subject demographics) applies only to frames containing a person.

---

## 2. Hard rules — reject on sight

A visual must satisfy **all four** of these or it does not ship:

1. **Hook overlay present and legible at thumbnail size.** (See §3.)
2. **[[BRAND_NAME]] wordmark present.** (See §4.)
3. **Culturally appropriate [[LOCALE]] register.** (See §5.)
4. **Subject diversity — no repeated archetype.** (See §5a.)

A visual that breaks any of the prohibitions in §8 is also rejected on sight.

These four are enforced as part of the CD review (Gate 0 + checklist, §10) and the deterministic gates (OCR text-free §9, aspect ratio §9, byte-serving host §9). Safety-relevant prohibitions **fail closed**.

---

## 3. Hook overlay (mandatory)

Every image must carry the post's hook (or a 4–10 word distillation of it) as overlaid typography composited **on top of** the image.

### Why
The image is what stops the scroll. If the hook lives only in the caption, the post is invisible in feed. The hook on the image is what earns the stop.

### Rules

- **Length:** 4–10 words. If the caption hook is longer, distil — don't crop mid-sentence.
- **Wording:** must mirror, not contradict, the caption hook. Same promise, same register ([[VOICE_DESCRIPTORS]]). The overlay restates the caption's promise; it does not invent a louder one.
- **Position — RECONCILED (live-engine board direction, 2026-06-30): the type block sits at the BOTTOM.** The compositor places kicker → accent rule → headline → subhead → CTA → brandmark as one bottom-anchored stack on the feathered scrim (see `tools/reference/paperclip_caption.py`); the photograph keeps its **lower ~40% clean** for it, with the subject in the upper/central area — **never reserve the top third**. Where any older top-third guidance in this guide conflicts, the bottom-stack rule wins (`visual_engine` §11).
- **Typography:**
  - High contrast against the area it sits on. If the background is busy, add a subtle scrim (soft-edged 10–25% black gradient) — not a hard box.
  - Use the brand headline face: [[HEADLINE_FONT]]. Weighted enough to read at a ~150px thumbnail. Avoid thin display weights.
  - Sentence case or Title Case. **No all-caps** unless [[VOICE_DESCRIPTORS]] explicitly calls for it (all-caps tends to read shouty and breaks an invitational register).
  - One typeface, one weight per overlay. No mixing. Labels/eyebrows use [[LABEL_FONT]].
- **Language match:** overlay language matches the caption language for that piece, drawn from [[LANGUAGES]]. Render in the script native to that language. **Never transliterate.**
- **Thumbnail test (required before submit):** view the rendered, composited image at ~150×150 px. If you cannot read the hook in two seconds, it fails.
- **Composition discipline:** the photograph must be composed *with overlay space in mind*. Generate with the **lower ~40% clean** (subject upper/central) so the bottom type stack never collides with the subject's face, hands, or focal gesture.

### Forbidden in overlays

- Clickbait phrasings ("You won't believe…", "The one thing…").
- Fear-bait ("Stop doing this", "If you don't, you'll regret…").
- Comparative framing — unless [[COMPARATIVE_CLAIMS_ALLOWED]] permits it.
- Any promise beyond what [[CLAIMS_ALLOWED]] permits / what [[CLAIMS_FORBIDDEN]] prohibits (see the brand's safe-language / claims canon and [[NON_DISCLOSURE_RULES]]).
- Any phrase in [[CTA_FORBIDDEN_PHRASES]].
- Emoji-as-noun ("✨ peace ✨"). Words do the work.

---

## 4. [[BRAND_NAME]] branding (mandatory)

Every image carries the **[[BRAND_NAME]]** wordmark. If the official logo asset [[LOGO_ASSET]] is available, use the logo + wordmark lockup; until then, the wordmark text [[WORDMARK_TEXT]] alone is the minimum.

### Rules

- **Placement:** bottom-right (default) or bottom-center. Never top — the top is reserved for the hook (§3).
- **Sizing:** visible without dominating. Target wordmark cap-height ≈ 2.5% of image height; logo lockup ≈ 4–5% of image height.
- **Contrast:** legible on the chosen ground. If the bottom of the image is busy, sit the wordmark on a subtle scrim matching §3's scrim treatment, so overlay and branding feel like one system.
- **Color:** brand-consistent, drawn from [[PALETTE_HEX]]. Default to [[ACCENT_DARK_BG]] treatment on warm/dark grounds and [[ACCENT_LIGHT_BG]] treatment on light grounds. No color shifts away from the approved palette.
- **Never:** stretch, rotate, heavily drop-shadow, place behind the subject's face, or pair with a sponsoring third-party logo.

### Asset sourcing TODO (carry until resolved)

- Source the official [[BRAND_NAME]] wordmark + logo asset (raster + vector, with safe-zone spec) into [[LOGO_ASSET]]. Until that asset exists, every image uses the typeset wordmark [[WORDMARK_TEXT]] in [[HEADLINE_FONT]], colored per ground from [[PALETTE_HEX]]. File the asset in the brand asset store and update this section with the exact filename + safe-zone rule.

---

## 5. Cultural register ([[LOCALE]])

The image must read like it belongs to [[AUDIENCE_PERSONA]] in [[LOCALE]] — recognisable to the people the brand actually serves. The image model's default for most categories drifts toward generic Western stock; we counter that explicitly.

### Subject

- **Demographic cue:** prefer subjects consistent with [[AUDIENCE_PERSONA]] (appearance, dress, and bearing native to [[LOCALE]]). Specify an age band when the brief implies one.
- **Dress:** default to attire native to [[LOCALE]] and appropriate to the offering context. Other registers (e.g. office/commute/contemporary) are opt-in only when the brief explicitly calls for them.
- **Setting:** default to authentic local settings drawn from [[LOCAL_DETAIL_BANK]] — real, lived-in detail rather than staged stock. Alternate/contemporary settings are opt-in for specific pieces, not the default.
- **Light:** warm, soft, directional unless [[VISUAL_REGISTER]] specifies otherwise. Avoid hard, flat overhead light and any treatment that drifts into a register the brand does not claim.

### Anti-cues (use as negatives in every prompt)

These are **required additions** to the prompt, not stylistic suggestions — the model's defaults are wrong without them.

- A negative line excluding demographics that do not fit [[AUDIENCE_PERSONA]].
- `Not a stock-wellness/brochure/studio shoot` — i.e. exclude the generic, staged stock look the model defaults to for this category.
- Exclude any iconography, symbols, or props the brand does not claim (see [[CLAIMS_FORBIDDEN]] and [[NON_DISCLOSURE_RULES]]).

Append subject- and setting-specific anti-cues from §6 to these defaults.

---

## 5a. Subject diversity (mandatory) — when a person is in frame

§5 is the *register*. §5a is *who within that register* — the rule that stops every image being the same single archetype. (For `product_led` frames with no person, this section applies only to any incidental human element.)

### Why
A feed where every image converges on one face/age/outfit reads as a single person repeating, which kills engagement and makes the channel look like it runs off one stock photo. The audience spans many kinds of people within [[AUDIENCE_PERSONA]]; the feed has to look like it. This implements [[VISUAL_VARIETY]] at the level of human subjects. We do **not** depart from the [[LOCALE]] register — we widen *which* person within it is in frame.

### Variation dimensions

Every brief must consciously choose across these. The "default to avoid" column is the model's lazy answer; the "vary by" column is the rule. Tune ranges to [[AUDIENCE_PERSONA]].

| Dimension | Default to avoid | Vary by |
|-----------|------------------|---------|
| **Gender** | The same gender every time | Balance across the genders and groupings present in [[AUDIENCE_PERSONA]] (individuals, pairs, intergenerational groups). Pick by topic register, not by habit. |
| **Age** | A single narrow age band | Span the full range present in [[AUDIENCE_PERSONA]] (younger through elder). Actively include older subjects where they fit the audience. |
| **Clothing** | One default garment/color | Vary garment and palette within the [[LOCALE]] register and [[PALETTE_HEX]]-compatible tones — not a single repeated outfit. |
| **Posture / activity** | One repeated pose | Match posture/activity to the piece's subject, not to visual habit. |
| **Setting** | One repeated corner/backdrop | Rotate across authentic settings from [[LOCAL_DETAIL_BANK]] — still in-register, just not always the same spot. |
| **Lighting mood** | One repeated lighting look | Pick a mood that fits the piece's register from the range allowed by [[VISUAL_REGISTER]], not always the same one. |

### Pre-generation checklist (Visual Production Agent runs this before writing the prompt)

- [ ] Look at the last 2–3 generated images on the feed (the system of record — Google Sheets/Drive — holds the prior shipped pieces and their image links).
- [ ] Pick **at least 2 dimensions** from the table above that this image will deliberately differ on.
- [ ] Encode those differences explicitly in the `[SUBJECT]` and `[SETTING]` blocks of the §9 prompt skeleton.
- [ ] If the brief locks one dimension, still vary the *other* dimensions against the previous image.

### What §5a does not change

- The [[LOCALE]] register from §5 still holds. Every subject remains recognisably part of [[AUDIENCE_PERSONA]], in an authentic setting and appropriate dress. We vary *within* the register, not away from it.
- Gesture/posture formulas (§6) still apply. Posture variation means a different *posture*, not a wrongly-shaped *gesture*.
- Anti-cues (§5) still apply to every prompt regardless of which dimensions we vary on.

### Out of scope for now

Recurring named characters (a curated, deliberate cast that reappears across pieces) is a future direction — opt-in and curated, not the default-drift this section corrects. Do not introduce recurring characters until a future version defines the cast spec; treat each image as a fresh subject.

---

## 6. Gesture, posture, and body language

When a person and a meaningful gesture/posture are in frame, the model's defaults drift (e.g. it cups or clasps hands when "open" was wanted). **Lock the exact gesture in the prompt, verbatim.**

### Canonical gesture/posture formula library

- Maintain a brand-specific library of canonical gesture/posture formulas here, each written as an exact, unambiguous prompt phrase with explicit negatives (what the hands/body are **not** doing).
- If a brief introduces a new gesture or posture not yet covered, **draft its formula here before generating**, then commit it back as a new entry. The library grows from real briefs.

### Body-language defaults

- **Expression and bearing** match the brand's emotional register ([[VISUAL_REGISTER]]). Avoid the generic stock-photo expression (performative, over-blissful, or the "gazing into middle distance" look).
- **Posture** is natural and authentic to the activity, not staged-rigid and not slumped.
- Keep gestures anatomically correct — this overlaps with the AI-slop bar in §7.

---

## 7. Photorealism and quality bar

- **Default to the brand's visual register** [[VISUAL_REGISTER]]. Illustrated or graphic treatments are opt-in for explicit briefs (e.g. an explainer carousel page).
- **No AI-slop tells.** Reject on sight if visible: extra fingers, melted/ fused jewelry, asymmetric eyes, gibberish text in the background (signage, book spines), warped hands, unnaturally smooth/plastic skin, impossible reflections.
- **Texture and imperfection.** Real fabric wrinkles; real walls have shadows. Airbrushed-perfect generations read as fake. Add grounding cues like natural skin texture, soft directional light, lived-in materials, real environmental detail.
- **No watermarks or fake brand marks from the model.** If the model invents brand text in the background, reject and regenerate. (The OCR text-free gate, §9, catches baked glyphs deterministically.)
- The quality tier requested from the provider is [[IMAGE_QUALITY_TIER]].

---

## 8. What never ships

- Visuals carrying any claim beyond [[CLAIMS_ALLOWED]] / prohibited by [[CLAIMS_FORBIDDEN]] (e.g. no medical/therapeutic-claim iconography, no before/after body shots) — per the brand's safe-language canon. **Safety-relevant: fails closed.**
- Comparative visuals against competitors, alternatives, or rival symbols — unless [[COMPARATIVE_CLAIMS_ALLOWED]] permits.
- Political imagery, flags, or party colors as a focal element — unless [[POLITICAL_CONTENT_ALLOWED]] permits.
- Fear-coded imagery (anxiety/isolation as the hook) — keep to the brand's invitational register.
- Children as primary subjects unless a guardian-consent flow is in place (out of scope until defined).
- Faces of identifiable real people without a release on file.
- Anything that violates [[NON_DISCLOSURE_RULES]] or [[REQUIRED_FRAMING]] (e.g. using a named figure's image in a way that misattributes the brand's own words to them — quote with attributed text, never a face under a paraphrase).

---

## 9. Prompt structure, text-free generation, and deterministic gates

### 9.1 Canonical prompt skeleton

Image prompts use this skeleton. Order matters — anchor the subject before the setting, the setting before the light, the negatives at the end.

```
[SUBJECT — demographic + age + dress + posture; must differ from the previous image on ≥2 §5a dimensions]
[GESTURE FORMULA from §6, verbatim]
[SETTING — authentic [[LOCALE]] specifics from [[LOCAL_DETAIL_BANK]]; vary the room/moment from the previous piece]
[LIGHT — pick from the range allowed by [[VISUAL_REGISTER]] to fit the piece, not from habit]
[STYLE — register per [[VISUAL_REGISTER]], natural texture, no AI-slop, real materials]
[COMPOSITION — text-free; reserve clean space (headroom top third / clean center for hook; lower band clean for wordmark)]
[NEGATIVES — defaults from §5, plus piece-specific]
```

### 9.2 Text-free generation + composited brand type system (hard invariant)

- **The image model renders NO text.** We composite ALL type ourselves (hook overlay §3, wordmark §4). The justification is **brand-exactness + determinism** — exact fonts ([[HEADLINE_FONT]] / [[LABEL_FONT]]), exact kerning, the scrim, and an OCR-verifiable invariant — *not* a claim the model can't render text.
- The photo is generated **clean**, with the lower band (~40%) and the hook zone reserved as empty space.
- The hook overlay and wordmark are added in a **separate compositing pass** on top of the generated photograph — never requested from the model. Treat the model output as the *photograph*; treat overlay + branding as the *compositing pass*.

### 9.3 OCR text-free gate (deterministic)

- A **deterministic OCR check on the raw, pre-composite image** (Cloud Vision, or an equivalent classical OCR) runs as the reproducible pass/fail. A Gemini multimodal OCR may serve only as a non-deterministic **secondary**.
- Any baked glyphs detected → **automatic fail → regenerate**. This gate runs before the compositing pass.

### 9.4 Channel aspect ratios and resolution

- Output format is per-channel and Brand-Kit-resolved from [[CHANNELS]]. Normative defaults:
  - **4:5 portrait at 1080×1350** (default feed).
  - **1:1 at 1080×1080.**
  - **9:16 at 1080×1920.**
  - 16:9 for video-style channels when configured.
- Base render **≥ 1080px on the short edge** (1024px upscales poorly on common feeds). A deterministic check asserts the final asset matches the channel's required aspect ratio at ≥1080px short edge.

### 9.5 Byte-serving hosting rule

- The hosted asset must be retrievable as **raw `image/*` bytes from a public/signed URL** (a public/signed object-store URL, or a direct-download byte-serving endpoint) — **not** a document-viewer page.
- A pre-publish check asserts the URL returns **HTTP 200 with an `image/*` content-type**. (This is required for the auto-publish path; the manual handoff is unaffected but should still host a clean byte-serving asset.)

### 9.6 Provider and model discipline

- Images are generated via [[IMAGE_PROVIDER]] (default: a Gemini-native image+edit model — confirm the current marketing name and API ID against live docs at build time; do **not** hard-code a name in config). A Google-native generator is the fallback; a cross-provider option is selectable via the Brand Kit token.
- A Gemini-native image+edit model is the default because the workload needs (a) text-free generation with reserved space, (b) carousel consistency across N slides, and (c) `product_led` real-hero compositing/editing.
- **No silent model swaps.** A provider/model error stops and escalates rather than quietly substituting a different model.

---

## 10. Review checklist (CD uses this) — pre-render and post-render passes

The CD review runs in two passes: a **pre-render pass** (brief + prompt: confirms MESSAGE + FEELING + TREATMENT, §5a dimension choices, gesture formulas, negatives) and a **post-render pass** (the rendered + composited asset against the checklist below).

**Start every review with Gate 0. Do not proceed past Gate 0 until it passes.**

### Gate 0 — Scroll Test (mandatory first gate)

> *Per [`visual_engine`](./visual_engine.md).*

- [ ] **Gate 0 PASS/FAIL:** View hook + image at thumbnail size (~150×150 px) for exactly two seconds. Would [[SCROLL_TEST_PERSONA]] stop scrolling? If the honest answer is "maybe," the answer is **no** — return for revision. Only proceed to the checklist below if Gate 0 passes.

---

A visual passes the items below only if Gate 0 already passed. Anything false is grounds for revise or reject.

- [ ] Hook overlay present, 4–10 words, mirrors caption, legible at ~150×150 thumbnail.
- [ ] [[BRAND_NAME]] wordmark present, bottom region, visible without dominating, palette-correct.
- [ ] Subject reads as [[AUDIENCE_PERSONA]] within the [[LOCALE]] register (or whatever the brief specifies — never defaulted-generic-Western).
- [ ] **Subject differs from the previous 2–3 shipped images on ≥2 §5a dimensions. No back-to-back same-archetype shipping.**
- [ ] Setting reads authentic to [[LOCALE]] unless the brief explicitly opts into an alternate register.
- [ ] Gesture matches a canonical formula in §6 — hands/body are not in a drifted default unless that was the brief.
- [ ] Light/mood fits [[VISUAL_REGISTER]] and the piece (not a habitual default unless §5a deliberately chose it).
- [ ] No AI-slop tells (fingers, jewelry, eyes, background text, texture).
- [ ] No prohibited content from §8. Safety-relevant prohibitions fail closed.
- [ ] **Text-free OCR gate passed** on the raw pre-composite image (§9.3).
- [ ] **Aspect ratio + ≥1080px short edge** correct for the channel (§9.4).
- [ ] **Byte-serving host check** passes (HTTP 200, `image/*`) for the auto-publish path (§9.5).
- [ ] Photo + overlay + wordmark feel like one composed system, not three layers stacked.
- [ ] Alt text authored for the asset (single owner per the pipeline spec).

The CD↔owner agreement rate feeds the trust signal; auto-advance behavior is governed by [[APPROVAL_MODE]] and [[TRUST_THRESHOLD]].

---

## 11. When to escalate

- **Two above-bar variants, same prompt:** default to the brand's primary register ([[VISUAL_REGISTER]]) unless the brief opts into an alternate.
- **Gesture or subject reads off after one revision:** the fix is almost always tighter anti-cues, not a full prompt rewrite. Pull the exact formulas from §5 and §6.
- **The overlay text fights the photograph:** the photograph is the problem, not the overlay. Regenerate with explicit reserved space in the prompt.
- **Brief asks for the same archetype as the last image** (same gender + age band + clothing register, or same posture + setting): push back on the **brief itself**, not just the rendered image. Two-in-a-row of the same archetype fails §5a even if each is individually brand-on. Ask the upstream agent (or CD) to flex at least two §5a dimensions; otherwise reject the brief, not just the image.
- **Brief asks for something this guide doesn't cover** (e.g. children, video frame, identifiable real person, a recurring named character): pause and ask CD before generating.
- **Provider/model error or an out-of-policy generation that can't be brought in-bounds:** stop and escalate — no silent model swap, fail closed on safety-relevant cases.

---

## 12. Versioning

- This is the generic Agent Atelier template. On resolve, the implementing instance stamps a brand-specific version line here (date + change summary + driving directive/ticket). Re-verify provider/model identifiers, channel limits, and aspect-ratio defaults against live docs at each build (do not trust the training cutoff).
- **Planned appendix (§13):** carousel layout rules (title/body/closing slides), once the first carousel test is complete.
- Re-confirm safe-language / claims canon ([[CLAIMS_ALLOWED]] / [[CLAIMS_FORBIDDEN]] / [[NON_DISCLOSURE_RULES]]) and any quantitative-claim re-verification cadence ([[CLAIM_REVERIFY_MONTHS]]) whenever a visual carries a factual or numeric assertion.
