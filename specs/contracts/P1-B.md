<!-- DERIVED from PRD §19.1 (CONTRACT P1-B). Do NOT hand-edit; regenerate with tools/build_view_split.py after §19 edits. The PRD is the source of truth; this contract governs the build, it does not replace the spec. -->

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
