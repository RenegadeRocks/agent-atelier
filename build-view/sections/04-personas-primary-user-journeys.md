<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §4 (source lines 114–132). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 4. Personas & primary user journeys

### 4.1 Personas

- **Brand Owner / Operator (primary).** Possibly non-technical. Owns a product and wants a steady, high-quality social feed. Supplies the Brand Kit; reviews and approves/publishes; occasionally drops on-demand asks ("post about X this week").
- **Studio Administrator (may be the same person).** Installs/deploys Agent Atelier, sets budgets, connects integrations (Google account, image provider, Instagram), toggles auto-publish.
- **The agent company (internal "users").** The agents themselves are first-class actors with identities, permissions, and budgets.

### 4.2 Primary journeys

1. **Onboard a brand.** Owner completes the conversational intake → Agent Atelier compiles a Brand Kit → seeds the engine docs and agent context → runs a "first light" test piece for confirmation.
2. **Standing production.** On a schedule, the studio plans a week, drafts pieces across slots, illustrates, reviews, and queues them. Owner approves in Google Sheets (or, post-MVP, the built-in Review app).
3. **Campaign mode.** Owner provides an offering with dates/details (or a standalone seasonal/promo campaign) → studio overlays a campaign ladder on top of the standing cadence.
4. **On-demand ask.** Owner asks for a specific piece; the Managing Editor routes it same-day.
5. **Publish.** Approved pieces are published manually by the owner, or auto-published if the brand has opted in (and an adapter exists).
6. **Improve.** The studio reviews its own performance (what the owner approved/edited/published, and any metrics provided) and tunes its craft over time.

---

