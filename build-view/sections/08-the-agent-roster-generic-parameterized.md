<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §8 (source lines 792–860). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 8. The agent roster (generic, parameterized)

**Eight generic roles, one of which is the onboarding Strategist; the Offering Content Agent runs as one role serving N offerings (brief selected per task).** Names are generic; AOL equivalents shown for traceability. For a brand with N offerings, running instances = 6 fixed roles + 1 Offering Content Agent (N briefs) + 1 Strategist. (The §2.1 "team of 8 agents" describes the existing AOL roster and is unchanged.)

| Role (Agent Atelier) | AOL equivalent | Class / model tier | One-line mandate |
|---|---|---|---|
| **Managing Editor** | CEO | Reasoning (Gemini 3 Pro) | Owns strategy, the weekly editorial rhythm, delegation, the human interface, unblocking. Does **no** IC work. |
| **Research & Verification Agent** | ResearchAgent | Reasoning | Terminal source of facts; maintains the verified Claim Bank; vets testimonials/quotes; enforces source allowlist. |
| **Evergreen Content Agent** | WellnessAgent | Reasoning | The always-on category voice; owns the topical territory between offerings. |
| **Offering Content Agent** (one role, per-offering brief) | HappinessProgramAgent, SahajSamadhiAgent | Reasoning | Owns each offering's spotlight, campaign, in-program, and retention content; selects the Offering Brief per task. |
| **Creative Director** | CreativeDirector | Reasoning (judge) | The sole quality judge. Reviews every piece (pre-render brief **and** post-render artifact) for craft, variety, compliance, truth; returns a verdict. Owns the engine docs. |
| **Visual Production Agent** | VisualsAgent | Operational (Flash) | Produces every image/carousel slide + alt text; runs the image pipeline + caption compositing. |
| **Publishing & Operations Agent** | PublishingCoordinator | Operational (Flash) | Owns the calendar, the ledger linter/audit, the approval-queue handoff, and the weekly visibility digest. |
| **Brand Onboarding Strategist** | (new) | Reasoning | Conducts intake; compiles & maintains the Brand Kit and Offering Briefs. |

### 8.1 Shared agent contract (every agent)

Every agent's instruction file follows the same generic skeleton (the static-context layer of its harness): **Identity & mandate · Canon to load (in order, progressive disclosure) · Procedure · Delegation rules · Hard rules (resolved from Brand Kit) · Heartbeat checklist · Memory.**

**Memory (what durable facts persist).** The durable stores the spec actually grounds:
1. the **Content Ledger** (anti-repetition; append on approval, read first per §10.1);
2. the **Claim Bank** (VERIFIED claims + source + reverify dates);
3. the **corrections log** (owner approvals/edits/rejects → monthly retro, §15.3).

Durable facts live in the **system of record (Sheets/Drive)** as **Sheets-keyed memory** (a `memory` namespace — an umbrella label over the §17 durable stores `LedgerRow` / `ClaimBankEntry` / `Correction`+`ApprovalAction`, **not** a new §17 entity) — this is the durable **cross-run** store; there is **no dependency on Agent Engine Memory Bank** (a documented future upgrade only). Per-offering memory is keyed by `offering_id`. ("What converts" is *not* a default memory fact — engagement is only what the owner shares, and publishing defaults to manual.)

### 8.2 Per-agent specifications (condensed)

**Managing Editor (orchestrator).** Weekly loop: Monday create the editorial-calendar task with slots from `cadence_plan` (incl. the §7.6 language axis), assign each; through the week watch for blocked/stalled work and reprioritize; Friday read the Ops digest and fix misses *this week*; monthly carry the Creative Director's retro changes to the owner. Batches human approvals. **Never writes copy, prompts, or reviews.** Routes on-demand asks same-day.

**Research & Verification Agent.** Maintains a standing **Claim Bank** (status model `PENDING → VERIFIED → RETIRED`). Authorship and verification are **separated** (F34): producing the locked sentence is one step; **flipping to VERIFIED requires an independent grounding gate** —
1. **Automated grounding** via the sanitized `research_fetch`: `source_url` resolves and every numeric figure / named statistic in the locked sentence appears on the fetched page; failure keeps it PENDING.
2. **Independent semantic confirmation**: a second-model verifier (a Gemini call mirroring the §14.2 semantic referee) confirms the locked sentence faithfully represents the source's population/design/finding.
3. **`source_hash`** is stored (§17); on re-verify and a lightweight periodic check the source is re-fetched and compared — changed/missing → RETIRED/PENDING and pulled from shipping.

 When a re-verify / periodic check RETIREs a claim that a **queued or scheduled** piece depends on, the piece is pulled from shipping **and the owner is notified (CRITICAL, §14.4.1)** — a queued piece never disappears silently, and the resulting cadence gap is surfaced, not absorbed. (The recall mechanics are the §10.3 claim-retirement cascade; the owner is notified per §8.2 for any queued/scheduled dependent.)
4. Owner/CD **spot-audit** a small VERIFIED sample (not every entry).
5. If `require_second_source_for_quantitative` is set, quantitative claims need a second corroborating source.

Locked sentences are caption-ready, hedged, source+year named; clinical/sensitive claims carry mandatory framing and are flagged to the owner before first use. Posts a weekly "research drop" *when `research_post_min_per_week > 0`*. **"Cannot verify" is a respected verdict.**

**Evergreen Content Agent.** Owns `evergreen_pillars`; most discovery happens through these posts. Every piece stands alone. When `research_post_min_per_week > 0`, one research-grounded post per week is the credibility anchor. Soft cross-promo to an offering only when organic.

**Offering Content Agent (one role, brief-per-task).** Loads the offering's Brief incl. its `spotlight_angles` (alongside the §9.1 angle lenses and the §9.4 idea-not-rerun rule). Phases — all delivered **through the same feed pipeline** (content-emphasis modes, not separate channels): (0) standing weekly spotlight even with no dates; (1) **campaign ladder** when dates exist (truthful scarcity only); (2) in-program emphasis (intimate, zero promotion); (3) retention emphasis (nudges, never guilt) — honoring `funnels_from` + the Brief's funnel/timing/tone guardrails. Represents the offering **accurately** — never trivialized. Obeys non-disclosure rules.

**Creative Director (the evaluation gate).** Reviews every draft through **Gate 0 (the Scroll Test)** then **Gate 1 (compliance)** — §15. Also runs a **post-render multimodal pass** on the rendered artifact (§10.1, §15.2). Verdicts `approve / revise(≤2) / reject`; round 3 → escalate. **Never edits drafts.** Owns and evolves the Creative & Visual Engines; runs the monthly retro. **Compliant-but-dead is a reject.**

**Visual Production Agent.** Per visual ticket: confirm the brief carries MESSAGE + FEELING + TREATMENT; for `concept_led` brands build the single image that delivers the feeling; for `product_led` brands use a real `products/` image as the hero and reserve generation for background/scene (reusing the Caption-Composer's real-asset compositing). Generate a **text-free** photo with clean space reserved in the lower band; composite the **brand type system**; format per channel aspect ratio; host the asset; **author the alt text** (single owner — §10.1/§17); attach prompt + provider + prediction id + tier. **No silent model swaps** (errors stop and escalate, §14.3). Maintains a prompt-template palette organized by feeling/treatment.

**Publishing & Operations Agent.** Owns the calendar and the **system of record** (Google Sheets/Drive). Runs the **deterministic ledger-linter** (§9.4) and audits before queueing (a piece without its ledger row, alt text, or a clean lint bounces back). Builds the per-piece **handoff bundle** (final caption in correct language, hosted image(s) in order, alt text, channel, first-comment hashtags ready to paste, plus optional `location_tag` / `collaborator_handles`). Posts the **weekly visibility digest** (what shipped, what's queued and for how long, slots hit/missed, research minimum met where applicable, paused routines/pending approvals with links, image spend, **CD↔owner agreement rate**). This digest is *why the engine can never silently stall*.

 **Manual handoff is this agent's responsibility end to end.** Beyond *building* the handoff bundle, Publishing & Ops **materializes it as the channel-aware Post Kit** (§12.3.1 — zero-padded ordered slide files, copy-blocks, per-slide alt text, send-to-phone/QR), **enforces the platform-export limits** (§14.2) before a piece enters the Approval Queue, and **owns mark-as-posted** (§12.3.2) — flipping Approved→Published, recording `posted_permalink`/`posted_at`, and counting the cadence slot **at post time**. An approved piece with no openable Post Kit, an over-limit export, or a piece left Approved-but-unposted past one cadence cycle **bounces or surfaces** exactly as a missing ledger row does.

**Brand Onboarding Strategist.** §7.1. Read/draft/act only; the owner acts; safety fields elicited explicitly.

### 8.3 Agent Skills (Day 3)

Recurring agent workflows are packaged as **Agent Skills** — a filesystem mechanism, **no vector store needed**:

- **`SKILL.md` anatomy:** YAML frontmatter (`name` + a one-line trigger `description`) + Markdown body + optional bundled `scripts/`, `references/`, `assets/`.
- **Three progressive-disclosure levels:** L1 frontmatter always in context; L2 body loads on description match; L3 references/scripts load on demand (scripts execute without polluting the token window).
- **Skills to package (→ triggering agent):** `draft-a-piece` (content agents), `verify-a-claim` (Research), `per-image-brief` + `compose-caption` (Visual), `ledger-lint` + `weekly-digest` + `ledger-append/audit` (Ops), `intake-interview` (Strategist).
- **Knowledge vs Skills (Day 3 line):** engine/canon docs + Claim Bank + voice/detail facts are **Knowledge** (keyed/structured Sheets/Drive access, no semantic index); recurring procedures are **Skills**. Optionally set per-agent static-context token budgets.
- **Skill evals** fold into §15: trigger accuracy + a golden-case per skill.

**Progressive disclosure for *tools*, not only skills (Day 1 "context rot" / Day 2 "RAG for tools").** Apply the same L1→L3 discipline to **MCP tool definitions**, which also consume the window and dilute attention. Each agent's prompt carries **only the tool definitions its role is allowed** — and the Policy Server's per-role `allowed_tools` allowlist (§14.2) is exactly that scoping key, so the registry already exists. Tools outside a role's tier are never placed in its window (the Creative Director never sees `instagram_publish`; content agents never see `claim_bank_write`). This is the Day-1 *context-rot-from-overloaded-prompts* mitigation made concrete and one source of the §6.3/§13.2 token economics.

---

