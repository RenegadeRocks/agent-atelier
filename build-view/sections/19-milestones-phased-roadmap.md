<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §19 (source lines 2355–2566). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 19. Milestones / phased roadmap

The table is the map; §19.1 is the executable underside (the eleven prompt-contracts, gated). Phase 1 is split into **P1-A** (the agents in role) and **P1-B** (the pipeline + MCP tools made real) because P1-B is the load-bearing "MCP becomes real" unit; **Phase 2** into **P2-A** (schema + resolver) and **P2-B** (Strategist + first-light); and **Phases 4 and 5** likewise each into two gated contracts (**P4-A/P4-B**, **P5-A/P5-B**) so the two densest units are right-sized and the scope-cut line falls on a clean boundary (§19.2). Four phases split → the eleven contracts.

| Phase | Time-box | Deliverable | Exit criteria (= the contract ACCEPTANCE/gate) |
|---|---|---|---|
| **0. Spec & scaffold** | ~30–45m | Spec confirmed; repo, `/specs`, `GEMINI.md`, tool stubs | Architect plan approved; CI green on stubs |
| **1. Single-brand end-to-end build** | ~3–5h | P1-A six core agents (ME + Evergreen + Research + CD + Visual + Ops); P1-B pipeline state machine + `sheets`/`caption_compose`/`image_generate`/`drive` MCP tools; idea→lint→review→render→**Sheets queue→approve**; Caption-Composer | One on-brand piece passes both gates and the ledger-linter and lands in the **Sheets** queue for a hard-coded test brand (no Review app yet) |
| **2. Brand Kit + onboarding** | ~3–4h | P2-A Brand Kit schema + `[[VARIABLE]]` resolver; P2-B Strategist interview (safety fields elicited) + first-light | New brand onboarded by interview with **zero code changes**; produces a piece |
| **3. Full roster + cadence** | ~4–6h | Offering Content Agent (briefs as data); standing-week scheduler; **deterministic ledger-linter**; weekly digest | A full week auto-plans/drafts/reviews/queues; a rotation-violating draft is rejected pre-CD |
| **4. Governance & eval** (P4-A/P4-B) | ~5–7h | Policy Server (structural + claim-grounding + fail-closed; publish-time semantic); append-only audit; run-level circuit-breaker; CI eval gate | **P4-A:** safety/claim scenarios pass; circuit-breaker fires in test; CI eval gate blocks a golden-set regression. **P4-B:** a publish-time referee catches a smuggled-CTA/tone near-miss (§19.1) |
| **5. Approval UI + publishing** (P5-A/P5-B) | ~4–6h | Review app + **Studio Floor UI (§12.4)**; manual publish handoff; adapter-aware auto-publish (byte-serving + first-comment + carousel cap + idempotency) | **P5-A:** owner approves via Sheets and the app; manual publish works; auto-publish gated, idempotent & audited. **P5-B:** Studio-Floor scenarios pass — live handoff/loop visible, intervention audited (§19.1) |
| **6. Improvement loop** | ~4–6h | Corrections mining; monthly retro tuning; post-publication audit; multi-brand | Escape-rate audit reports CIs; CD↔owner calibration tracked; a second brand runs alongside the first |

### 19.1 The gated P0–P6 sequence (the eleven prompt-contracts)

Each contract is one instance of the §18.4 ten-field template. **Build + VERIFY before the next** (lock-and-proceed). Executor: Antigravity (Gemini 3 + ADK), Architect/no-YOLO. Validator: review each against the PRD before moving on. The PRD is the source of truth; these contracts govern the build, they do not replace it.

#### PHASE 0 — Spec & scaffold `[~30–45m]`

**CONTRACT P0 — Repo, /specs, GEMINI.md, tool stubs**
**READ-SCOPE** (build-navigation, not a 10-field entry): read §18 (build workflow + governance), §16 (MCP contracts), Appendix D (file map). Park §7–§15 — later phases.
1. **INTENT** — Stand up the SDD skeleton so the PRD is the regenerable root and agents have a home.
2. **SCOPE** — Repo; `/specs` (this PRD + the Appendix-D authored artifacts: agent templates, canon docs, `policies.yaml`, `brand_kit.schema.json`, `resolver.md`, `golden_set.md`, `secrets.md`, `/specs/contracts/`, `/specs/deviation_log.md`); `/.agent/skills`; `GEMINI.md`/`AGENTS.md` (project DNA + skills router); MCP tool **stubs** (§16); CI green on stubs.
3. **NON-GOALS** — No agent logic, no real tools, no Brand Kit resolution yet.
4. **INPUTS** — The PRD; ADK; Antigravity.
5. **INVARIANTS** — Folder structure approved by owner before scaffolding (no-YOLO). `/specs` is the source of truth. Secrets via vault reference only (§14.6) from day one.
6. **ACTION** — Propose structure → on approval, scaffold; commit the PRD + authored artifacts; stub the MCP tools; wire CI.
7. **ACCEPTANCE** — §19 P0 exit: *Architect plan approved; CI green on stubs.*
8. **VERIFY** — CI passes on stubs; `/specs` + `/.agent/skills` present; GEMINI.md routes to the skills catalog.
9. **AUTHORIZATION** — Owner authorizes P1.
10. **ON-FAIL** — If Antigravity/ADK project layout differs from assumption, conform to the tool's actual layout (ground truth) and log the deviation.

→ **GATE:** CI green on stubs; structure approved. Authorize P1.

#### PHASE 1 — Single-brand end-to-end build `[~3–5h, split into two gated contracts]`

**CONTRACT P1-A — The six core agents (hard-coded test brand)**
**READ-SCOPE** (build-navigation, not a 10-field entry): read §8 (roster + agent instruction files), §9.1–§9.4 (engine docs + linter), §10.1 (pipeline). Park §7 (Brand Kit), §12.4, §14 — later phases.
1. **INTENT** — Bring up the §8 roster minus the Strategist/Offering agents, for ONE hard-coded brand, so a piece can flow end-to-end. The multi-agent-system concept (ADK) made real.
2. **SCOPE** — ADK agents: **Managing Editor** (orchestrator), **Evergreen Content**, **Research & Verification**, **Creative Director** (judge), **Visual Production**, **Publishing & Operations**. In-process handoffs (§13.3 default). Each agent's §8.1 instruction file (Identity/Canon/Procedure/Delegation/Hard-rules/Heartbeat/Memory). Brand facts hard-coded for now (Brand Kit comes P2).
3. **NON-GOALS** — No Brand Kit/resolver (P2). No Offering agent (P3). No Policy Server/auto-publish (P4). No Review app (P5). Instagram publish NOT wired (manual/Sheets only).
4. **INPUTS** — P0 scaffold; the canon/engine docs (§9) as `/specs/canon`; Gemini via ADK.
5. **INVARIANTS** — Managing Editor does **no IC work** (delegates only). CD **never edits** drafts (verdicts only). Separation of concerns mirrors the PRD roles exactly.
6. **ACTION** — Build the six agents + their instruction files; wire ME→content→CD→Visual→Ops handoffs.
7. **ACCEPTANCE** — A test idea flows PLAN→DRAFT→(lint stub)→REVIEW→VISUALIZE→QUEUE for the hard-coded brand; agents coordinate in order.
8. **VERIFY** — Run one piece through; confirm each agent acts in role; capture the run (the "real multi-agent system" moment).
9. **AUTHORIZATION** — Owner authorizes P1-B.
10. **ON-FAIL** — If ADK sub-agent I/O differs from assumption, conform to ADK's convention; don't force the assumed hand-off shape.

→ **GATE:** one idea flows through all six agents in role. Authorize P1-B.

**CONTRACT P1-B — The pipeline state machine + Sheets gate + Caption-Composer**
**READ-SCOPE** (build-navigation, not a 10-field entry): read §10.1 (pipeline), §11.2 (Caption-Composer), §12.2 (Sheets integrity), §16.1 (MCP contracts). Park §7, §12.4, §14 — later phases.
1. **INTENT** — Make the §10.1 pipeline real end-to-end and land a piece in the Sheets approval queue, with brand typography composited.
2. **SCOPE** — The state machine (PLAN→…→RECORD); the **`sheets` MCP tool** (calendar/queue/ledger/append-only audit — §12.2 integrity: queue sheet ≠ audit trail; orchestrator sole writer of derived status; publish-once guard keyed by `piece_id`); the **`caption_compose` MCP tool** (text-free image in, OCR check, composite brand type system, scrim, channel aspect ratio ≥1080px short edge — §11.2); the **`image_generate`** + **`drive`** MCP tools (text-free generation; host asset).
3. **NON-GOALS** — No claim-grounding/semantic gate yet (P4 — Research returns VERIFIED stubs). No auto-publish.
4. **INPUTS** — P1-A agents; the MCP tool stubs from P0 (now implemented).
5. **INVARIANTS** — Image model renders **NO text** (OCR-verified invariant, §11.2). Scrim behind every line (unreadable first line = reject). Sheets append-only for ledger/audit; idempotent publish guard.
6. **ACTION** — Implement the four MCP tools; wire the pipeline; land a piece in the Sheets queue.
7. **ACCEPTANCE** — §19 P1 exit: *one on-brand piece passes both gates and the ledger-linter and lands in the Sheets queue for the hard-coded test brand (no Review app).*
8. **VERIFY** — Run end-to-end; confirm the piece in Sheets with image (composited type, scrim, correct ratio), caption, alt text; OCR text-free check fires on a baked-glyph test. Capture this end-to-end run.
9. **AUTHORIZATION** — Owner authorizes P2.
10. **ON-FAIL** — If MCP↔ADK wiring is harder than the codelab suggested, fall back to the simplest conformant MCP server the docs support; do **NOT** fake MCP with an inline function (the protocol is the concept).

→ **GATE (§19 P1 exit):** one on-brand piece passes both gates + the ledger-linter and lands in the Sheets queue. Authorize P2.

#### PHASE 2 — Brand Kit + onboarding (the G1 core innovation) `[~3–4h, split into two gated contracts]`

**CONTRACT P2-A — Brand Kit schema + [[VARIABLE]] resolver**
**READ-SCOPE** (build-navigation, not a 10-field entry): read §7.2 (Brand Kit schema), §7.2.1 (resolver), §7.3 (seeding map), Appendix A (worked kit). Park §12.4, §14, §15 — later phases.
1. **INTENT** — Lift every brand-specific fact out of the agents into config, so "new brand" = config not code (G1).
2. **SCOPE** — `brand_kit.schema.json` (required/optional, enums, the three **fail-closed** safety fields must be owner-confirmed to validate); the `[[VARIABLE]]` **resolver** (§7.2.1: substitution at prompt-assembly; precedence Brand-Kit→env→error; fail-closed on missing required; secrets resolve **only** into the tool/MCP auth layer, never model-visible context; resolved values are literals, no re-resolution); the §7.3 seeding map (which field seeds which canon).
3. **NON-GOALS** — No interview yet (P2-B). No Offering agent (P3).
4. **INPUTS** — P1 slice (now the brand facts get externalized); PRD §7.2 schema + Appendix A worked example.
5. **INVARIANTS** — Unresolved required variable **blocks the run** and surfaces to owner (nothing drafted/published). Secrets never inlined into prompts.
6. **ACTION** — Author schema + resolver; retrofit the P1 agents to read `[[VARIABLE]]`s instead of hard-coded facts.
7. **ACCEPTANCE** — The P1 hard-coded brand now runs entirely from a `brand_kit.yaml`; a missing required var blocks with an owner-surfaced gap; the AOL Appendix-A kit validates.
8. **VERIFY** — Swap the brand facts to a second toy brand via Brand Kit only — the same agents produce that brand's piece with zero code change (the G1 proof). Run the "unresolved var blocks" scenario.
9. **AUTHORIZATION** — Owner authorizes P2-B.
10. **ON-FAIL** — If the resolver's serialization (lists/objects into prompts) is ambiguous at a use-site, define the per-site format explicitly (§7.2.1) rather than dumping raw YAML.

→ **GATE:** the P1 brand runs entirely from `brand_kit.yaml`; a second toy brand works via Brand Kit only (the G1 proof); missing-required-var blocks. Authorize P2-B.

**CONTRACT P2-B — Brand Onboarding Strategist + first-light**
**READ-SCOPE** (build-navigation, not a 10-field entry): read §7.1 (intake + first-light), §7.8 (archetype starters), Appendix A. Park §12.4, §15.4 — later phases.
1. **INTENT** — Capture a brand through a guided conversational interview (not a dead form), producing a valid Brand Kit (G3).
2. **SCOPE** — The **Strategist** agent (§7.1): one question at a time; proposes defaults; **source-ingests** (URL/handle/PDF/logo) to auto-draft **non-safety** fields; **elicits each safety-prohibition field explicitly with worked examples** (read/draft/act ladder — it reads/drafts, owner acts); the **`intake-interview` skill**; first-light commissions one end-to-end test post **including a deliberate near-violation** to surface unstated prohibitions.
3. **NON-GOALS** — Strategist must **not** silently auto-draft `claims_forbidden`/`non_disclosure_rules`/`required_framing` from marketing sources (which never contain prohibitions).
4. **INPUTS** — P2-A schema + resolver; the §7.1 intake design.
5. **INVARIANTS** — Safety fields elicited explicitly, never inferred-and-shipped. Output Brand Kit passes schema validation. No agent code/engine doc modified during onboarding (G1).
6. **ACTION** — Build the Strategist + intake skill; wire source ingestion; wire first-light.
7. **ACCEPTANCE** — §19 P2 exit: *new brand onboarded by interview with zero code changes; produces a piece.* The §7.1 onboarding scenario passes (one-at-a-time; drafts non-safety from sources; elicits safety explicitly; valid kit; first-light near-violation).
8. **VERIFY** — Onboard a fresh brand by interview; confirm zero code change + a produced piece + first-light surfaces a planted prohibition gap.
9. **AUTHORIZATION** — Owner authorizes P3.
10. **ON-FAIL** — If source-ingestion is brittle, fall back to strong defaults + explicit elicitation (the §20 mitigation); the interview, not ingestion, is the load-bearing part.

→ **GATE (§19 P2 exit):** new brand onboarded by interview with zero code changes; produces a piece. Authorize P3.

#### PHASE 3 — Full roster + cadence `[~4–6h]`

**CONTRACT P3 — Offering Content Agent + standing-week scheduler + ledger-linter + digest**
**READ-SCOPE** (build-navigation, not a 10-field entry): read §7.4 (Offerings), §9.4 (ledger-linter), §9.5 + §13 (cadence + control loop), §8.2. Park §12.4, §14.2 — later phases.
1. **INTENT** — Complete the roster and the always-on rhythm; make anti-repetition deterministic.
2. **SCOPE** — The **Offering Content Agent** (one role; Offering Brief as **dynamic context selected by `offering_id`** — adding an offering = new Brief + cadence slot, no agent-tree change/redeploy, G1); the **standing-week scheduler** (Cloud Scheduler tick → ME orchestrator → task graph w/ blocked-by wake, §13.2); the **deterministic ledger-linter** (§9.4 — the real implementation now, not the P1 stub: hook-in-3, back-to-back-shape, aphorism-1-in-5, idea-rerun-30d, treatment-label-repeat, research-min); the **`weekly-digest` skill** (the anti-silent-stall surface — what shipped/queued/missed/spend/CD↔owner rate); the **§9.5 queue-backpressure pause** (the Monday-tick precondition that pauses routine materialisation when the queue is deep AND the owner is absent — the one bounded exception to no-self-pause).
3. **NON-GOALS** — No Policy Server/claim-grounding/auto-publish (P4).
4. **INPUTS** — P2 Brand Kit + Strategist (Offering Briefs now drafted at intake); the §9.4 linter rules; §13 control loop.
5. **INVARIANTS** — Offering granularity (budget/memory/pause) re-keyed by `offering_id`. **No first-piece self-pause** — routines produce into the queue; gate is at publish — **except the one bounded §9.5 backpressure pause** (deep queue + prolonged owner absence). The linter hard-blocks pre-CD (it's what makes "countable violations =0" *true*).
6. **ACTION** — Build the Offering agent + brief-per-task selection; the scheduler/tick (incl. the §9.5 backpressure precondition); the real linter; the digest skill.
7. **ACCEPTANCE** — §19 P3 exit: *a full week auto-plans/drafts/reviews/queues; a rotation-violating draft is rejected pre-CD; a deep queue with no owner action for `owner_absence_pause_days` pauses routine materialisation (§9.5).* The §10.2 anti-repetition scenario and the §9.5 backpressure scenario pass deterministically.
8. **VERIFY** — Run a simulated week; confirm slots fill, the digest posts, and a planted rotation-violating draft bounces at the linter before CD; force queue-depth > `max_queue_depth` with owner-absence > `owner_absence_pause_days` and confirm routine materialisation pauses (CRITICAL alert + backpressure `AuditEntry`), and any owner action resumes it.
9. **AUTHORIZATION** — Owner authorizes P4.
10. **ON-FAIL** — If event-wake is hard, poll-based graph advancement is the documented default (§13.2); Firestore/Pub-Sub are the event-driven upgrade path layered on once the poll-based default is verified.

→ **GATE (§19 P3 exit):** a full week auto-plans/drafts/reviews/queues; a rotation-violating draft is rejected pre-CD; backpressure pauses routine materialisation on a deep queue + owner absence (§9.5). Authorize P4.

#### PHASE 4 — Governance & evaluation (the credibility core) `[~5–7h, split into two gated contracts]`

**CONTRACT P4-A — The deterministic gauntlet (Policy Server structural gate + claim-grounding + fail-closed safety + circuit-breaker + CI eval gate)**
**READ-SCOPE** (build-navigation, not a 10-field entry): read §14.2 (Policy Server + claim-grounding + fail-closed), §13.2 (circuit-breaker), §15.1–§15.3 + §18.2 (CI eval gate + golden set), §10.3 (blocker scenarios), `policies.yaml`. Park §12.4 and the publish-time referee (P4-B).
1. **INTENT** — Wire the *falsifiable* governance gauntlet — every gate deterministic and testable — before any publish tool is enabled.
2. **SCOPE** — The **Policy Server structural layer** (§14.2): default-deny `policies.yaml` (all 8 roles × tools × {preview,production}, unlisted=blocked) on all tools; **deterministic claim-grounding** on `caption_compose`/`instagram_publish` (numeric/verb claim ⇒ near-verbatim match to a VERIFIED `locked_sentence`, every number equal, else BLOCK); **fail-closed safety** on the three fields; the **run-level cost circuit-breaker** (§13.2 — per-run token accumulator + iteration cap; aborts + pauses; distinct from `max_output_tokens`); append-only **audit trail**; the **CI eval gate** (§18.2 step 4: pinned judge model + rubric, temp 0; pass/fail on automated §15.2 checks + golden-set threshold; holistic CD verdict advisory in CI).
3. **NON-GOALS** — No publish-time semantic referee yet (P4-B). No auto-publish enabling (P5).
4. **INPUTS** — P3 full roster; the §14.2 gate spec; `golden_set.md` (negatives labeled from owner decisions).
5. **INVARIANTS** — Default-deny (any role absent from `policies.yaml` is blocked). Circuit-breaker is the run-accumulator, not a per-call cap. Every gate here is deterministic/falsifiable.
6. **ACTION** — Author `policies.yaml` (all 8 roles); build the Policy Server structural middleware; the claim-grounding check; the breaker around the runner; the CI eval gate.
7. **ACCEPTANCE** — §19 P4-A exit: *deterministic safety/claim scenarios pass; circuit-breaker fires in test; CI eval gate blocks a golden-set regression.* The deterministic §10.3 blocker scenarios pass (cost breaker aborts a runaway; safety-field-unconfirmed fails closed; a claim can't ship unverified; non-disclosure binds words+image).
8. **VERIFY** — Run each deterministic §10.3 scenario; confirm the breaker fires on a forced runaway; confirm a golden-set regression blocks CI.
9. **AUTHORIZATION** — Owner authorizes P4-B.
10. **ON-FAIL** — If a gate can't be made deterministic at a use-site, keep the falsifiable structural check and log the deviation; never downgrade to a soft check silently.

→ **GATE (§19 P4-A exit):** deterministic safety/claim scenarios pass; breaker fires; CI eval gate blocks a golden-set regression. Authorize P4-B.

**CONTRACT P4-B — The publish-time semantic referee (the one soft gate)**
**READ-SCOPE** (build-navigation, not a 10-field entry): read §14.2 (publish-time semantic referee), §14.7 (untrusted content), §15.4 (adversarial suite). Park the UI (P5).
1. **INTENT** — Add the single soft, LLM-on-LLM gate — a **publish-time-only** semantic referee — layered on top of the deterministic gauntlet.
2. **SCOPE** — A second Gemini call at `instagram_publish` **only** (NOT on every draft — the CD is the draft-time judge): a semantic pass over the final caption + first-comment for CTA-forbidden smuggling, tone/framing, and residual non-disclosure risk the deterministic gate can't catch. Ties into §14.7 untrusted-content handling and the §15.4 adversarial suite.
3. **NON-GOALS** — Not a draft-time gate (avoids LLM-on-LLM + Denial-of-Wallet). Not a replacement for any P4-A deterministic gate.
4. **INPUTS** — P4-A gauntlet (the referee runs *after* the deterministic gates pass); the §14.2 referee spec.
5. **INVARIANTS** — Semantic referee runs **only** at publish. It is **additive** — it can BLOCK but never green-lights anything a deterministic gate blocked. Flaky/costly → it degrades to advisory, never disables a P4-A gate.
6. **ACTION** — Build the publish-time semantic referee; wire it after the P4-A gates at `instagram_publish`; add its §15.4 adversarial cases.
7. **ACCEPTANCE** — §19 P4-B exit: *a CTA-forbidden / tone-smuggling publish attempt is caught at publish-time by the referee, on top of a clean deterministic pass.*
8. **VERIFY** — Force a smuggled-CTA/near-miss publish that passes the deterministic gates; confirm the referee blocks it; confirm it degrades to advisory (P4-A still enforces) when disabled.
9. **AUTHORIZATION** — Owner authorizes P5.
10. **ON-FAIL** — If the referee is costly/flaky, keep the deterministic gates and treat the referee as the secondary catch the PRD already frames it as. Under the §19.2 tail-cut order it is the **last of the three cuttable units** (dropped only after P6 and P5-B) — but it is the **first gate to relax to advisory**, never at the cost of a P4-A deterministic gate.

→ **GATE (§19 P4-B exit):** the publish-time referee catches a smuggled-CTA/tone near-miss on top of a clean deterministic pass; degrades to advisory cleanly. Authorize P5. **(Cut-line: under deadline pressure P4-B is the last of the three tail-cuts — dropped only after P6 and P5-B; P4-A alone remains a safe, falsifiable governance floor.)**

#### PHASE 5 — Approval UI + publishing `[~4–6h, split into two gated contracts]`

**CONTRACT P5-A — Review app + manual handoff + Instagram publish (the path that must work)**
**READ-SCOPE** (build-navigation, not a 10-field entry): read §12.1 (Review app), §12.3 (publishing + Post Kit + mark-as-posted), §12.5 (approval protocol), §12.2 (Sheets integrity). Park §12.4 (Studio Floor → P5-B).
1. **INTENT** — Ship the focused approve/act surface and the gated publish path — the publishing that must work end-to-end.
2. **SCOPE** — The **Review app** (§12.1: queue list + piece detail + the §12.5 action set at parity with Sheets); **manual publish handoff** (the frictionless Post Kit, §12.3.1) + **mark-as-posted** (§12.3.2); **adapter-aware auto-publish** (§12.3: only when `auto_publish_enabled` AND mode auto/auto_after_trust-met AND all gates pass AND a channel adapter exists; **byte-serving check** — asset must serve raw `image/*` 200, not a Drive viewer page; **publish-then-comment** for first-comment hashtags; carousel cap confirmed at build time; **idempotent** via publish-once guard). `instagram_publish` is the only launch adapter (Instagram-Login path preferred).
3. **NON-GOALS** — No Studio Floor UI yet (P5-B). No Reels/Stories auto-publish (feed single-image + carousel only). Other channels manual-only until an adapter is registered.
4. **INPUTS** — P4 governance (publish must pass the Policy Server + byte-serving rule); §12.1/§12.3/§12.5 specs.
5. **INVARIANTS** — `auto_publish_enabled` is a master kill-switch; enabling auto-publish is **owner-only, never auto-flipped** (a §14.4 high-stakes action with a Vibe-Diff). Published asset is studio-hosted + byte-serving-valid, never a raw provider URL. Human edits in the app **re-run the deterministic gates** (§12.1/§12.5).
6. **ACTION** — Build the Review app; the manual handoff / Post Kit; the Instagram adapter + byte-serving check + publish-then-comment + idempotency.
7. **ACCEPTANCE** — §19 P5-A exit: *owner approves via Sheets and the app; manual publish works; auto-publish gated, idempotent & audited.* The §10.2/§10.3 publish scenarios pass.
8. **VERIFY** — Approve via both Sheets and app; manual-publish a piece; force a duplicate-approval poll (no double-post); force a Drive-viewer URL (publish blocks).
9. **AUTHORIZATION** — Owner authorizes P5-B.
10. **ON-FAIL** — Verify Instagram API prerequisites at build time (Business/Creator account; Instagram-Login vs Facebook-Login path); if blocked, manual handoff is the unaffected default.

→ **GATE (§19 P5-A exit):** owner approves via Sheets + app; manual publish works; auto-publish gated, idempotent, audited. Authorize P5-B.

**CONTRACT P5-B — The Studio Floor UI (the live agent-company console)**
**READ-SCOPE** (build-navigation, not a 10-field entry): read §12.4 (Studio Floor — the whole section), §5.3/§8.3 (progressive disclosure), §14.5 (observability spans). Park P6 material.
1. **INTENT** — Add the live agent-company console — a substantial web application on its own (which is why it is its own contract).
2. **SCOPE** — The **Studio Floor UI** (§12.4): the live agent graph + activity feed + stuck/loop/backpressure detection (incl. the §9.5 "materialisation paused" banner) + the "Floor Actions" intervention set + the trust panel; dark+light theming; first-run / empty / loading / error / offline states; the Brand Desk + Planner surfaces; a *rich view over the same audit trail as Sheets*.
3. **NON-GOALS** — Studio Floor adopts only the approachable Paperclip subset (§12.4) — no engineer-grade internals. It adds **no** new publish authority.
4. **INPUTS** — P5-A (the approve/act path + audit trail it visualises); the §12.4 UI spec; the §14.5 event/span model.
5. **INVARIANTS** — The Studio Floor is a *consumer* of the `sheets`/`drive` MCP tools and the §14.5 audit, **never** a competing source of truth; every Floor Action routes through the one §12.5 protocol; the circuit-breaker still wraps the runner, not the UI.
6. **ACTION** — Build the Studio Floor UI (graph / feed / intervention / trust + theming + states); wire it to the live event stream; route the intervention set through §12.5.
7. **ACCEPTANCE** — §19 P5-B exit: *the §12.4 Studio-Floor scenarios pass — a live handoff/loop is visible; a stuck-task intervention is audited; trust never auto-flips.*
8. **VERIFY** — Confirm a live handoff and a revise-loop render on the Studio Floor and an intervention writes to the audit trail.
9. **AUTHORIZATION** — Owner authorizes P6.
10. **ON-FAIL** — If the console fights the time-box, ship the approachable subset first; this is the **natural second scope-cut after P6** — the console is demo-polish, not demo-critical; P5-A is the path that must work.

→ **GATE (§19 P5-B exit):** the §12.4 Studio-Floor scenarios pass (live handoff/loop visible; intervention audited; trust never auto-flips). Authorize P6. **(Cut-line: under deadline pressure P5-B drops after P6 — P5-A is the publish path that must ship.)**

#### PHASE 6 — Improvement loop + multi-brand `[~4–6h]`

**CONTRACT P6 — Corrections mining + retro tuning + post-publication audit + multi-brand**
**READ-SCOPE** (build-navigation, not a 10-field entry): read §15.3 (post-publication audit + golden set), §12.2 (scaling/migration), §7.8 (multi-brand). Final phase — nothing to park.
1. **INTENT** — Close the learning loop and prove multi-brand.
2. **SCOPE** — Mine the **corrections log** (owner approves/edits/rejects) into the **monthly CD retro** (qualitative triage → engine/canon amendments); the **independent post-publication audit** (§15.3 — sample N published, biased to edited/escalated/auto; re-check with a fresh-context Gemini judge + human spot-audit; report **escape rates with CIs** — the §3.3 numbers); **CD↔owner calibration** tracked; run a **second brand** alongside the first.
3. **NON-GOALS** — No KMeans/fixed-k clustering, no formal before/after experiment harness (directional, owner-driven — §15.3).
4. **INPUTS** — P1–P5 running; the §15.3 audit + calibration design.
5. **INVARIANTS** — Escape rates come from the **independent** audit (not the gate that produced the content — unfalsifiable otherwise). Golden set labeled from **owner** decisions, not CD verdicts.
6. **ACTION** — Build corrections-mining → retro; the post-publication audit; calibration surfacing in the digest; onboard a second brand.
7. **ACCEPTANCE** — §19 P6 exit: *escape-rate audit reports CIs; CD↔owner calibration tracked; a second brand runs alongside the first.*
8. **VERIFY** — Produce one audit report with CIs; confirm two brands run from two Brand Kits on the same unchanged agent code (the ultimate G1 proof).
9. **AUTHORIZATION** — Owner declares the system feature-complete vs the PRD.
10. **ON-FAIL** — If multi-brand surfaces single-process limits, the PRD's DB + object-store migration is the documented next step (§12.2).

→ **GATE (§19 P6 exit):** escape-rate audit reports CIs; calibration tracked; two brands run on the same unchanged agent code (the ultimate G1 proof). Feature-complete vs PRD.

### 19.2 Critical-path notes

1. **P1-B is the load-bearing capstone unit.** It is where MCP becomes real and the pipeline closes. Budget the most care here — if MCP↔ADK wiring fights you, it's the ON-FAIL: the simplest conformant MCP server the docs support, **never** a faked inline function. The engineering fallback is always a genuine, conformant MCP server — never a false MCP claim (§16, §18.4).
2. **Resist scope creep ruthlessly inside each phase.** The PRD is vast; adding "just the Policy Server stub" during P1 is how phase boundaries blur. Build the phase you're in, verify, *then* proceed.
3. **Verify against live docs at build time** (model IDs, Instagram API limits, ADK/MCP specifics) — only a live 404 proves a model absent; never silent-fallback (§14.3). Training/codelab knowledge may be stale.
4. **Scope-cut order (if the July-6 deadline bites).** Cut from the tail: **P6**, then **P5-B** (the Studio Floor console — demo-polish, not demo-critical), then **P4-B** (the publish-time semantic referee — the one soft gate). The P4/P5 splits put each cut on a clean contract boundary; **P4-A** (the falsifiable governance floor) and **P5-A** (the publish path that must ship) never drop. The lock-and-proceed gates, not the time-boxes, are the schedule.

### 19.3 Build-order summary (lock-and-proceed; verify-before-next)

P0 scaffold → **P1-A six agents → P1-B pipeline + Sheets + Caption-Composer** (multi-agent + MCP + skills + a gate, end-to-end, one brand) → P2 Brand Kit + Strategist (the G1 innovation) → P3 Offering agent + scheduler + linter + digest → **P4-A deterministic gauntlet** (Policy Server + claim-grounding + breaker + CI eval) → **P4-B publish-time semantic referee** → **P5-A Review app + manual handoff + publishing** → **P5-B Studio Floor UI** → P6 improvement loop + multi-brand.

**The complete Agent Atelier is the build target — P0 through P6, in order (§21).** Each phase is a build unit that is locked-and-proceeded: every unit VERIFIED against its gate before the next begins. The demo shows the full end-to-end flow; the writeup describes the complete built system.

---

