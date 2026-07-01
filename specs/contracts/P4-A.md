<!-- DERIVED from PRD §19.1 (CONTRACT P4-A). Do NOT hand-edit; regenerate with tools/build_view_split.py after §19 edits. The PRD is the source of truth; this contract governs the build, it does not replace the spec. -->

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
