# tools/reference — proven implementations ported from the live Paperclip engine

**`paperclip_caption.py`** — the production Caption-Composer from the AOL/Paperclip system
(verbatim copy, 2026-07-04). This is the REAL brand type system the §11.2 Caption-Composer
spec was written from: feathered full-strength scrim (holds over bright photos), auto-
shrinking serif headline (max 3 lines), small-caps kicker with never-clip auto-fit, accent
rule, wrapping subhead, CTA action line, logo + wordmark brandmark, luminance themes
(light photo → dark text/cream scrim; dark photo → near-white text/dark scrim + shadow).

**Adapt, don't reinvent**, when implementing `caption_compose` (P1-B) — with these changes:
1. **Fonts:** the FONTS dict points at macOS paths. On Windows use
   `C:\Windows\Fonts\georgiab.ttf` (Georgia Bold — present by default) for the headline and
   a clean sans (`segoeui.ttf` / `bahnschrift.ttf`) as the label/kicker stand-in until the
   Brand Kit supplies font files (log the stand-in as a deviation). Resolve paths from
   config, never hardcode.
2. **Brand values from config/Brand Kit**, not literals: accent colors (`[[ACCENT_DARK_BG]]`
   / `[[ACCENT_LIGHT_BG]]` semantics are the two `accent` defaults in the script), logo
   path, wordmark text.
3. Keep the geometry constants (margin 7.5% W, headline 7.2% W, scrim feather 10% H,
   bottom paddings) — they encode reviewed production taste; expose as config only if a
   contract requires it.
4. The grammar contract is `specs/skills/compose-caption/SKILL.md`; the craft law is
   `specs/canon/visual_engine.md` §11.
