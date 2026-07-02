# GEMINI.md — Agent Atelier (project DNA + conventions + skills router)

> **Scope.** This is the project-level instruction file for Gemini / Antigravity / ADK working in this
> repository. It is the **static-context spine** every agent and every coding session loads first. It carries
> the project DNA, the engineering conventions, the build posture, the model-version-currency rule, and a
> short **skills catalog/router** into `specs/skills/*`. It is authored source code, not generated output
> (Day-4 principle: instruction/rule files are source code). `AGENTS.md` is the cross-tool mirror of the
> load-bearing rules here; if the two ever disagree, **`GEMINI.md` wins** and `AGENTS.md` must be fixed.
>
> Source of truth for *what to build*: `specs/` (the PRD lives at `specs/PRD-Agentic-Content-Studio.md`).
> This file governs *how* to build it.

---

## 0. Build loop — start here

**Before building anything, read `.agents/rules/build-protocol.md`** (the always-on
build-loop rule). The one rule: **never load the whole PRD while coding.** The PRD is
kept whole at `specs/PRD-Agentic-Content-Studio.md`, but the build is driven with
**progressive disclosure** — per contract, load `build-view/core.md` + that contract's
READ-SCOPE files only. Loading the whole ~2,840-line PRD per phase causes context rot and
degrades quality.

- **The plan is eleven gated contracts, P0 → P6** (§19.1), built **lock-and-proceed**:
  build one, VERIFY against its gate, commit, get owner authorization, then the next.
- **To build the next contract, run `.agents/workflows/build-<id>.md`** — it lists the
  exact files to load, the test-first gate, and the hand-off steps. **`BUILD-STATUS.md`**
  names which contract is next.
- **`build-view/`, `specs/contracts/`, and `.agents/workflows/build-*.md` are DERIVED**
  from the PRD — never hand-edit them; re-run `python3 tools/build_view_split.py` after
  any PRD edit.
- **Switching PCs / resuming mid-contract:** `.agents/workflows/resume.md`.
  **Changing the spec mid-build:** `.agents/workflows/change-request.md`.

---

## 1. What this project is

**Agent Atelier** is a product-agnostic AI content studio: a small company of cooperating agents that plans,
writes, illustrates, quality-reviews, and queues a varied, on-brand stream of social posts (Instagram-first,
channel-extensible) for **any** brand. It is the generalization of a working single-brand engine.

The core promise: **the studio is constant; the brand is configuration.** Every brand-specific fact lives in a
**Brand Kit** (`brands/<brand>/brand_kit.yaml`); the agents, canon docs, pipeline, and governance never change
between brands. Onboarding a new brand is a **configuration** action, not an **engineering** action — the hard
success metric is **zero** brand-specific code/engine-doc changes to onboard a brand.

Mission for the reference brand is `[[MISSION]]`; brand identity strings render from `[[BRAND_NAME]]` /
`[[BRAND_SHORT_NAME]]`, locale `[[LOCALE]]`, languages `[[LANGUAGES]]`, type `[[BRAND_TYPE]]`. **Never hardcode
a brand value in code or canon — emit the registry token and let the resolver fill it** (see §6).

### The ~90% rule (Agent = Model + Harness)

A raw model is not an agent; it becomes one when wrapped in a harness — instruction files, tools (MCP),
sandboxes, orchestration, guardrails/hooks, memory, observability. **~10% of behaviour is the model; ~90% is
the harness.** Almost all of this repo's value is harness: the canon docs, per-agent instructions, the
pipeline, the gates, the budgets. The model underneath (Gemini) is swappable; **invest in the harness.**

---

## 2. The agent company (8 roles)

Six fixed roles + one Offering Content Agent (one role, N per-offering briefs) + the onboarding Strategist.

| Role | Class / tier | One-line mandate |
|---|---|---|
| **Managing Editor** | Reasoning | Owns strategy, the weekly rhythm, delegation, the human interface, unblocking. Does **no** IC work. |
| **Research & Verification** | Reasoning | Terminal source of facts; maintains the VERIFIED Claim Bank; enforces the source allowlist. |
| **Evergreen Content** | Reasoning | The always-on category voice; owns the topical territory `[[EVERGREEN_PILLARS]]`. |
| **Offering Content** (brief-per-task) | Reasoning | Owns each offering's spotlight/campaign/in-program/retention content; selects the Offering Brief per task. |
| **Creative Director** | Reasoning (judge) | The **sole** quality judge (pre-render brief **and** post-render artifact). Owns the engine docs. Never edits drafts. |
| **Visual Production** | Operational | Produces every image/slide + alt text; runs image-gen + caption compositing. **No silent model swaps.** |
| **Publishing & Operations** | Operational | Owns the calendar, the ledger-linter/audit, the queue handoff, the weekly visibility digest. |
| **Brand Onboarding Strategist** | Reasoning | Conducts intake; compiles & maintains the Brand Kit + Offering Briefs. |

Every agent's instruction file (`specs/agents/*.md`) follows one skeleton: **Identity & mandate · Canon to load
(in order, progressive disclosure) · Procedure · Delegation rules · Hard rules (resolved from Brand Kit) ·
Heartbeat checklist · Memory.** Durable memory = the **Content Ledger**, the **Claim Bank**, the **corrections
log** — all in the system of record (Sheets/Drive) by default.

---

## 3. Build posture — Architect mode, NO YOLO

This is non-negotiable and applies to **every** coding session in this repo.

1. **Propose before you generate.** Before writing code, propose the folder structure and the pinned tech
   stack and **wait for confirmation**. Do not scaffold a tree the owner has not seen. No "I'll just build the
   whole thing" runs.
2. **Tests, docs, and logging ship alongside features** — never as a follow-up. Every feature lands with its
   Gherkin-derived tests, its doc note, and structured logging/tracing.
3. **Failing test first, then green.** Write the failing test against the §10.2 Gherkin scenario, then
   implement to pass. Keep tests in the repo. Two tests are mandatory and must exist before any publish path is
   wired: a **ledger-linter test** (a rotation-violating draft is rejected pre-CD) and a **fail-closed safety
   test** (an unconfirmed `[[CLAIMS_FORBIDDEN]]` / `[[NON_DISCLOSURE_RULES]]` / `[[REQUIRED_FRAMING]]` field
   blocks publish).
4. **Show diffs; build component-by-component** against the spec. Match existing conventions. Do not refactor
   adjacent code uncritically.
5. **Security before publish.** The Policy Server, sandboxing, the secrets vault, and the append-only audit
   trail must be wired **before any publish tool is enabled**. Publish is the last thing turned on, not the
   first.
6. **Supply-chain hygiene (guard against hallucinated/slopsquatted packages).** When you propose a dependency,
   **verify it exists on its official registry, then pin it (ideally by hash)** before installing. Wire only
   the first-party / known MCP servers from the integrations table (§5); **never** an untrusted third-party MCP
   server.
7. **The spec is durable; code is disposable.** Regenerate code from `specs/`, never the reverse. If reality
   forces a spec change, change the spec first (with a plain-language "Vibe Diff") and then the code.

---

## 4. Model-version currency rule (read this twice — both directions)

Model and library versions are **deliberately deferred to build time.** Pin every library/model version then,
and **verify the *current* identifiers and limits against live docs before using them — do not trust the
training cutoff.** This cuts both ways:

- **Forward (no stale pins):** confirm the live Gemini / ADK / image-model / Instagram Platform API
  identifiers and limits against live documentation at build time. Treat any model ID, alias, or quota in this
  repo as **"confirm names/IDs at build time."**
- **Inverse (no phantom-404 refusals):** a configured model **may postdate your training cutoff.** You must
  **not** refuse, downgrade, or "correct" a configured model on the belief it does not exist. **Only a live
  provider 404 is acceptable evidence of non-existence.** On any other provider error: capture the **verbatim**
  error, **stop, and escalate** — **never silently fall back** to a different model.

### Current model tokens (confirm names/IDs at build time)

| Use | Token / alias in this repo | Notes |
|---|---|---|
| Reasoning / editorial / judge tier | reasoning tier (e.g. `Gemini 3 Pro`) | Managing Editor, Research, content agents, Creative Director. |
| Operational tier | alias **`gemini-flash-latest`** | Visual Production, Publishing & Ops; mechanical formatting. Confirm the live alias resolves. |
| Optional mechanical tier | Flash-Lite tier | Ledger/digest/formatting-only work. |
| Image generation (default) | **`gemini_image_pro`** (Gemini-native, *Nano Banana Pro*) | The default for `[[IMAGE_PROVIDER]]`. Confirm the exact model ID at build time. |
| Image generation (fallbacks) | Imagen (fallback) · Replicate `gpt-image-*` (optional) | Pluggable; only on explicit Brand Kit selection. |

> The reference brand's `[[IMAGE_PROVIDER]]` may differ from the default; the recommended Google-native swap is
> `gemini_image_pro` / Nano Banana Pro. **The CI evaluation gate pins an explicit judge model ID + rubric
> prompt and runs at temperature 0** — that pin is intentional and separate from the "verify live" rule above.

---

## 5. Tech stack & integrations (versions pinned at build time)

Google Antigravity (sandboxed browser for E2E checks) · Google ADK (multi-agent) · reasoning + operational
model tiers per §4 · Vertex AI Agent Engine (durable Sessions + Memory Bank — **confirm the current product
name and Memory Bank GA/API at build time**) or Cloud Run · MCP servers (below) · Google Sheets + Drive/GCS as
the system of record · the image stack per §4 · Cloud Scheduler. **Confirm all model names/IDs and API limits
against live docs at build time.**

Every external capability is exposed over **MCP** (one integration, every framework). Wire only these:

| MCP tool/server | Purpose | Default impl |
|---|---|---|
| `image_generate` | text-free image generation | `gemini_image_pro` / Imagen / Replicate |
| `caption_compose` | brand typography compositing | Caption-Composer service |
| `drive` | host assets, byte-serving, previews | Google Drive / GCS |
| `sheets` | calendar, ledger, queue, async approval, append-only audit | Google Sheets |
| `research_fetch` | sanitized, allowlist-bound source retrieval + grounding | Search grounding / sanitized fetcher |
| `instagram_publish` | publish to Instagram (the only launch adapter) | Instagram Platform content-publishing API |
| `instagram_caption_edit` / `instagram_delete` | post-publication correct-in-place / take-down of a live piece (§14.3) — owner-authorized, behind the §14.4 checkpoint, **no new publish authority** | Instagram Platform content-publishing API |
| `notify` *(optional; fully contracted — §16.2)* | owner-reaching alerts, digests & escalations (severity-tiered, deduped, rate-capped) | Gmail / Google Chat |
| `calendar` *(optional)* | schedule slots | Google Calendar |
| `handoff_export` | materialize the manual **Post Kit** (§12.3.1) + the deterministic platform-export pre-check — packaging + validation only, **no publish authority** | Drive/GCS folder + Review-app/Studio-Floor view |

The cost circuit-breaker (§7) wraps the **runner**, not a tool.

---

## 6. The Brand Kit + `[[VARIABLE]]` resolver (the only thing that changes between brands)

All brand specifics live in `brands/<brand>/brand_kit.yaml` (+ `assets/people/`, `assets/products/`,
`offerings/`). Code and canon reference brand facts **only** through registry tokens resolved by
`specs/resolver.md`. The registry below is the contract — **emit the token, never the literal value.**

### Token registry (token → Brand Kit field, abbreviated; full table in `specs/resolver.md`)

- **Identity:** `[[BRAND_NAME]]`, `[[BRAND_SHORT_NAME]]`, `[[LOCALE]]`, `[[LANGUAGES]]`, `[[MISSION]]`,
  `[[BRAND_TYPE]]`.
- **Audience:** `[[AUDIENCE_PERSONA]]`, `[[AUDIENCE_PAINS]]`, `[[SCROLL_TEST_PERSONA]]`.
- **Voice:** `[[VOICE_DESCRIPTORS]]`, `[[VOICE_DO]]`, `[[VOICE_DONT]]`, `[[READING_LEVEL]]`,
  `[[SAMPLE_LINES_GOOD]]`, `[[SAMPLE_LINES_BAD]]`.
- **Compliance & safety (fail-closed):** `[[CLAIMS_ALLOWED]]`, `[[CLAIMS_FORBIDDEN]]`,
  `[[NON_DISCLOSURE_RULES]]`, `[[REQUIRED_FRAMING]]`, `[[COMPARATIVE_CLAIMS_ALLOWED]]`,
  `[[POLITICAL_CONTENT_ALLOWED]]`.
- **Research policy:** `[[SOURCE_ALLOWLIST]]`, `[[SOURCE_DENYLIST]]`, `[[CLAIM_REVERIFY_MONTHS]]`,
  `[[REQUIRE_SECOND_SOURCE_FOR_QUANTITATIVE]]`.
- **Territory & offerings:** `[[EVERGREEN_PILLARS]]`, `[[LOCAL_DETAIL_BANK]]`, `[[OFFERINGS]]`,
  `[[OFFERING_NAME]]`, `[[OFFERING_BRIEF]]`, `[[OFFERING_ID]]`.
- **Channels & cadence:** `[[CHANNELS]]`, `[[STANDING_WEEK]]`, `[[POSTS_PER_WEEK_TARGET]]`,
  `[[MAX_POSTS_PER_WEEK]]`, `[[RESEARCH_POST_MIN_PER_WEEK]]`.
- **Contact / CTA (used EXACTLY, never invented):** `[[CONTACT_WHATSAPP]]`, `[[CONTACT_INSTAGRAM]]`,
  `[[CTA_STYLE]]`, `[[CTA_FORBIDDEN_PHRASES]]`.
- **Visual identity:** `[[LOGO_ASSET]]`, `[[WORDMARK_TEXT]]`, `[[PALETTE_HEX]]`, `[[ACCENT_DARK_BG]]`,
  `[[ACCENT_LIGHT_BG]]`, `[[HEADLINE_FONT]]`, `[[LABEL_FONT]]`, `[[VISUAL_REGISTER]]`, `[[VISUAL_VARIETY]]`,
  `[[VISUAL_STRATEGY]]`, `[[IMAGE_PROVIDER]]`, `[[IMAGE_QUALITY_TIER]]`.
- **Publishing & trust:** `[[APPROVAL_MODE]]`, `[[TRUST_THRESHOLD]]`.

### Fail-closed safety (hard)

`[[CLAIMS_FORBIDDEN]]`, `[[NON_DISCLOSURE_RULES]]`, and `[[REQUIRED_FRAMING]]` **must be explicitly
owner-confirmed** to pass schema validation. **Empty / unconfirmed = "unknown" = block publish, route to a
human.** Contact and CTA tokens (`[[CONTACT_WHATSAPP]]`, `[[CONTACT_INSTAGRAM]]`, `[[CTA_STYLE]]`,
`[[CTA_FORBIDDEN_PHRASES]]`) are used **exactly** and **never invented**.

---

## 7. Conventions (the house rules)

- **Spec-driven, hybrid format.** Markdown carries intent; flat YAML (nesting ≤ 3) carries config/schemas;
  **Gherkin** (`Scenario / Given / When / Then`) carries acceptance behaviour. Implement behaviour, not vibes.
- **Default-deny everywhere.** The Policy Server (`specs/policies.yaml`) is a default-deny matrix (8 roles ×
  tools × preview+production). Unlisted combinations are blocked. The read/draft/act ladder is **per
  capability, not per agent.**
- **Determinism where it can be deterministic.** Countable rotation rules and numeric claim grounding are
  enforced by the **deterministic ledger-linter** and the publish-boundary numeric check — not by a model's
  judgment. The CD's holistic verdict is for craft/variety/truth, not for countable rules.
- **State must be observable.** No silent stalls. Trace every run and tool call (session / think / tool
  spans). The **weekly visibility digest** is the anti-silent-stall surface; surface queue depth, stalled
  pieces, slot hits/misses, spend, and the CD↔owner agreement rate.
- **Cost circuit-breaker is mandatory.** A run-level circuit-breaker + per-agent/per-offering budgets wrap the
  runner. (A real incident once burned ~631k tokens in a runaway loop — this is not optional.)
- **Append-only audit.** The audit trail is immutable and separate from the editable queue sheet; it binds
  every external action to the agent and the human who approved it.
- **Human-in-the-loop by default.** `[[APPROVAL_MODE]]` defaults to a human gate (Sheets at MVP; Review app is
  Phase 5). Auto-publish is owner-only opt-in, gated behind `[[TRUST_THRESHOLD]]` + the CD↔owner agreement
  signal, and **never auto-flipped**.
- **Per-piece language.** Language is a per-piece axis from `[[LANGUAGES]]` / `[[STANDING_WEEK]]`, resolved at
  draft time — not a global toggle.
- **No deepfakes.** Real people only from the pre-approved `assets/people/` pool. Images are generated
  **text-free**; typography is **composited, never model-baked**.

---

## 8. Skills catalog / router → `specs/skills/*`

Recurring agent workflows are packaged as **Agent Skills** (filesystem mechanism, **no vector store**). Each
`specs/skills/<name>/SKILL.md` has YAML frontmatter (`name` + a one-line trigger `description`) + a Markdown
body + optional `scripts/` `references/` `assets/`. **Progressive disclosure:** L1 frontmatter always in
context; L2 body loads on description match; L3 references/scripts load on demand (scripts execute without
polluting the token window).

**Router — match the task, load the skill, defer the rest:**

| Skill (`specs/skills/...`) | Triggering agent(s) | Load when the task is… |
|---|---|---|
| `draft-a-piece` | Evergreen / Offering Content | turning a slot/idea into a draft caption + per-image brief |
| `verify-a-claim` | Research & Verification | grounding a claim to a source and flipping PENDING → VERIFIED |
| `per-image-brief` | Visual Production | authoring MESSAGE/FEELING/TREATMENT/IMAGE/WORDS/LIGHT-MOOD/CHECK |
| `compose-caption` | Visual Production | compositing the brand type system onto a text-free image |
| `ledger-lint` | Publishing & Operations | running the deterministic linter before CD review |
| `weekly-digest` | Publishing & Operations | building the Friday visibility digest |
| `ledger-audit` | Publishing & Operations | appending/auditing the Content Ledger |
| `intake-interview` | Brand Onboarding Strategist | conducting the guided intake → Brand Kit |

**Knowledge vs Skills (the Day-3 line):** engine/canon docs + the Claim Bank + voice/detail facts are
**Knowledge** (keyed/structured Sheets/Drive access, no semantic index); recurring procedures are **Skills**.
Skill evals fold into the eval suite: trigger accuracy + one golden case per skill.

---

## 9. Repository map (authored artifacts)

Legend: **[authored]** = hand-edited source · **[derived]** = regenerated by the splitter,
never hand-edited · **[live]** = written during the build.

```
agent-atelier/                     # = git repo root; open THIS folder in Antigravity
  GEMINI.md / AGENTS.md            # [authored] this file + its cross-tool mirror (project DNA)
  README.md                        # [authored] setup, two-PC/GitHub, and resume instructions
  .gitignore                       # [authored] OS / Python / secrets / build-artifact ignores
  BUILD-STATUS.md                  # [live] the phase checklist — which contract is done / next
  WORKLOG.md                       # [live] mid-contract scratchpad (done / remaining / next action)
  .agents/
    rules/build-protocol.md        # [authored] the always-on build LOOP rule (read first)
    workflows/
      build-P0.md … build-P6.md    # [derived] the 11 per-contract /commands
      resume.md                    # [authored] pick up a half-finished contract / switch PCs
      change-request.md            # [authored] change the spec mid-build
  build-view/                      # [derived] progressive-disclosure view of the PRD (do NOT hand-edit)
    core.md                        #   the always-load core (§0 + §3 + §5 + §17)
    00-index.md                    #   the map + per-contract READ-SCOPE → files table
    build-view.manifest.json       #   machine-readable section/contract map
    sections/NN-*.md               #   one file per top-level PRD section
  tools/build_view_split.py        # [authored] the splitter — re-run after any PRD edit
  specs/
    PRD-Agentic-Content-Studio.md  # [authored] the durable source of truth (North Star)
    agents/                        # [authored] 8 generic, [[VARIABLE]]-templated agent prompts
    canon/                         # [authored] creative_engine · visual_engine · research_bank ·
                                   #   content_ledger · cadence_plan · brand_voice · visual_style_guide ·
                                   #   brand_assets · offering_brief.template · channel_style_guides/
    skills/                        # [authored] 8 SKILL.md (see §8 router)
    policies.yaml                  # [authored] default-deny matrix (8 roles × tools × preview+production)
    brand_kit.template.yaml        # [authored] + brand_kit.schema.json (enums, fail-closed flags)
    resolver.md                    # [authored] [[VARIABLE]] registry + resolver pseudocode
    golden_set.md                  # [authored] eval schema + seed exemplars + CI pass threshold
    secrets.md                     # [authored] vault choice, secrets_ref schema, rotation/scoping
    redteam.md                     # [authored] Red/Blue/Green adversarial-vibes suite + escape-log (§15.4)
    agent_cards/                   # [authored] creative-director.json — illustrative A2A card (§13.3)
    schemas/                       # [authored] MCP tool output (§16.1) · notify payload (§16.2) ·
                                   #   conscious-deviation-entry (§18.4.4) JSON schemas
    contracts/P0.md … P6.md        # [derived] the 11 BUNNY prompt-contracts, carved from §19.1
    deviation_log.md               # [live] conscious-deviation log (assumption → ground truth → decision)
  brands/
    <brand>/
      brand_kit.yaml               # [authored] the only thing that changes between products
      offerings/                   # [authored] filled Offering Briefs
      assets/{people,products}/    # [authored] pre-approved image pool
```

> **Layout note (conscious deviation from §18.3 / P0).** Antigravity governance lives in
> `.agents/{rules,workflows}/`; the PRD's `/.agent/skills` reference is superseded — the
> product's Agent Skills are authored at `specs/skills/` (§8 router). The eleven contracts,
> `deviation_log.md`, `build-view/`, and the workflows are **pre-seeded** in this handoff
> (the PRD's P0 lists them as scaffold items — they are done, not deferred). Log any further
> layout ground-truth from Antigravity in `specs/deviation_log.md`.

---

## 10. Definition of done (per change)

- Proposed structure/stack confirmed before scaffolding (no-YOLO, §3).
- Failing Gherkin-derived test written first, now green; ledger-linter + fail-closed safety tests present.
- No brand literal hardcoded — only registry tokens, resolver-filled (§6).
- Default-deny policy entry exists for any new tool/capability; no publish path live without Policy Server +
  sandbox + secrets vault + audit (§3.5, §7).
- New dependencies verified on their official registry and pinned (§3.6).
- Model IDs/aliases treated as "confirm at build time"; no phantom-404 refusal or silent fallback (§4).
- Tracing/logging emitted; observable state updated; digest unaffected or updated.
- Docs updated; the spec changed first if behaviour changed.
```
