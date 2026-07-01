<!-- DERIVED from PRD §19.1 (CONTRACT P1-A). Do NOT hand-edit; regenerate with tools/build_view_split.py after §19 edits. The PRD is the source of truth; this contract governs the build, it does not replace the spec. -->

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
