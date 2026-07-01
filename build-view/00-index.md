<!-- DERIVED build-view file — do NOT hand-edit. Regenerate with `python3 tools/build_view_split.py`. Source of truth: specs/PRD-Agentic-Content-Studio.md -->

# build-view/00-index.md — the build navigation map

The PRD is kept whole at `specs/PRD-Agentic-Content-Studio.md`. This folder is a **derived, read-only view** for building without context rot: load `build-view/core.md` + your contract's READ-SCOPE files only — never the whole PRD.

## Sections

| § | File | Source lines | In core? | Read by contracts |
|---|------|-------------|----------|-------------------|
| §0 | `sections/00-how-to-read-this-spec.md` | 16–29 | ✅ core | — |
| §1 | `sections/01-executive-summary.md` | 30–41 |  | — |
| §2 | `sections/02-background-motivation.md` | 42–67 |  | — |
| §3 | `sections/03-goals-non-goals-success-metrics.md` | 68–113 | ✅ core | — |
| §4 | `sections/04-personas-primary-user-journeys.md` | 114–132 |  | — |
| §5 | `sections/05-conceptual-model.md` | 133–159 | ✅ core | P5-B |
| §6 | `sections/06-system-architecture-substrate-agnostic.md` | 160–232 |  | — |
| §7 | `sections/07-the-brand-kit-product-agnostic-configuration.md` | 233–791 |  | P2-A, P2-B, P3, P6 |
| §8 | `sections/08-the-agent-roster-generic-parameterized.md` | 792–860 |  | P1-A, P3, P5-B |
| §9 | `sections/09-the-canon-engine-documents-the-harness-s-shared.md` | 861–1025 |  | P1-A, P3 |
| §10 | `sections/10-the-content-production-pipeline-state-machine.md` | 1026–1190 |  | P1-A, P1-B, P4-A |
| §11 | `sections/11-visual-generation-typography-subsystem.md` | 1191–1236 |  | P1-B |
| §12 | `sections/12-review-approval-publishing-system-of-record.md` | 1237–1733 |  | P1-B, P5-A, P5-B, P6 |
| §13 | `sections/13-orchestration-scheduling.md` | 1734–1817 |  | P3, P4-A |
| §14 | `sections/14-governance-safety-security.md` | 1818–2057 |  | P4-A, P4-B, P5-B |
| §15 | `sections/15-evaluation-quality.md` | 2058–2138 |  | P4-A, P4-B, P6 |
| §16 | `sections/16-integrations-interfaces-mcp-first.md` | 2139–2188 |  | P0, P1-B |
| §17 | `sections/17-data-model.md` | 2189–2265 | ✅ core | — |
| §18 | `sections/18-tech-stack-build-plan-for-antigravity.md` | 2266–2354 |  | P0, P4-A |
| §19 | `sections/19-milestones-phased-roadmap.md` | 2355–2566 |  | — |
| §20 | `sections/20-risks-open-questions.md` | 2567–2578 |  | — |
| §21 | `sections/21-capstone-submission-kaggle-vibe-coding-agents.md` | 2579–2647 |  | — |
| App A | `sections/app-a-worked-example-the-art-of-living-ludhiana-brand.md` | 2648–2738 |  | P2-A, P2-B |
| App B | `sections/app-b-course-concept-mapping-capstone-rubric.md` | 2739–2782 |  | — |
| App C | `sections/app-c-glossary.md` | 2783–2798 |  | — |
| App D | `sections/app-d-specs-brands-file-map-authored-artifacts.md` | 2799–2837 |  | P0 |

## Per-contract READ-SCOPE → files (from PRD §19.1)

For each contract, load **`core.md` + these files** (plus `GEMINI.md`/`AGENTS.md`, always loaded). Everything else is parked. The `.agents/workflows/build-<id>.md` command for each contract lists the same set.

| Contract | READ-SCOPE (PRD text) | Load these build-view files | Park |
|----------|-----------------------|-----------------------------|------|
| **P0** | §18 (build workflow + governance), §16 (MCP contracts), Appendix D (file map) | `core.md`<br>`sections/18-tech-stack-build-plan-for-antigravity.md`<br>`sections/16-integrations-interfaces-mcp-first.md`<br>`sections/app-d-specs-brands-file-map-authored-artifacts.md` | §7–§15 — later phases |
| **P1-A** | §8 (roster + agent instruction files), §9.1–§9.4 (engine docs + linter), §10.1 (pipeline) | `core.md`<br>`sections/08-the-agent-roster-generic-parameterized.md`<br>`sections/09-the-canon-engine-documents-the-harness-s-shared.md`<br>`sections/10-the-content-production-pipeline-state-machine.md` | §7 (Brand Kit), §12.4, §14 — later phases |
| **P1-B** | §10.1 (pipeline), §11.2 (Caption-Composer), §12.2 (Sheets integrity), §16.1 (MCP contracts) | `core.md`<br>`sections/10-the-content-production-pipeline-state-machine.md`<br>`sections/11-visual-generation-typography-subsystem.md`<br>`sections/12-review-approval-publishing-system-of-record.md`<br>`sections/16-integrations-interfaces-mcp-first.md` | §7, §12.4, §14 — later phases |
| **P2-A** | §7.2 (Brand Kit schema), §7.2.1 (resolver), §7.3 (seeding map), Appendix A (worked kit) | `core.md`<br>`sections/07-the-brand-kit-product-agnostic-configuration.md`<br>`sections/app-a-worked-example-the-art-of-living-ludhiana-brand.md` | §12.4, §14, §15 — later phases |
| **P2-B** | §7.1 (intake + first-light), §7.8 (archetype starters), Appendix A | `core.md`<br>`sections/07-the-brand-kit-product-agnostic-configuration.md`<br>`sections/app-a-worked-example-the-art-of-living-ludhiana-brand.md` | §12.4, §15.4 — later phases |
| **P3** | §7.4 (Offerings), §9.4 (ledger-linter), §9.5 + §13 (cadence + control loop), §8.2 | `core.md`<br>`sections/07-the-brand-kit-product-agnostic-configuration.md`<br>`sections/09-the-canon-engine-documents-the-harness-s-shared.md`<br>`sections/13-orchestration-scheduling.md`<br>`sections/08-the-agent-roster-generic-parameterized.md` | §12.4, §14.2 — later phases |
| **P4-A** | §14.2 (Policy Server + claim-grounding + fail-closed), §13.2 (circuit-breaker), §15.1–§15.3 + §18.2 (CI eval gate + golden set), §10.3 (blocker scenarios), policies.yaml | `core.md`<br>`sections/14-governance-safety-security.md`<br>`sections/13-orchestration-scheduling.md`<br>`sections/15-evaluation-quality.md`<br>`sections/18-tech-stack-build-plan-for-antigravity.md`<br>`sections/10-the-content-production-pipeline-state-machine.md`<br>`specs/policies.yaml` | §12.4 and the publish-time referee (P4-B) |
| **P4-B** | §14.2 (publish-time semantic referee), §14.7 (untrusted content), §15.4 (adversarial suite) | `core.md`<br>`sections/14-governance-safety-security.md`<br>`sections/15-evaluation-quality.md` | the UI (P5) |
| **P5-A** | §12.1 (Review app), §12.3 (publishing + Post Kit + mark-as-posted), §12.5 (approval protocol), §12.2 (Sheets integrity) | `core.md`<br>`sections/12-review-approval-publishing-system-of-record.md` | §12.4 (Studio Floor → P5-B) |
| **P5-B** | §12.4 (Studio Floor — the whole section), §5.3/§8.3 (progressive disclosure), §14.5 (observability spans) | `core.md`<br>`sections/12-review-approval-publishing-system-of-record.md`<br>`sections/05-conceptual-model.md`<br>`sections/08-the-agent-roster-generic-parameterized.md`<br>`sections/14-governance-safety-security.md` | P6 material |
| **P6** | §15.3 (post-publication audit + golden set), §12.2 (scaling/migration), §7.8 (multi-brand) | `core.md`<br>`sections/15-evaluation-quality.md`<br>`sections/12-review-approval-publishing-system-of-record.md`<br>`sections/07-the-brand-kit-product-agnostic-configuration.md` | Final phase — nothing to park |

## Contracts (BUNNY) 

The eleven gated prompt-contracts are carved from §19.1 into `specs/contracts/P*.md` (also derived — regenerate the splitter after §19 edits). The full roadmap is §19 (`sections/19-milestones-phased-roadmap.md`).
