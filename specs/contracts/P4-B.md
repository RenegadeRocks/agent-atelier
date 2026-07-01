<!-- DERIVED from PRD §19.1 (CONTRACT P4-B). Do NOT hand-edit; regenerate with tools/build_view_split.py after §19 edits. The PRD is the source of truth; this contract governs the build, it does not replace the spec. -->

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
