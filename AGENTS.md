# AGENTS.md — Agent Atelier (cross-tool conventions)

> **Scope.** `AGENTS.md` is the **cross-tool** instruction file: any coding agent or assistant that does *not*
> read `GEMINI.md` (Codex, Cursor, Claude, a CI bot, etc.) reads this. It mirrors the **load-bearing rules** so
> no tool can miss them. The full project DNA, the agent roster, and the token registry live in **`GEMINI.md`**
> (the canonical project file) and in **`specs/`** (the source of truth for *what* to build).
>
> **Precedence:** if `AGENTS.md` and `GEMINI.md` ever disagree, **`GEMINI.md` wins** — fix this file.
> Instruction/rule files are **source code** (Day-4 principle), not generated output.

---

## 0. Build loop — start here

**Read `.agents/rules/build-protocol.md` before building.** The one rule: **never load
the whole PRD while coding.** The PRD is whole at `specs/PRD-Agentic-Content-Studio.md`,
but the build is driven by **progressive disclosure** — per contract, load
`build-view/core.md` + that contract's READ-SCOPE files only (avoids context rot). The
plan is **eleven gated contracts P0 → P6** (§19.1), lock-and-proceed. For the next one,
run `.agents/workflows/build-<id>.md`; `BUILD-STATUS.md` says which is next. `build-view/`,
`specs/contracts/`, and `.agents/workflows/build-*.md` are **derived** — regenerate with
`python3 tools/build_view_split.py`, never hand-edit. Mid-contract PC switch →
`.agents/workflows/resume.md`; spec change mid-build → `.agents/workflows/change-request.md`.

---

## 1. The one-line project DNA

**Agent Atelier** is a product-agnostic AI content studio — a company of cooperating agents that plans, writes,
illustrates, quality-reviews, and queues a varied, on-brand social feed (Instagram-first) for **any** brand.
The core promise: **the studio is constant; the brand is configuration.** Every brand fact lives in a **Brand
Kit** (`brands/<brand>/brand_kit.yaml`); the agents/canon/pipeline/governance never change between brands.
Mission of the reference brand: `[[MISSION]]` for `[[BRAND_NAME]]` (`[[BRAND_SHORT_NAME]]`), locale
`[[LOCALE]]`, languages `[[LANGUAGES]]`, type `[[BRAND_TYPE]]`. **~90% of value is the harness, not the model.**

Eight roles: Managing Editor · Research & Verification · Evergreen Content · Offering Content (brief-per-task) ·
Creative Director (sole judge) · Visual Production · Publishing & Operations · Brand Onboarding Strategist.
(Full mandates: `GEMINI.md` §2.)

---

## 2. Build posture — Architect mode, NO YOLO (non-negotiable)

1. **Propose folder structure + pinned stack first, and wait for confirmation.** Never scaffold a tree the
   owner has not approved. No "build the whole thing" runs.
2. **Tests, docs, logging ship alongside features** — never as a follow-up.
3. **Failing test first, then green.** Tests stay in the repo. Two are mandatory before any publish path is
   wired: a **ledger-linter test** (a rotation-violating draft is rejected pre-CD) and a **fail-closed safety
   test** (an unconfirmed `[[CLAIMS_FORBIDDEN]]` / `[[NON_DISCLOSURE_RULES]]` / `[[REQUIRED_FRAMING]]` field
   blocks publish).
4. **Build component-by-component against the Gherkin scenarios; show diffs; match conventions.**
5. **Security before publish.** Policy Server + sandboxing + secrets vault + append-only audit wired **before
   any publish tool is enabled.**
6. **Supply-chain hygiene.** Verify each proposed dependency exists on its official registry, then **pin it
   (ideally by hash)** before install. Wire only first-party / known MCP servers (§5); never an untrusted
   third-party MCP server.
7. **Spec is durable; code is disposable.** Regenerate code from `specs/`, never the reverse. Change the spec
   first (with a plain-language "Vibe Diff") when behaviour changes.

---

## 3. Model-version currency rule (both directions)

Model/library versions are **deferred to build time.** Pin them then, and **verify the *current* identifiers
and limits against live docs — do not trust the training cutoff.** Treat every model ID/alias/quota in this
repo as **"confirm names/IDs at build time."**

- **Forward:** confirm the live Gemini / ADK / image-model / Instagram Platform API identifiers + limits.
- **Inverse (no phantom-404 refusals):** a configured model **may postdate your training cutoff.** Do **not**
  refuse, downgrade, or "correct" it on the belief it doesn't exist. **Only a live provider 404 proves
  non-existence.** On any other provider error: capture the **verbatim** error, **stop, and escalate** —
  **never silently fall back** to a different model.

**Current tokens (confirm at build time):** reasoning/judge tier = `Gemini 3 Pro`-class · operational alias =
**`gemini-flash-latest`** · optional mechanical = Flash-Lite tier · **image default = `gemini_image_pro`
(Gemini-native, *Nano Banana Pro*)** for `[[IMAGE_PROVIDER]]`, with Imagen (fallback) / Replicate `gpt-image-*`
(optional). The CI eval gate intentionally **pins** a judge model ID + rubric at **temperature 0** (separate
from the verify-live rule).

---

## 4. House conventions

- **Spec-driven hybrid format:** Markdown = intent; flat YAML (nesting ≤ 3) = config/schemas; **Gherkin** =
  acceptance behaviour. Implement behaviour, not vibes.
- **Default-deny:** `specs/policies.yaml` is a default-deny matrix (8 roles × tools × preview+production);
  unlisted = blocked. The read/draft/act ladder is **per capability, not per agent.**
- **Determinism where possible:** countable rotation rules → the **deterministic ledger-linter**; numeric
  claim grounding → the publish-boundary check. The Creative Director judges craft/variety/truth, not countable
  rules.
- **Observable state, no silent stalls:** trace every run/tool call (session / think / tool spans); the
  **weekly visibility digest** is the anti-silent-stall surface (queue depth, stalls, slot hits/misses, spend,
  CD↔owner agreement rate).
- **Cost circuit-breaker is mandatory:** run-level breaker + per-agent/per-offering budgets wrap the runner.
- **Append-only audit:** immutable, separate from the editable queue sheet; binds every external action to the
  agent + the approving human.
- **Human-in-the-loop by default:** `[[APPROVAL_MODE]]` defaults to a Sheets gate (Review app = Phase 5).
  Auto-publish is owner-only opt-in, gated behind `[[TRUST_THRESHOLD]]`, and **never auto-flipped.**
- **Per-piece language** from `[[LANGUAGES]]` / `[[STANDING_WEEK]]`; resolved at draft time.
- **No deepfakes** (real people only from `assets/people/`); images generated **text-free**, typography
  **composited, never model-baked.**

---

## 5. Integrations (MCP-first; wire only these)

`image_generate` (`gemini_image_pro` / Imagen / Replicate) · `caption_compose` (Caption-Composer) · `drive`
(Drive/GCS) · `sheets` (calendar, ledger, queue, approval, audit) · `research_fetch` (sanitized,
allowlist-bound) · `instagram_publish` (Instagram Platform content-publishing API — the only launch adapter) ·
`instagram_caption_edit` / `instagram_delete` (post-publication correction, §14.3 — owner-authorized, behind the
§14.4 checkpoint, no new publish authority) · `handoff_export` (the §12.3.1 manual Post Kit + export pre-check —
packaging only, no publish authority) · `notify` *(optional; fully contracted, §16.2 — severity-tiered, deduped,
rate-capped)* · `calendar` *(optional)*. The cost circuit-breaker wraps the **runner**, not a tool.

---

## 6. Brand tokens — emit the token, never the literal value

All brand specifics resolve from `brands/<brand>/brand_kit.yaml` via `specs/resolver.md`. **Never hardcode a
brand value.** Registry (full table in `GEMINI.md` §6 / `specs/resolver.md`):

- **Identity/audience:** `[[BRAND_NAME]]` `[[BRAND_SHORT_NAME]]` `[[LOCALE]]` `[[LANGUAGES]]` `[[MISSION]]`
  `[[BRAND_TYPE]]` `[[AUDIENCE_PERSONA]]` `[[AUDIENCE_PAINS]]` `[[SCROLL_TEST_PERSONA]]`.
- **Voice:** `[[VOICE_DESCRIPTORS]]` `[[VOICE_DO]]` `[[VOICE_DONT]]` `[[READING_LEVEL]]`
  `[[SAMPLE_LINES_GOOD]]` `[[SAMPLE_LINES_BAD]]`.
- **Compliance/safety (fail-closed):** `[[CLAIMS_ALLOWED]]` `[[CLAIMS_FORBIDDEN]]` `[[NON_DISCLOSURE_RULES]]`
  `[[REQUIRED_FRAMING]]` `[[COMPARATIVE_CLAIMS_ALLOWED]]` `[[POLITICAL_CONTENT_ALLOWED]]`.
- **Research:** `[[SOURCE_ALLOWLIST]]` `[[SOURCE_DENYLIST]]` `[[CLAIM_REVERIFY_MONTHS]]`
  `[[REQUIRE_SECOND_SOURCE_FOR_QUANTITATIVE]]`.
- **Territory/offerings:** `[[EVERGREEN_PILLARS]]` `[[LOCAL_DETAIL_BANK]]` `[[OFFERINGS]]` `[[OFFERING_NAME]]`
  `[[OFFERING_BRIEF]]` `[[OFFERING_ID]]`.
- **Channels/cadence:** `[[CHANNELS]]` `[[STANDING_WEEK]]` `[[POSTS_PER_WEEK_TARGET]]` `[[MAX_POSTS_PER_WEEK]]`
  `[[RESEARCH_POST_MIN_PER_WEEK]]`.
- **Contact/CTA (used EXACTLY, never invented):** `[[CONTACT_WHATSAPP]]` `[[CONTACT_INSTAGRAM]]`
  `[[CTA_STYLE]]` `[[CTA_FORBIDDEN_PHRASES]]`.
- **Visual:** `[[LOGO_ASSET]]` `[[WORDMARK_TEXT]]` `[[PALETTE_HEX]]` `[[ACCENT_DARK_BG]]` `[[ACCENT_LIGHT_BG]]`
  `[[HEADLINE_FONT]]` `[[LABEL_FONT]]` `[[VISUAL_REGISTER]]` `[[VISUAL_VARIETY]]` `[[VISUAL_STRATEGY]]`
  `[[IMAGE_PROVIDER]]` `[[IMAGE_QUALITY_TIER]]`.
- **Publishing/trust:** `[[APPROVAL_MODE]]` `[[TRUST_THRESHOLD]]`.

**Fail-closed:** `[[CLAIMS_FORBIDDEN]]`, `[[NON_DISCLOSURE_RULES]]`, `[[REQUIRED_FRAMING]]` must be explicitly
owner-confirmed to pass schema validation; **empty/unconfirmed = "unknown" = block publish, route to a human.**

---

## 7. Skills router → `specs/skills/*`

Recurring workflows are **Agent Skills** (filesystem, no vector store; progressive disclosure L1/L2/L3). Match
the task → load one skill → defer the rest:

| Skill (`specs/skills/...`) | Agent | Load when the task is… |
|---|---|---|
| `draft-a-piece` | Evergreen / Offering Content | slot/idea → draft caption + per-image brief |
| `verify-a-claim` | Research & Verification | grounding a claim; PENDING → VERIFIED |
| `per-image-brief` | Visual Production | MESSAGE/FEELING/TREATMENT/IMAGE/WORDS/LIGHT-MOOD/CHECK |
| `compose-caption` | Visual Production | compositing the brand type system onto a text-free image |
| `ledger-lint` | Publishing & Operations | running the deterministic linter before CD review |
| `weekly-digest` | Publishing & Operations | building the Friday visibility digest |
| `ledger-audit` | Publishing & Operations | appending/auditing the Content Ledger |
| `intake-interview` | Brand Onboarding Strategist | guided intake → Brand Kit |

**Knowledge vs Skills:** canon/engine docs + Claim Bank + voice/detail facts = **Knowledge** (keyed Sheets/Drive
access, no semantic index); recurring procedures = **Skills**.

---

## 8. Definition of done (per change)

- Structure/stack confirmed before scaffolding (no-YOLO).
- Failing Gherkin test first, now green; ledger-linter + fail-closed safety tests present.
- No brand literal hardcoded — registry tokens only, resolver-filled.
- Default-deny policy entry exists for any new tool; no publish path live without Policy Server + sandbox +
  secrets vault + audit.
- New deps verified on the official registry and pinned.
- Model IDs treated as "confirm at build time"; no phantom-404 refusal or silent fallback.
- Tracing/logging emitted; spec changed first when behaviour changed.
