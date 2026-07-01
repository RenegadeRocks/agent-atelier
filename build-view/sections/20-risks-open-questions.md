<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §20 (source lines 2567–2578). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 20. Risks & open questions

- **Image-model fidelity (typography/hands/product).** Mitigated by text-free generation + OCR backstop + composited type + the CD multimodal pass + regenerate-on-fail; `product_led` adds SKU-fidelity risk (real product hero mitigates it).
- **Onboarding depth vs. effort.** Source-ingestion + strong defaults + explicit safety elicitation + first-light feedback.
- **Auto-publish trust.** Human-default; gate auto behind the concrete `trust_threshold` + visual-judge calibration + Policy Server + audit; never auto-flipped.
- **Cost.** Run-level circuit-breaker + per-agent/per-offering budgets + model routing + carousel slide caps + image-tier discipline.
- **Judge bias.** Owner is ground truth under HITL default; CD↔owner calibration + negative golden-set guard against drift.
- **Resolved:** human gate at MVP is **Sheets-only (Phase 1)**; the **Review app is Phase 5**; **durable cross-run memory is Sheets-keyed** (a `memory` namespace) — **no Agent Engine Memory Bank dependency** (Memory Bank is a documented future upgrade).
- **Open question (owner):** channels beyond Instagram at launch (Facebook adapter? LinkedIn/YouTube/X later) — adapters are pluggable; launch publish adapter is Instagram only.

---

