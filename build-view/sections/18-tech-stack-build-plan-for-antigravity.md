<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §18 (source lines 2266–2354). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 18. Tech stack & build plan for Antigravity

This is **one** plan. §18 is the stack + the build *workflow* + the build *governance harness*; §19 is the at-a-glance phase map whose underside (§19.1) is the same plan expressed as eleven gated **prompt-contracts**. The build runs under the **§18.4 build-governance harness** with **lock-and-proceed** discipline — every unit *runs and VERIFIES* against its gate before the next begins — and `/specs` (this PRD + the Appendix-D authored artifacts) is the durable source of truth; code regenerates from it. The complete Agent Atelier — **P0 through P6** — is the build target, built in sequence (§21).

### 18.1 Recommended stack (versions pinned at build time against live docs)

Google Antigravity (sandboxed browser for E2E checks) · Google ADK (multi-agent) · reasoning tier **Gemini 3 Pro** (editorial/judge) + operational tier via the **`gemini-flash-latest`** alias (+ an optional **Flash-Lite** tier for purely mechanical formatting/ledger/digest work) · Vertex AI Agent Engine (durable Sessions; confirm the current product name, e.g. a possible "Gemini Enterprise" umbrella, at build time) or Cloud Run — **durable cross-run memory is Sheets-keyed (no Memory Bank dependency; Memory Bank is a future upgrade)** · MCP servers (§16) · Google Sheets + Drive/GCS (SoR) · **Nano Banana Pro** (Gemini-native image, default; token `gemini_image_pro`) / Imagen (fallback) / Replicate `gpt-image-*` (optional) · Cloud Scheduler. **Confirm all model names/IDs and API limits against live docs at build time (§0, §14.3) — do not trust the training cutoff.**

### 18.2 Spec-driven build workflow (runs once per prompt-contract)

The loop below is applied to **every** prompt-contract in §19.1 — the contract is the unit of work, this is the cycle it goes through:

1. **Project Generation (Architect, no YOLO):** propose folder structure + pinned stack for confirmation; scaffold `/specs`, `/.agent/skills`, `GEMINI.md`/`AGENTS.md`, tests, logging.
2. **Feature Generation (Builder):** implement component-by-component against the Gherkin scenarios; match conventions; show diffs.
3. **AI-generated test coverage (test-first):** failing test first, then implement to green; keep tests in the repo. Include a **ledger-linter test** (a rotation-violating draft is rejected pre-CD) and a **fail-closed safety test**. The phase's ACCEPTANCE Gherkin (§10.2/§10.3) is authored as its suite *before* the code, and the **phase gate = that suite green + the step-4 eval gate** (§18.4.3, tests-first per phase) — added to a growing regression suite every later phase keeps green.
4. **Evaluation gate in CI (deterministic):** pin the judge model version + rubric prompt, run at **temperature 0**, and decide pass/fail on (a) the automated checks of §15.2 plus (b) the golden-set score crossing a documented threshold with a small tolerance. The holistic CD craft verdict is **advisory in CI**, not a hard gate (the live runtime CD review stays holistic, §15.1).
5. **Security:** wire the Policy Server, sandboxing, secrets vault, audit trail before enabling any publish tool. **Supply-chain hygiene:** when the implementing agent proposes dependencies, verify each package exists on its official registry before installing and pin it (ideally by hash) — a guard against hallucinated/slopsquatted packages — and wire only the first-party/known MCP servers from §16, never untrusted third-party MCP servers.
6. **Continuous review:** a code-review skill/agent (Tier-2 hybrid: GitHub Action → Antigravity CLI) on every change.

### 18.3 Where instructions live (Day 5)

- **`/specs`** — this PRD + component specs + canon templates + the **prompt-contracts** (`/specs/contracts/`) and the **conscious-deviation log** (`/specs/deviation_log.md`) — the durable source of truth.
- **`/.agent/skills/*/SKILL.md`** — reusable agent workflows (§8.3, progressive disclosure).
- **`GEMINI.md` (canonical project DNA) / `AGENTS.md` (alias).** `GEMINI.md` is the single source of project DNA + cross-tool conventions + the skills catalog/router; **`AGENTS.md` is a generated alias pointing to it — on any conflict `GEMINI.md` wins** (one canon, no drift). The router scopes each of the eight §8.3 skills to **explicit owning agent(s)** so their L1 description-match triggers cannot collide: `draft-a-piece`→content agents · `verify-a-claim`→Research · `per-image-brief`+`compose-caption`→Visual · `ledger-lint`+`weekly-digest`+`ledger-audit`→Ops · `intake-interview`→Strategist — an agent only ever matches skills in its own scope.
- **Brand Kits** — `/brands/<brand>/brand_kit.yaml` + `assets/` (`people/`, `products/`) — the only thing that changes between products.

### 18.4 Build-governance: the prompt-contract harness (the BUNNY method)

§0 states the *posture* — Architect mode, no-YOLO, `/specs` as the durable root, code as disposable. This subsection is the *machinery* that makes that posture executable and auditable. The complete Agent Atelier (P0–P6, §19) is built under a **spec-first, contract-governed harness**: every build unit is a **prompt-contract**, each contract is **built and VERIFIED before the next begins** (lock-and-proceed), and every departure from the spec is **logged as a conscious deviation**. The PRD is the source of truth — code regenerates from it; the contracts *govern* the build, they do not replace the spec.

> This harness is itself a capstone differentiator (Appendix B, Day-5): most submissions are a notebook that ran once; this one is built the way a production agent fleet should be — and the claims in the writeup (§21) are grounded in code that runs, not in description.

#### 18.4.1 The prompt-contract — the unit of work (10 fields)

Each build unit (one phase, or one slice of a phase) is specified as a **ten-field prompt-contract** before any code is generated. The §18.2 workflow (Architect → Builder → test → eval gate → security → review) runs **once per contract**. The ten fields:

1. **INTENT** — the one-sentence purpose of this unit (what capability comes alive).
2. **SCOPE** — exactly what is built in this unit (components, tools, files).
3. **NON-GOALS** — what is explicitly deferred to a later phase (the anti-scope-creep boundary).
4. **INPUTS** — the artifacts this unit consumes (prior phases, the PRD section, the stack).
5. **INVARIANTS** — the rules that must hold throughout (separation of concerns, fail-closed safety, idempotency, secrets-never-in-prompts).
6. **ACTION** — the concrete build steps, in order.
7. **ACCEPTANCE** — the gate: bound to the matching **§19 exit criterion** (the contracts were authored from §19, so ACCEPTANCE and the roadmap are the same line).
8. **VERIFY** — how the gate is *proven* (run the piece, fire the negative test, capture the run) — evidence, not assertion.
9. **AUTHORIZATION** — the owner authorizes the next contract (the authorizer is a separate role from the builder; see §18.4.2).
10. **ON-FAIL** — the predefined fallback when the tool's ground truth differs from the assumption (see §18.4.4).

Each contract may additionally carry a non-numbered **READ-SCOPE** preamble (build-navigation only — which §§ to read vs park for that phase; **not** an 11th field), as used throughout §19.1. **Authorizing a phase** (e.g. P0 → "authorize P1") means releasing that phase's **first sub-contract** (P1 = P1-A; P2 = P2-A; P4 = P4-A; P5 = P5-A); intra-split hops name the exact sub-contract.

The eleven contracts for this build are **P0, P1-A, P1-B, P2-A, P2-B, P3, P4-A, P4-B, P5-A, P5-B, P6** (§19.1). They are authored alongside the PRD in `/specs/contracts/` (Appendix D) — durable inputs, not regenerated output.

#### 18.4.2 Separation of roles — validator / executor / authorizer

Three roles are kept distinct on every contract, so no single actor both does the work and certifies it:

- **Executor** — Antigravity (Gemini 3 + ADK), Architect mode / no-YOLO. Generates the code/tests/docs/logging for the contract's SCOPE and ACTION.
- **Validator** — reviews the executor's output **against the PRD and the contract's ACCEPTANCE/VERIFY** before anything proceeds. The validator checks the *codebase*, not the executor's description of it (§18.4.5, report-is-not-the-repo).
- **Authorizer** — the owner, who signs off the AUTHORIZATION field and releases the next contract. High-stakes flips (enabling auto-publish, canon/schema changes) additionally require the §14.4 Vibe-Diff.

This mirrors, at build time, the same separation the *running system* enforces: the Managing Editor delegates but does no IC work; the Creative Director judges but never edits drafts; the Policy Server gates but is not the agent it gates.

#### 18.4.3 Lock-and-proceed / verify-before-next

Each contract is **locked** before the next opens: its VERIFY evidence must exist (a captured run, a passing negative test, a green CI eval gate) and its AUTHORIZATION must be signed. Phase boundaries are real — the temptation to add "just the Policy Server stub" during P1 is exactly how boundaries blur. Build the phase you are in, verify it, *then* proceed. Gates are quality checkpoints, **not** stopping lines: the full PRD scope (P0–P6) is the build target, locked-and-proceeded end to end.

**Tests-first, per phase — the phase gate is a green test suite, not a judgment call.** Each contract's **ACCEPTANCE** — its matching §19 exit criterion *plus* the phase's Gherkin scenarios (§10.2/§10.3 and the contract's own VERIFY step) — is authored as that phase's **executable test suite *before* the phase's code is generated** (§18.2 step 3, failing-test-first: red → green). The phase **GATE** is then deterministic and mechanical: **the phase's test suite is green AND the CI evaluation gate (§18.2 step 4) passes** — only then does the authorizer (§18.4.2) release the next contract. Each phase **adds its tests to a growing regression suite** every later phase must keep green, so no phase silently breaks an earlier one (P4 governance cannot regress the P1 pipeline). The **hard** gate is the *deterministic* tests + the golden-set threshold; the holistic CD / LLM-judge craft verdict stays **advisory in CI** (§15.1) so a time-boxed build is never blocked by a soft signal. This is Day-4 evaluation + Day-5 spec-driven, test-first development made a **build rule, not a suggestion** — and it is what lets the writeup (§21) claim "built under a governed harness" truthfully.

#### 18.4.4 Conscious-deviation logging + ON-FAIL fallbacks

The implementing agent will hit places where the tool's actual layout/convention differs from the contract's assumption (ADK sub-agent I/O, Antigravity project layout, MCP↔ADK wiring, Instagram API prerequisites). The discipline:

- **Conform to ground truth, then log the deviation.** When reality differs from the assumption, conform to the *tool's* actual behaviour (not the assumed shape) **and record it** in `/specs/deviation_log.md`: the assumption, the ground truth found, the decision taken, and why. Deviations are part of the audit surface (§14.5); they are conscious and visible, never silent.
- **Every contract carries a predefined ON-FAIL fallback** (field 10) so failure has a planned, conformant path rather than an improvised one. The standing fallbacks for this build:
  - **Don't fake MCP.** If MCP↔ADK wiring is harder than the codelab suggested, fall back to the *simplest conformant MCP server the docs support* — **never** a faked inline function that pretends to be a tool. The protocol is the concept (§16); a genuine, conformant MCP server is the floor.
  - **Conform to ADK/Antigravity, don't force the assumed shape.** If sub-agent I/O or project layout differs, adopt the framework's convention.
  - **Keep the falsifiable gate when the soft one is flaky.** If the publish-time semantic referee is costly/flaky, keep the *deterministic* gates (claim-grounding, fail-closed safety, the ledger-linter — the falsifiable ones) and treat the referee as the secondary catch the PRD already frames it as (§14.2).
  - **Poll-based is the documented default.** If event-wake is hard, poll-based task-graph advancement is the default (§13.2); Firestore/Pub-Sub are the flagged upgrade layered on *after* the default is verified.
  - **Manual handoff is the unaffected default.** If an external publish prerequisite is blocked, the frictionless manual handoff (§12.3) is the path that still works.

#### 18.4.5 Grounding disciplines (baked into every contract)

- **Report-is-not-the-repo.** Verification is against the running codebase, not against the executor's summary of it. A passing description is not a passing test; the VERIFY field demands captured evidence (§14.5 audit).
- **Fail-closed.** The three safety fields (`claims_forbidden` / `non_disclosure_rules` / `required_framing`) block when empty/unconfirmed (§14.2); a build unit that cannot prove a safety invariant does not ship that capability.
- **Honest refusal over silent fallback.** On any provider error other than a live 404, capture the verbatim error, stop, and escalate — never silently downgrade a model or a capability (§14.3). Only a live 404 proves a model absent.
- **Verify against live docs at build time.** Pin every model ID / library version / API limit (Gemini, ADK, MCP, Nano Banana/Imagen, Instagram Graph API) against live docs when the contract runs (§0, §14.3, §18.1) — training/codelab knowledge may be stale.
- **Supply-chain hygiene.** Verify each proposed dependency exists on its official registry and pin it (ideally by hash) before installing; wire only first-party/known MCP servers from §16, never untrusted third-party MCP (§18.2 step 5).

---

