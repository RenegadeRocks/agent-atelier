<!-- DERIVED from PRD §19.1 (CONTRACT P2-B). Do NOT hand-edit; regenerate with tools/build_view_split.py after §19 edits. The PRD is the source of truth; this contract governs the build, it does not replace the spec. -->

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
