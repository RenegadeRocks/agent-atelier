<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §app-d (source lines 2799–2837). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## Appendix D — `/specs` & `/brands` file map (authored artifacts)

The spec is the source of truth, but the harness artifacts are **authored alongside it**, not left to regeneration (a Day-4 principle: instruction/rule files are source code). Legend: ✅ authored · ☐ deferred to its build phase.

```
specs/
  agents/                 ✅ 8 generic agent prompt templates ([[VARIABLE]]-templated):
                              managing-editor · research-verification · evergreen-content ·
                              offering-content · creative-director · visual-production ·
                              publishing-operations · brand-strategist
  canon/                  ✅ engine docs: creative_engine.md · visual_engine.md · research_bank.md ·
                              content_ledger.md · cadence_plan.md · brand_voice.md ·
                              visual_style_guide.md · brand_assets.md · offering_brief.template.md
    channel_style_guides/ ✅ instagram.md · facebook.md
  skills/                 ✅ 8 SKILL.md: draft-a-piece · verify-a-claim · per-image-brief ·
                              compose-caption · ledger-lint · weekly-digest · ledger-audit · intake-interview
  policies.yaml           ✅ complete default-deny matrix (all 8 roles × tools × preview+production)
  brand_kit.template.yaml ✅  + brand_kit.schema.json (required/optional, enums, fail-closed flags)
  resolver.md             ✅ [[VARIABLE]] registry (token → field → serialization → target) + resolver pseudocode
  golden_set.md           ✅ schema + seed exemplars (incl. negatives) + CI pass threshold
  secrets.md              ✅ vault choice, secrets_ref schema, named keys per integration, rotation/scoping

  redteam.md              ✅ Red/Blue/Green adversarial-vibes suite: attack × bound-invariant table + escape-log schema (§15.4)
  agent_cards/            ✅ creative-director.json — the illustrative A2A Agent Card (§13.3)
  schemas/                ✅ MCP tool output schemas (§16.1) · notify payload schema (§16.2) · conscious-deviation-entry schema (§18.4.4)
  contracts/              ☐ eleven BUNNY prompt-contracts: P0·P1-A·P1-B·P2-A·P2-B·P3·P4-A·P4-B·P5-A·P5-B·P6 (§18.4 / §19.1)
  deviation_log.md        ☐ conscious-deviation log: assumption → ground truth → decision (§18.4.4)
GEMINI.md / AGENTS.md     ✅ project DNA + conventions + skills router
brands/
  aol/
    brand_kit.yaml        ✅ Appendix A as a committed example
    offerings/            ✅ happiness_program.md · sahaj_samadhi.md (filled Offering Briefs)
```

The Atelier Review app (§12.1) and the **Studio Floor UI (§12.4)** component specs are intentionally ☐ deferred to Phase 5; the eleven prompt-contracts (`contracts/`) and `deviation_log.md` are ☐ created at the P0 scaffold (§18.4); per-channel guides beyond Instagram/Facebook are ☐ added per launch channel.

---

*End of PRD (v4). This document is the source of truth; regenerate code from it, not the reverse.*
