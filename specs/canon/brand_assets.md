# Brand Assets & CTA — Canon Template

> **Generic, product-agnostic template (Agent Atelier).** All brand-specific facts are
> `[[VARIABLE]]` placeholders resolved at runtime from the Brand Kit (`brand_kit.yaml`),
> per the context-resolver pattern (PRD §7, §7.2.1). This document is a *template*: the
> generic engine text never changes between brands — only the resolved values, fonts,
> palette, and contact facts do. Do not hand-edit brand values into the body; supply them
> through the Brand Kit and let the resolver substitute.
>
> **Owner agent:** Creative Director · **Operated by:** Visual Production Agent
> (compositing) and the content agents (CTA/outro copy) · **Approver:** the brand owner.
> Seeded from the Brand Kit identity/contact/visual fields (PRD §7.3, §9.6).
>
> **Resolver contract (PRD §7.2.1).** Scalars inline; lists comma-joined or bulleted as
> noted per use site; objects via a defined per-key format; **no raw YAML in prompts**.
> Any unresolved *required* variable **fails closed** — the run is blocked and the gap is
> surfaced to the owner; nothing is drafted or published. **Secrets are never inlined**:
> contact handles here are model-visible brand facts, but any provider/API tokens resolve
> only into the tool/MCP auth layer (PRD §7 intro, §14.6).

---

## 1. Brand identity (OFFICIAL — use exactly; encoded in the Caption-Composer config)

- **Logo:** the official brand logo at `[[LOGO_ASSET]]` (transparent PNG). On every post the
  brandmark = this logo with **`[[WORDMARK_TEXT]]`** in text beneath it, composited by the
  Caption-Composer (PRD §11.2) — the logo asset plus the wordmark line, never re-typeset by
  the image model. On dark photos, if the logo's wordmark text would not read against the
  scrim, it is auto-recoloured to the light/cream accent so it reads; on light photos the
  logo is used as-is.
- **Colours (sampled from / aligned to the official logo):** the accent-rule gradient is
  `[[PALETTE_HEX]]`. The **type accent** (the rule, kicker, and `[[WORDMARK_TEXT]]`) is
  **`[[ACCENT_DARK_BG]]`** on dark slides and **`[[ACCENT_LIGHT_BG]]`** on light slides
  (these are the theme/scrim accents, distinct from `[[PALETTE_HEX]]`, the accent-rule
  gradient — PRD §11.2). The **logo itself stays its official colour** (it is designed to
  read as-is); only the *type* accent — rule, kicker, and wordmark — uses the theme accent.
- **Type:** brand headline serif = `[[HEADLINE_FONT]]` (headlines); small-caps label face =
  `[[LABEL_FONT]]` (kicker / wordmark). These are the constant brand type system composited
  on every post; swap here only if the owner supplies an official brand typeface via the
  Brand Kit.

> The brand type system (serif headline + accent rule + optional kicker + logo + wordmark),
> the fixed `[[PALETTE_HEX]]`, and `[[VISUAL_REGISTER]]` are **constant across the feed** —
> brand cohesion is non-negotiable and applies to every post (PRD §9.2). Variety lives in
> the *message and treatment*, never in the brand identity.

---

## 2. Contact (use EXACTLY; never invent or alter)

Resolved from the Brand Kit; the agents reference these facts verbatim and never fabricate,
abbreviate, or alter them.

- **Action:** `[[CTA_STYLE]]` — the default is a warm, subtle invitation (e.g. invite a DM),
  **never** high-pressure conversion language. See §3.
- **WhatsApp:** `[[CONTACT_WHATSAPP]]`
- **Instagram:** `[[CONTACT_INSTAGRAM]]`
- **No offer the owner has not confirmed.** Do **not** advertise a promotion, free session,
  discount, or date the Brand Kit / a confirmed Offering Brief does not contain. Unknown =
  do not claim it.

---

## 3. CTA discipline & forbidden phrases

- **CTA style:** `[[CTA_STYLE]]`. The call-to-action is subtle, warm, and low-pressure by
  default — one clear soft action, never a stack of asks.
- **Forbidden phrases:** never use `[[CTA_FORBIDDEN_PHRASES]]`. These hard-pressure /
  fake-urgency phrasings are rejected by the Creative Director and must not appear in any
  caption or on-image text.
- **One soft action only.** A piece carries at most one CTA, and only where the format calls
  for it (see the outro pattern, §4). Teaching slides stay clean.
- **Truthful scarcity only.** Any time-bound or limited-availability framing is allowed only
  when it is literally true and confirmed by the owner (PRD §8.2 campaign rules); otherwise
  it falls under the forbidden-phrases rule.

---

## 4. Soft-CTA / outro pattern (carousels)

The **last** slide of a teaching carousel is a dedicated outro: subtle, warm, low-pressure.
It does three jobs — (1) **name the brand** (`[[BRAND_SHORT_NAME]]`, via the logo +
`[[WORDMARK_TEXT]]`), (2) **name the offering** the piece funnels to (`[[OFFERING_NAME]]`),
and (3) **one soft action**. All other slides stay clean; only the outro carries the CTA.

```
line:     "If <the pain in the piece> still <happens> —"
headline: "<the promise, tied to the offering>"
offer:    "[[OFFERING_NAME]]"
action:   "<[[CTA_STYLE]] action> · <resolved from [[CONTACT_WHATSAPP]] / [[CONTACT_INSTAGRAM]]>"
```

- The `action` line is built from the contact facts in §2 and must obey §3 (never a
  forbidden phrase).
- **Offering → CTA mapping.** Which offering a piece funnels to is decided per piece from
  `[[OFFERINGS]]` (each with its `[[OFFERING_ID]]` / `[[OFFERING_NAME]]` / `[[OFFERING_BRIEF]]`).
  General/category (evergreen) pieces funnel to the offering the piece leans toward, honoring
  any `funnels_from` relationship in the relevant Offering Brief; credibility/research pieces
  build trust in the brand broadly and point the CTA where the piece leans. Keep cross-promo
  soft and organic — timing/tone guardrails live in the Offering Brief prose, not as global
  numeric rules (PRD §7.4, §8.2).

---

## 5. Represent offerings accurately — never trivialize

Copy must reflect what each offering genuinely delivers. Reducing an offering to a single
trick or gimmick is a **misrepresentation**: it makes a reader think "I already do that — so
what?" and it undersells the offer.

- Draw the accurate description, audience, outcomes (with any `[[REQUIRED_FRAMING]]` hedges),
  and what-not-to-claim from the relevant **Offering Brief** (`[[OFFERING_BRIEF]]`, dynamic
  context selected per task by `[[OFFERING_ID]]` — PRD §7.4). Convey the real depth and the
  experiential nature of the offering; never collapse it to one catchphrase.
- Obey `[[NON_DISCLOSURE_RULES]]`: never reveal a proprietary mechanism the brand keeps
  undisclosed — in the **words on the image** or the **scene depicted** (enforced by the
  Creative Director's post-render multimodal pass, PRD §9.2, §15.2). These fields **fail
  closed**: if a relevant safety field is empty or owner-unconfirmed, the piece is blocked
  and routed to a human, never treated as "nothing forbidden" (PRD §14.2, §15.1).

**Two hard copy rules for any offering line:**
1. Never undersell or trivialize an offering, and never imply it is just one small technique.
2. No ambiguous or "clever" lines that say nothing. Every line must mean **one clear thing**
   to a stranger on first read (the `[[SCROLL_TEST_PERSONA]]` two-second scroll test). A line
   that is both ambiguous and a misrepresentation fails on both counts.

---

## 6. Resolution checklist (build-time)

Before this canon is live for a brand, confirm every token below resolves from the Brand Kit
(else the run fails closed, PRD §7.2.1):

- Identity: `[[LOGO_ASSET]]`, `[[WORDMARK_TEXT]]`, `[[BRAND_SHORT_NAME]]`
- Colour: `[[PALETTE_HEX]]`, `[[ACCENT_DARK_BG]]`, `[[ACCENT_LIGHT_BG]]`
- Type: `[[HEADLINE_FONT]]`, `[[LABEL_FONT]]`
- Register: `[[VISUAL_REGISTER]]`
- Contact: `[[CONTACT_WHATSAPP]]`, `[[CONTACT_INSTAGRAM]]`
- CTA: `[[CTA_STYLE]]`, `[[CTA_FORBIDDEN_PHRASES]]`
- Offerings: `[[OFFERINGS]]` (`[[OFFERING_ID]]`, `[[OFFERING_NAME]]`, `[[OFFERING_BRIEF]]`)
- Safety (fail-closed): `[[NON_DISCLOSURE_RULES]]`, `[[REQUIRED_FRAMING]]`
- Scroll test: `[[SCROLL_TEST_PERSONA]]`
