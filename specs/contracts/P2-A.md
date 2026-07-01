<!-- DERIVED from PRD §19.1 (CONTRACT P2-A). Do NOT hand-edit; regenerate with tools/build_view_split.py after §19 edits. The PRD is the source of truth; this contract governs the build, it does not replace the spec. -->

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
