# Visual Engine — [[BRAND_NAME]] (variety by message)

> **Why this engine exists.** A feed dies two ways: by looking *grim* (cold, lifeless, documentary-empty pictures — vacant rooms, random object photos) and by looking *same* (every post collapsing to one subject, one palette, one treatment). Both come from asking *"which class is next?"* instead of *"what should a person feel seeing this post?"* This engine throws out class-rotation thinking entirely. The engine is: read the post's message, decide the feeling it must create, build the one image that delivers that feeling — and never let any single look become "the feed."

---

## 1. The only principle that matters

**A social feed lives on variety.** Its job is that no two posts look alike. The image is decided fresh, every time, from *this* post's message and the emotion it must spark in the first second of [[SCROLL_TEST_PERSONA]]'s scroll.

There is exactly one constant across the whole feed, and it is **not a look — it is character and cohesion**. Cohesion is carried by a small, fixed kit: the brand **type system**, [[PALETTE_HEX]], and the [[VISUAL_REGISTER]] — never by repeating a subject or composition. Character is [[VOICE_DESCRIPTORS]]: warmth, craft, emotional truth, [[LOCALE]]-rootedness, and the quiet authority of being research-backed. Sameness is not character. A feed of fifty beautiful-but-identical images is a failure, however beautiful each one is.

**The variety dial.** [[VISUAL_VARIETY]] tunes how far treatments may spread across the feed: a tighter setting keeps the look closer to the core kit; a wider setting invites bolder swings between treatments. Whatever the setting, brand cohesion (type system + [[PALETTE_HEX]] + [[VISUAL_REGISTER]]) is the floor and never the variable.

**The collapse we never repeat.** One subject every post → then one environment every post → the temptation to make "a single radiant look" every post. If you ever notice the last several posts converging on one subject, palette, or treatment, *that convergence is the bug* — not a style we found. Stop and break it.

## 2. How every image is decided (emotion first, never class first)

Before any prompt, answer two questions:

1. **What is this post actually saying?** (one sentence)
2. **What should a stranger feel in the first second?** (one feeling — caught/seen, relief, calm, delight, awe, curiosity, belonging, "I need to save this")

Then build the single image that delivers *that feeling*. The treatment changes because the feeling changes. That is the whole engine.

**The full emotional range is in bounds — including the hard ones.** Match the range to [[BRAND_TYPE]] and [[AUDIENCE_PERSONA]]: this is not a feed of permanent smiling. If a post is about a pain in [[AUDIENCE_PAINS]], *show the pain* — recognition is what stops the scroll. If a post is about relief, show the turn — the same person resolving it, or a before→after. Difficult feelings are allowed *when the post is about them*, and they hit hardest when the image resolves toward ease. What's banned is not a feeling — it's coldness, emptiness, and lifelessness for their own sake.

## 3. The palette is a menu, not a rota

These are treatments to *choose from* by what the message needs — not a list to cycle through. If a post needs a treatment that isn't here, invent it. The rule is the feeling; this menu only shows how wide the range is:

- **A real human moment, any emotion** — the feeling on a real face.
- **A transformation** — before→after in one frame or a 2-up. Often the most persuasive thing we own.
- **Candid connection / belonging** — genuine warmth between people. Not a glossy posed look — real, within [[VISUAL_REGISTER]].
- **An intimate detail** — hands, texture, light on a surface. Quiet, premium, tactile.
- **A place with feeling** — an environment that carries a mood. NOT empty-for-empty's-sake; a place qualifies only if it makes you *feel* something.
- **A physical metaphor** — only when a stranger can bridge it in two seconds with the on-image words (see §5). Otherwise it's just a photo of an object.
- **A bold typographic statement** — the line *is* the image. Premium editorial type on texture/color. Often the strongest scroll-stopper for a teaching or a research point.
- **A research / credibility card** — a designed stat or finding, authoritative and clean. This is how we earn trust in [[OFFERINGS]].
- **An illustrated explainer / infographic** — a different visual language entirely; great for "3 signs…", myth-vs-fact.
- **A carousel** — when one idea wants steps or a teach: a multi-step sequence, a myth→fact, a small lesson. Use freely; carousels are in scope.
- **Texture / abstract** — color, light, material as pure mood.

Mix these across the feed on purpose. Two posts in a row reaching for the same treatment is a flag — not forbidden, but justify it or change it. (The countable side of this is enforced by the deterministic ledger-linter before CD review; the *rendered* "visibly different" judgment is the CD's post-render pass — §9, §11.)

## 4. The quality bar — the real constant (every image clears this)

Whatever the subject, the image must be:

- **Alive, not empty.** It holds a feeling. If it reads as a vacant room or a lifeless still, it fails.
- **Warm and human**, rooted in real [[LOCALE]] life — light, skin, cloth, street, home, drawing on [[LOCAL_DETAIL_BANK]] — not stock-wellness, not spa, not brochure, not generic "global" filler.
- **Premium / crafted** to the [[VISUAL_REGISTER]] — composition, light, and type are deliberate; at least the floor tier [[IMAGE_QUALITY_TIER]], with the CD free to call a premium upgrade (§12).
- **Emotionally true** — a real feeling, never a posed stock cliché.
- **Scroll-stopping** — it earns the stop in a crowded feed. If it wouldn't stop *you*, regenerate.
- **Words-as-craft** — when text sits on the image (it often carries the hook), the typography is designed, legible, and beautiful. The words on the image are usually what's actually read — treat them as the headline, not a caption. Honor [[READING_LEVEL]].

Light, color, and palette are chosen for *this post's emotion*, never from habit. A calm post is not obligated to be bright; a heavy post is allowed to be dim — as long as it's alive and crafted.

## 5. Metaphor legibility

A metaphor that lives only in the caption is just a random object photo. The **two-second bridge test:** with only the on-image words (no caption), a stranger connects the picture to the idea in two seconds. Make the on-image line *be* the bridge, or anchor the metaphor in a real human/household moment. If neither works, the idea wants a human moment or a detail instead — choose again, don't force the metaphor.

## 6. Content non-disclosure — hard rules

[[NON_DISCLOSURE_RULES]] bind both the **words on the image** and the **scene depicted**. Treat each rule as a ceiling on what may be said *and* shown: never depict, teach, or give away the protected mechanism in image or text; stay at or below the framing the rule permits.

General compliance, every image:

- Only [[CLAIMS_ALLOWED]] are permissible; [[CLAIMS_FORBIDDEN]] never appear in words or scene.
- Comparative claims only if [[COMPARATIVE_CLAIMS_ALLOWED]]; political content only if [[POLITICAL_CONTENT_ALLOWED]].
- Any required framing in [[REQUIRED_FRAMING]] is honored.
- Research/statistics appear only from VERIFIED Claim-Bank entries with the locked sentence, subject to deterministic claim-grounding at compose/publish time. Quantitative claims observe [[REQUIRE_SECOND_SOURCE_FOR_QUANTITATIVE]] and re-verification every [[CLAIM_REVERIFY_MONTHS]] months; sources respect [[SOURCE_ALLOWLIST]] / [[SOURCE_DENYLIST]].

These three safety fields — [[CLAIMS_FORBIDDEN]], [[NON_DISCLOSURE_RULES]], [[REQUIRED_FRAMING]] — **fail closed**: if a relevant field is empty or owner-unconfirmed, the gate blocks and routes to a human.

## 7. Why we do all this (the mission, so judgment stays anchored)

The feed exists to (1) catch attention, (2) teach [[AUDIENCE_PERSONA]] something genuinely useful about their life, and (3) build real interest and trust in [[OFFERINGS]] — in service of [[MISSION]]. Every image is in service of that. Character through quality and cohesion, never through repetition.

## 8. The per-image brief (the brief, not a class skeleton)

Every `[Visual]` brief and every render carries:

```
MESSAGE   — the one thing this post says (1 sentence)
FEELING   — the single emotion a stranger should feel in 1 second
TREATMENT — which approach delivers that feeling, and why (1 line). NOT "which class is next."
IMAGE     — the actual picture: subject, setting, real [[LOCALE]] detail, action/emotion
WORDS     — on-image text if any (designed as the headline; obeys §6)
LIGHT/MOOD— chosen for FEELING, not habit
CHECK     — clears the §4 quality bar? visibly different from the last several posts? no §6 leak? would it stop me?
```

The brief is authored pre-render and confirmed by the Creative Director's **pre-render pass** before any image is generated (§9, §11).

## 9. CD review gates (judgment, not a mechanical checklist)

The Creative Director is the sole quality judge and reviews every piece twice — a **pre-render pass** on the brief and a **post-render pass** on the rendered artifact.

**Pre-render pass (on the §8 brief).** Approve the brief only when all are yes:
- Does it serve *this post's* specific feeling (§2)?
- Will the planned treatment plausibly clear the quality bar (§4)?
- Is it visibly different from the recent feed — no collapse toward one look (§1)?
- Any leak of [[NON_DISCLOSURE_RULES]] mechanics, in planned words or scene (§6)?

**Post-render pass (on the rendered artifact, multimodal).** Approve the image only when all are yes:
- Does it serve *this post's* specific feeling (§2)?
- Does it clear the quality bar — alive, warm, premium, true, scroll-stopping (§4)?
- Is it visibly different from the recent feed — no collapse toward one look (§1)? *(This rendered "visibly different" judgment lives here, not in the linter.)*
- Any leak of [[NON_DISCLOSURE_RULES]] mechanics, in words or scene (§6)?
- Would a stranger actually stop?

Verdicts: `approve / revise(≤2) / reject`; round 3 escalates. The CD **never edits drafts**. If the honest read is "the metaphor isn't legible," "it's pretty but lifeless," or "this is the third near-identical look in a row" — reject and re-decide from §2. **Compliant-but-dead is a reject.**

The **deterministic ledger-linter** (reads the system-of-record ledger) runs **before** the CD pre-render pass and hard-blocks countable-rotation violations over a pinned trailing window (hook/shape/idea-rerun/visual-treatment-label/research-minimum). The linter is what makes "countable rotation violations = 0" true; the rendered "visibly different" call is deliberately *not* in the linter — there is no rigid gender/age/clothing/posture/lighting hard-block (that would fight the variety principle).

## 10. Carousels (multi-slide posts)

A carousel is **one post made of several ordered slides.** Use it when an idea wants steps, a myth→fact flip, or a small lesson that won't fit one frame ("3 signs…", "how an evening winds down").

- **Variety is ACROSS posts, not within a carousel.** The slides of a single carousel deliberately **share one template** — same type system, [[PALETTE_HEX]], margins, frame language — so it reads as one cohesive piece. (Don't make slide 2 look like a different brand from slide 1.) The cover carries the hook; each inner slide carries one beat; the last slide closes (soft CTA / brand).
- **Production reality:** the image provider renders **one image per call**, so a carousel is N separate renders. Hold the shared template fixed across slides and change only the per-slide content. Number slides in order (01, 02, …).
- **Handoff:** upload every slide to the piece's row in the **system of record (Google Sheets + Google Drive)** in slide order; name each file with its slide number so the publisher posts them in sequence. State the slide count + order in the handoff bundle.
- **Cost & safety:** a carousel multiplies image cost by slide count — **declare the slide count up front**, keep within sensible defaults unless the owner asks for more, and every slide still clears the §4 quality bar.

## 11. Craft laws (HARD — they exist so the autonomous engine reproduces board-grade work unattended)

These bind the Visual Production Agent (execution) and the Creative Director (the gate).

**11.1 Advertising polish, never raw.** Prompt for premium ADVERTISING-CAMPAIGN photography appropriate to [[VISUAL_REGISTER]] — cinematic controlled lighting, shallow depth of field, filmic color grade, elevated, magazine-quality. NEVER use "raw / candid / documentary / authentic / not glamorous" as prompt language — those produce cheap footage. Real people, but elevated. Follow [[VOICE_DO]] and avoid [[VOICE_DONT]] in any on-image language.

**11.2 Typography is composited, never baked — and verified text-free.** The image provider renders **NO text**; we composite all type ourselves. The justification is **brand-exactness + determinism** (exact fonts/kerning, the scrim, an OCR-verifiable invariant) — not a claim the model can't render text. Generate the photo **clean** with space reserved, then composite the caption with the brand type tool. A **deterministic Cloud Vision OCR check on the raw pre-composite image** is the **text-free gate**: any baked glyphs → automatic fail → regenerate. (A multimodal OCR is a non-deterministic secondary only.)
  - The brand type **SYSTEM is constant across the whole feed** — only the imagery varies: headline in [[HEADLINE_FONT]], labels/kickers in [[LABEL_FONT]], accent per [[PALETTE_HEX]], wordmark "[[WORDMARK_TEXT]]" with [[LOGO_ASSET]].
  - Light photo → dark text on [[ACCENT_LIGHT_BG]]; dark photo → light text on [[ACCENT_DARK_BG]]. The scrim MUST sit behind EVERY line of text; a scrim that fades before the first line (an unreadable first line) is a reject.
  - **Reserve the clean space in the LOWER band of the frame** (≈ lower 40%) — the compositor places type at the bottom; reserving the top leaves type over busy/bright image and it washes out.
  - A **kicker is a SHORT label only**; a sentence under the headline uses a wrapping sub-line on the scrim — never cram a sentence into the kicker.

**11.3 Concept legibility — a still image must CONVEY its concept.** The picture must carry the idea to a stranger in ~2 seconds, image alone. If the concept needs motion or before/after, a single static pose will NOT read. Use a clear device instead: a two-frame / diptych contrast, a legible metaphor, or a different image. Before generating, the Visual Production Agent states in one line what a stranger would read from the image ALONE; if that doesn't match the intended concept, re-concept. This is a primary CD reject reason.

**11.4 No suggestive imagery.** People are dignified and modestly framed — never sexualized (posture, dress, crop, emphasis). This is not about gender; it's about register: stay inside [[VISUAL_REGISTER]] — warm and respectful, never sexy.

**11.5 Carousels carry the teaching; the outro carries the CTA.** Captions go largely unread — the story lives in the images + type across the slides. Structure: hook → why → real value → (benefit) → a dedicated OUTRO slide with a subtle CTA. CTAs follow [[CTA_STYLE]] and never use [[CTA_FORBIDDEN_PHRASES]]; contact routes via [[CONTACT_WHATSAPP]] / [[CONTACT_INSTAGRAM]]. Single images are hooks only.

## 12. Strategy mode and quality tier

**12.1 Visual strategy ([[VISUAL_STRATEGY]]).**
- **`concept_led`** (default for idea/teaching brands) — there is no product to show; build the single generated image that delivers the §2 feeling.
- **`product_led`** — use a real asset from the offering's product set as the hero, and reserve generation for background/scene (placing the supplied product/logo into a generated scene via the real-asset compositing path). Each offering is identified by [[OFFERING_ID]]; the hero references the named offering ([[OFFERING_NAME]] / [[OFFERING_BRIEF]]).

**12.2 Provider, tier, and upgrades.** Images are produced through a single provider abstraction selected by [[IMAGE_PROVIDER]] (default: the Gemini-native image+edit model — confirm the current marketing name and API ID at build time against live docs; do not hard-code a name). The floor quality tier is [[IMAGE_QUALITY_TIER]]; the Creative Director may call a **premium upgrade** above the floor when the piece warrants it. **No silent model swaps** — a provider error stops and escalates rather than quietly substituting. Every render attaches its prompt, provider, prediction id, and tier to the ledger row.

## 13. Pipeline placement (where this engine sits)

1. Content agent drafts the piece and authors the §8 brief.
2. **Ledger-linter** (deterministic, reads Sheets) hard-blocks countable-rotation violations.
3. **CD pre-render pass** approves/revises the brief (§9).
4. Visual Production Agent generates the **text-free** image(s) per [[VISUAL_STRATEGY]] with the lower band reserved.
5. **Cloud Vision OCR text-free gate** (§11.2) — baked glyphs fail → regenerate.
6. Brand type composited; formatted to channel aspect ratio (per [[CHANNELS]]); asset hosted to Drive; alt text authored.
7. **CD post-render multimodal pass** (§9) on the rendered artifact.
8. Ops ledger audit (row + alt text + clean lint) → handoff bundle → Approval Queue in the system of record. Approval per [[APPROVAL_MODE]]; auto-publish only past [[TRUST_THRESHOLD]]. Fail-closed safety (§6) and deterministic claim-grounding run alongside.

---

*Governs the visual half of the engine: brief → render → composite → gate. The mechanical craft tool (compositing, wordmark, demographic variation when a person is in frame, the provider pipeline) is subordinate to this engine — serve the post's feeling and the quality bar first. Owner: the Creative Director maintains this doc and operates the gates; the Visual Production Agent executes. Approval owner per [[APPROVAL_MODE]]. System of record: Google Sheets + Google Drive.*
