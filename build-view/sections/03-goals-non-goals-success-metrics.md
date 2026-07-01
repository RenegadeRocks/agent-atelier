<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §3 (source lines 68–113). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 3. Goals, non-goals, success metrics

### 3.1 Goals

- **G1 — Product-agnostic.** Stand up a fully working content studio for a brand-new product by supplying only a Brand Kit, with **zero changes to agent code or engine docs**.
- **G2 — Faithful reproduction.** Reproduce the AOL engine's agent roster, pipeline, craft rules, and governance — generalized, not weakened.
- **G3 — Intuitive onboarding.** Capture a brand through a guided, conversational intake (not a dead form) that a non-technical owner can complete, producing a valid Brand Kit.
- **G4 — Human-in-the-loop by default, autonomous-capable.** Default to a human approval gate; allow per-brand opt-in to auto-publish once trusted.
- **G5 — Google-native, simple.** Prefer Google tools (Gemini, Nano Banana / Imagen, Drive, Sheets, ADK, Agent Engine) and keep the stack as simple as the job allows; pluggable where a non-Google option is genuinely better (e.g., Replicate image models).
- **G6 — Governed & evaluated.** Every shipped piece passes safety/compliance gating and an automated quality evaluation before reaching a human.

### 3.2 Non-goals (YAGNI)

- Not rebuilding Paperclip's full multi-company SaaS control plane. Agent Atelier needs a *minimal* orchestration layer, not a generic agent-business platform.
- Not building a general social-media scheduler/analytics suite. Publishing is a thin, optional last step.
- Not auto-running paid ad campaigns or handling payments/commerce (this also rules out Instagram Shopping product tags).
- Not multi-language NLG research; channel/locale language is a Brand Kit field, not an R&D problem.
- Not a public marketplace of agents. Single-owner, possibly multi-brand, deployment.
- **Static assets only (v1).** The studio produces single images, carousels, and static 9:16 covers via the Caption-Composer; it **writes Reel scripts** (§9.1) but does **not** generate motion video, and does **not** produce interactive Stories (polls/stickers/link stickers). This is a known reach/discovery ceiling. Image-to-motion/b-roll Reels and interactive Stories are explicit out-of-scope (future) items — cross-referenced from §9.2 and §11.
- **No participant/cohort messaging.** Private/cohort messaging (WhatsApp/Telegram broadcasts, email/LMS sequences) is out of scope. Where an offering has "in-program" or "retention" phases (§8.2), these are content-emphasis/timing **modes delivered through the same feed pipeline**, not a separate delivery system or channel type.

### 3.3 Success metrics

Two kinds of targets: **hard `=0`** only where a deterministic structural check makes it observable, and **measured escape rates with confidence intervals** where the only honest measurement is an independent audit (because a `=0` "escapes" claim measured by the same gate that produced the content is unfalsifiable — see §15.3 for the independent post-publication audit that produces these numbers).

| Metric | Target |
|---|---|
| Time to first on-brand draft for a new brand | < 1 hour from completed intake |
| Brand-specific **code/engine-doc** changes to onboard a new brand | 0 (hard; structural) |
| Posts shipped to the approval queue per week, at quality bar | meets the brand's configured cadence |
| Countable rotation-rule violations reaching a human (all linter-checked rules: hook, shape, aphorism 1-in-5 cap, idea-rerun, visual-treatment-label, research-min) | 0 (hard; enforced by the deterministic ledger-linter, §9.4) |
| "Repetition reaching a human" — semantic/visual sameness | measured escape rate (north-star 0), via §15.3 audit |
| Factually unverifiable claims published | measured escape rate **< 2%** (95% CI), north-star 0; deterministic claim-grounding (§14.2) makes numeric overclaims structurally `=0` |
| Safety / non-disclosure violations published | measured escape rate **< 1%** (95% CI), north-star 0 |
| Runaway-cost incidents (circuit-breaker fired but loop not contained) | 0 (hard; structural) |
| **Creative-Director ↔ owner agreement rate** (judge calibration) | tracked; false-approve rate (CD-approved → owner-edited/rejected) trending down. Computed in §15.3, surfaced in the Friday digest (§14.5) and monthly retro; **this is the explicit trust signal gating `auto_after_trust → auto`** (§12.3) |
| Owner edits per approved piece | trending down quarterly (directional, not an SLA; baseline = current AOL system's first weeks). Optional one-word edit tag (cosmetic / substantive / rejection) on the Review row |

| **Approved pieces that actually reach Published** (manual path) | tracked; approved-but-unposted **aging** surfaced in the Friday digest (§8.2) and the §12.4 tray; north-star: no piece stranded > one cadence cycle |
| **Approve → posted latency** (manual) | tracked, directional — the last-mile of "can the owner actually post" |
| Cadence slot counted as hit | only at **post time** (mark-as-posted, §12.3.2), never at approval |
| **Time-to-owner for a CRITICAL alert** (breaker / fail-closed / adapter-down / no-heartbeat) | reaches the owner within one tick + one send attempt; **0 CRITICAL conditions undetected beyond the dead-man's-switch grace window** (hard; structural, §14.4.1/§14.5) |
| **Out-of-band sends per owner-day** | within the configured rate cap; trending toward the batched ideal (approval-fatigue guard) |

---

