# Content Ledger — [[BRAND_NAME]]

> **The anti-repetition memory.** Every content agent reads this BEFORE drafting and appends a row when a piece is approved by the Creative Director. The CD verifies the row at review time — a draft without its ledger row is returned unread. The Publishing & Operations agent confirms the row exists, alt text is present, and the deterministic ledger-linter is clean before queueing to the approval gate ([[APPROVAL_MODE]]).
>
> **System of record.** This ledger lives in the project's Google Sheets / Drive system of record (one feed = one ledger across **all** agents) — not a third-party notes tool. The deterministic ledger-linter reads the Sheets ledger directly.
>
> The rotation rules this ledger enforces live in `creative_engine` (caption hook + shape rules) and `visual_concepts` (visual-treatment rotation). Summary:
> hook pattern — no repeat within the last 3 posts · caption shape — no back-to-back, aphorism shape ≤ 1-in-5 of the trailing window · visual-treatment label — no back-to-back repeat · idea — no re-run within 30 days · ≥ [[RESEARCH_POST_MIN_PER_WEEK]] research post(s) per week when that value > 0.
>
> Append rows at the TOP (newest first). One row per piece, including rejected-then-killed pieces (mark KILLED — failed ideas also shouldn't repeat).

## Row column spec

Each row records exactly these fields (matches the §9.4 ledger schema and the Sheets Calendar/Queue surface):

| Column | Meaning |
|--------|---------|
| **Date** | ISO date the piece was approved / slotted. |
| **Piece** | Stable piece id (project-issued; one per piece, killed pieces included). |
| **Agent** | Owning content agent for the piece. |
| **Channel/Format** | One of [[CHANNELS]] plus the format (e.g. single / carousel). |
| **Topic → Idea** | One-sentence topic→idea; the load-bearing claim, framing, or angle. |
| **Hook** | Hook-pattern label from `creative_engine` (the rotated identifier, not the prose). |
| **Shape** | Caption-shape label from `creative_engine`. |
| **Visual** | Visual-treatment **label** from `visual_concepts` (the rotated label, plus an optional in-parentheses scene note). |
| **Language** | Per-piece language from [[LANGUAGES]]. |
| **Status** | Lifecycle state (see below). |

**Status lifecycle.** `drafted → in_review (CD) → revise(≤2) → CD-approved → pending-image → board-approved → queued → published`, with terminal `KILLED` / `SUPERSEDED` for ideas that must not re-run. Record the round and a short note inline (e.g. "CD-approved, pending image"). Killed and superseded rows stay in the ledger so their ideas are blocked from re-running.

## Deterministic ledger-linter (the countable rules)

The **deterministic ledger-linter** reads this ledger and runs **BEFORE CD review**, hard-blocking any draft that violates a **countable** rule over a pinned trailing window (e.g. the last ~30 rows, or each rule's own window). This linter is what makes the program's "countable rotation violations reaching a human = 0" guarantee true. It is deterministic and fail-closed: an unreadable or missing ledger blocks the run rather than passing it.

Hard-block rules:

1. **Hook no-repeat-in-3** — the draft's hook pattern was used within the last 3 posts.
2. **Shape no-back-to-back** — the draft's caption shape equals the immediately prior piece's shape.
3. **Aphorism ≤ 1-in-5** — the aphorism caption shape exceeds 1-in-5 of the trailing window.
4. **Idea no-rerun-30d** — the topic→idea re-runs an idea (including KILLED/SUPERSEDED ideas) within 30 days.
5. **Research-min** — the weekly research-post minimum is not met, when [[RESEARCH_POST_MIN_PER_WEEK]] > 0.
6. **Visual-label no-back-to-back** — the recorded visual-treatment **label** repeats back-to-back.

**Out of scope for the linter (by design).** Rendered-image "visibly different" judgment is NOT a linter rule — it routes to the CD's post-render multimodal pass. There is deliberately **no** rigid gender/age/clothing/posture/lighting hard-block; that would fight the variety principle ([[VISUAL_VARIETY]]). The linter mechanically enforces exactly the six countable rules above and nothing more.

## How this ledger sits in the pipeline

- **Append on approval (discipline).** A content agent appends its row only when the piece is approved — never speculatively. The append is part of "approved," not a follow-up chore.
- **Lint before review.** Ops runs the deterministic linter before the CD sees the draft; a lint failure bounces the draft back to its agent unread.
- **CD verifies the row.** The Creative Director confirms the row exists and is accurate at review time; a draft missing its row is returned.
- **Ops audits before queueing.** A piece without its ledger row, alt text, or a clean lint does not reach the approval gate. Ops also surfaces ledger health in the weekly visibility digest.

## Ledger

| Date | Piece | Agent | Channel/Format | Topic → Idea (one sentence) | Hook | Shape | Visual | Language | Status |
|------|-------|-------|----------------|------------------------------|------|-------|--------|----------|--------|
| | | | | | | | | | |

---

*Owner: all content agents (append on approval), Creative Director (verify at review), Publishing & Operations (lint, audit before queueing, weekly digest). Newest rows at the top.*
