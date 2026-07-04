---
name: compose-caption
description: Composite the brand type system (serif headline, accent rule, kicker, logo, wordmark) over a text-free photo with a readable scrim, render per-channel aspect ratios, host the asset, and author alt text.
---

# compose-caption

The Visual Production Agent's typography step, driving the Caption-Composer service over MCP
(`caption_compose`, PRD §11.2). The image model renders NO text; we composite all type
ourselves for brand-exactness + determinism + an OCR-verifiable invariant.

> **Reference implementation:** `tools/reference/paperclip_caption.py` — the PROVEN
> production compositor from the live Paperclip engine (feathered full-strength scrim,
> auto-shrinking headline max 3 lines, never-clip kicker auto-fit, wrapping subhead, CTA
> action line, luminance themes, bottom-anchored brandmark). **Adapt it (fonts/brand values
> from config — see `tools/reference/README.md`); do not reinvent its geometry** — the
> constants encode reviewed production taste and real CD root-cause fixes.

Type/theme facts resolve from the Brand Kit: headline `[[HEADLINE_FONT]]`, label/kicker
`[[LABEL_FONT]]`, logo `[[LOGO_ASSET]]`, wordmark `[[WORDMARK_TEXT]]`, accent-rule gradient
`[[PALETTE_HEX]]`, dark-photo scrim `[[ACCENT_DARK_BG]]`, light-photo scrim
`[[ACCENT_LIGHT_BG]]`.

## Inputs

- A clean, generated, **text-free** photo (the per-image-brief output) that has passed the
  deterministic OCR check.
- The WORDS from the `visual_brief` (headline + optional kicker/sub-line).
- Target channel from `[[CHANNELS]]`.

## Procedure

1. **Gate on text-free.** Run the deterministic OCR backstop (Cloud Vision or equivalent
   classical OCR) on the raw pre-composite image. Any baked glyph → automatic fail →
   regenerate (do not composite over a non-clean image). A Gemini multimodal OCR is a
   non-deterministic secondary only.
2. **Overlay the brand type system** (constant across the feed): serif headline in
   `[[HEADLINE_FONT]]` + the accent rule from `[[PALETTE_HEX]]`; optional small-caps kicker/
   sub-line in `[[LABEL_FONT]]`; logo `[[LOGO_ASSET]]` + wordmark `[[WORDMARK_TEXT]]`.
3. **Apply the theme scrim.** Light photo → dark text on a `[[ACCENT_LIGHT_BG]]` cream scrim;
   dark photo → light text on a `[[ACCENT_DARK_BG]]` dark scrim. The scrim sits behind
   **every** line — an unreadable first line is a reject.
4. **Render per-channel format.** Use the Brand-Kit-resolved aspect ratio for the channel
   (defaults: 4:5 1080×1350; alternates 1:1 1080×1080, 9:16 1080×1920; 16:9 where configured).
   Base render ≥ 1080px on the short edge.
5. **Host the asset.** Upload to Drive/GCS via the `drive` tool. For the auto-publish path,
   produce a raw `image/*` byte-serving public/signed URL (not a Drive viewer page); a
   pre-publish check asserts HTTP 200 + `image/*` content-type.
6. **Author alt text (single owner).** Write descriptive, naturally-searchable alt text (light
   IG-SEO; no keyword-stuffing). Alt text lives on the `Asset`, not the Draft, and its
   presence is enforced later at QUEUE by `ledger-audit`.
7. **Attach provenance.** Record prompt + provider (`[[IMAGE_PROVIDER]]`) + prediction id +
   tier on the `Asset`. For carousels, repeat per slide with `slide_no`.

## Output

A hosted, brand-composited `Asset` (image or carousel slides) with `drive_url`, optional
`byte_url`, and `alt_text` — ready for the CD post-render multimodal pass, then QUEUE.

## When to use / When NOT

- **Use** once a text-free image exists and needs brand typography, hosting, and alt text;
  also for `product_led` real-asset compositing.
- **Do NOT use** to generate the base photo (that is `per-image-brief`), to decide craft
  pass/fail (the CD post-render pass), or to composite over an image that failed the OCR
  text-free check.

Examples: "composite the headline + wordmark on the hosted 4:5 image and write alt text"; "render the 9:16 cover for the Reel-script carousel and host it for auto-publish".
