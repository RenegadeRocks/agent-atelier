<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §11 (source lines 1191–1236). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 11. Visual generation & typography subsystem

### 11.1 Image generation (pluggable)

- **Provider abstraction** — a single `ImageGenerator` interface; default **Nano Banana Pro** (the Gemini-3-era Gemini-native image+edit model; the Brand Kit token is `gemini_image_pro`, decoupled from the marketing name so a rename can't break config), with **Imagen** as a Google-native fallback and **Replicate `gpt-image-*`** as the cross-provider option, selected by `brand_kit.image_provider`.
- **Why a Gemini-native image+edit model is the default.** This workload is not plain text-to-image: it needs (a) **text-free** generation with reserved space (we composite type ourselves — §11.2), (b) **carousel consistency** — one subject/template held across N slides, and (c) **`product_led` real-hero compositing/editing** — placing a supplied product/logo into a generated scene. A native image-*editing* model is the better fit for (b) and (c) than a pure generator; Imagen stays the fallback for straight generation. (These comparative strengths are the *expected* advantage of the Nano Banana Pro line, not a settled benchmark — confirm against live docs/benchmarks at build time, exactly as for the model ID; §14.3, where only a live 404 is evidence a configured model does not exist.)
- **No silent model swaps** — on any provider error: capture the verbatim error, stop, escalate. *(Encodes a real prior incident: a silent model swap produced off-spec output that the review gate caught.)* See the inverse rule in §14.3.
- **Quality tiers** — floor/default from `image_quality_tier`; a CD "premium" tag upgrades a piece to `high` and never downgrades below the floor (§9.2). Report image counts/cost on every ticket.
- **Capture per generation** — exact prompt, model + tier, provider prediction id, asset attached to the task.
- **One image per call** — carousels = N renders sharing one fixed template; number slides in order.

### 11.2 Caption-Composer (the typography step — a proper, swappable capability)

A small **Caption-Composer service/tool** (exposed over MCP), not a hand-run script. Requirements:

- **The image model renders NO text; we composite all type ourselves.** The justification is **brand-exactness + determinism** (exact fonts/kerning, the scrim, an OCR-verifiable invariant) — *not* a claim that the model can't render text. Modern Gemini-native image models render text well, which is precisely why we **enforce** the text-free invariant rather than rely on the model. The photo is generated clean with the lower ~40% reserved. A **deterministic OCR check on the raw pre-composite image** — use **Cloud Vision** (or an equivalent classical OCR) for the reproducible pass/fail; a Gemini multimodal OCR is a non-deterministic *secondary* only — catches any baked glyphs → automatic fail → regenerate.
- The Composer overlays the **brand type system** (constant across the feed): serif headline + accent rule, optional small-caps kicker/sub-line, logo + wordmark — resolved from the Brand Kit.
- **Theme/scrim colors** — light photo → dark text on a **`accent_light_bg`** cream scrim; dark photo → light text on a **`accent_dark_bg`** dark scrim (these are distinct from `palette_hex`, the accent-rule gradient). The scrim sits behind **every** line (an unreadable first line is a reject).
- **Output formats per channel** — feed example **4:5 portrait at 1080×1350** (alternates 1:1 1080×1080, 9:16 1080×1920); 16:9 for channels like YouTube when configured. Base render ≥ **1080px** on the short edge (1024px upscales on IG). Aspect ratio is already per-channel and Brand-Kit-resolved — only the example numbers are normative defaults.
- **Implementation freedom** — any stack (a serverless function on Google Cloud is the recommended default for portability); the **owner has no library preference — the executor picks the rendering library at build time**; the contract is the requirement, the implementation is disposable.

```gherkin
Scenario: Brand-consistent typography compositing
  Given a clean generated photo that passes the text-free OCR check
  When the Caption-Composer renders the headline and brandmark
  Then the type uses the brand fonts and theme accent colors (accent_light_bg / accent_dark_bg)
  And the scrim sits behind every line of text
  And the output matches the channel's required aspect ratio at >=1080px short edge
  And no text was baked by the image model
```

---

**OCR text-free precision (Day-4 functional-correctness / reproducible pass-fail: don't reject a real street scene for a shop sign).** The §11.2 deterministic OCR check is made precise so incidental signage passes but a baked headline fails:
- **Geometry first:** fail if **any** detected text overlaps the **reserved lower band** (the ~40% where we composite type) — that band must be clean.
- **Outside the band**, detected text fails only if (a) total character-area exceeds `ocr_text_area_max` of the frame (pinned in config, e.g. 2%), **or** (b) detected tokens fuzzy-match the headline/caption about to be composited. Small incidental signage below threshold is **allowed and logged**.
- Pin the **OCR confidence floor** and that **Cloud Vision is the deterministic arbiter**; a Gemini multimodal OCR is a non-deterministic secondary only.

```gherkin
Scenario: Incidental scene signage is allowed; baked headline is rejected
  Given a generated shopfront photo with a small painted sign outside the reserved band and below ocr_text_area_max
  Then the image passes
  But if any glyph falls in the reserved band, or fuzzy-matches the intended headline, it fails and regenerates
```


