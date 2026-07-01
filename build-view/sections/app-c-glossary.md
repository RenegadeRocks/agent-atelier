<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §app-c (source lines 2783–2798). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## Appendix C — Glossary

- **Brand Kit** — the per-product configuration bundle (YAML + assets + secrets ref) that makes the studio product-agnostic.
- **Canon / Engine docs** — the generic, shared instruction documents (Creative Engine, Visual Engine, Research/Claim Bank, Content Ledger, Cadence Plan, voice/style/asset guides).
- **Offering** — a thing being marketed; each gets an Offering Brief (dynamic context for the single Offering Content Agent role).
- **Content Ledger + ledger-linter** — the anti-repetition memory; the linter deterministically enforces countable rotation rules before CD review.
- **Claim Bank** — the verified-claims store; only `VERIFIED` entries with locked wording (and matching numbers) may ship.
- **Harness** — everything around the model that makes it an agent.
- **Policy Server** — the structural + claim-grounding + (publish-time) semantic gate in front of tool calls; default-deny.
- **Caption-Composer** — the swappable typography-compositing capability (replaces the legacy `caption.py`).
- **System of record** — Google Sheets + Drive (default) holding the calendar, ledger, queue, and append-only audit.
- **Vibe Diff** — a plain-language summary of a proposed high-stakes change, shown to the owner before sign-off.
- **Trust threshold** — the concrete, owner-tunable rule that surfaces a recommendation to enable auto-publish.

---

