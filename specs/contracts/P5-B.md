<!-- DERIVED from PRD §19.1 (CONTRACT P5-B). Do NOT hand-edit; regenerate with tools/build_view_split.py after §19 edits. The PRD is the source of truth; this contract governs the build, it does not replace the spec. -->

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
