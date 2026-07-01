<!-- DERIVED from PRD §19.1 (CONTRACT P5-A). Do NOT hand-edit; regenerate with tools/build_view_split.py after §19 edits. The PRD is the source of truth; this contract governs the build, it does not replace the spec. -->

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
