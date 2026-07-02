---
name: weekly-digest
description: Compose and post the weekly visibility digest — what shipped, what's queued and for how long, slots hit/missed, research minimum, paused routines/pending approvals, image spend, and CD↔owner agreement rate.
---

# weekly-digest

The Publishing & Operations Agent's Friday digest (PRD §8.2, §15.3). This digest is *why the
engine can never silently stall* — it surfaces every queued, paused, or pending item with a
link so nothing rots invisibly.

## Inputs

- The Calendar/Queue sheet (system of record) and the append-only `AuditEntry` log.
- The Content Ledger (for slots hit/missed and research-minimum tracking).
- `Run` cost records (tokens + image spend).
- The CD verdict log vs owner Approve/Edit/Reject signals.
- `[[POSTS_PER_WEEK_TARGET]]`, `[[MAX_POSTS_PER_WEEK]]`, `[[RESEARCH_POST_MIN_PER_WEEK]]`,
  `[[STANDING_WEEK]]`.

## Procedure

1. **What shipped.** List published pieces this week with piece_id, channel (`[[CHANNELS]]`),
   track/offering, and language. Compare count against `[[POSTS_PER_WEEK_TARGET]]` (ceiling
   `[[MAX_POSTS_PER_WEEK]]`).
2. **What's queued and for how long.** List Approval-Queue / CD-Review items with age in days
   and a direct link; call out anything aging past threshold.
3. **Slots hit/missed.** Reconcile the week against `[[STANDING_WEEK]]`; name missed slots.
4. **Research minimum.** When `[[RESEARCH_POST_MIN_PER_WEEK]] > 0`, report whether the
   research-grounded minimum was met (omit when 0).
5. **Paused routines / pending approvals.** List each with a link and the reason it is waiting
   (e.g. fail-closed safety field unconfirmed, round-3 escalation, provider error). Include a
   **§9.5 backpressure line** when materialisation is paused (queue depth, days since last
   owner action, "any action resumes it") and call out any `Stale-Dated` or `posted_unverified`
   pieces awaiting the owner.
6. **Image spend.** Sum image generation cost and total tokens from `Run` records for the week.
7. **CD↔owner agreement rate.** Compute agreement rate + false-approve count from CD verdicts
   vs owner actions. This is the explicit trust signal gating `auto_after_trust → auto`
   against `[[TRUST_THRESHOLD]]`; surface it prominently.
8. **Post it.** Write the digest to the agreed surface (Sheet tab and/or `notify`), append an
   `AuditEntry`. Read-only over the SoR — the digest never mutates queue status.

## Output

A posted weekly visibility digest covering the eight items above, each actionable item linked.

## When to use / When NOT

- **Use** on the weekly cadence (Friday), or on demand when the owner asks "what's the state
  of the studio?".
- **Do NOT use** to change queue status, approve/publish pieces, or run rotation checks (that
  is `ledger-lint`/`ledger-audit`). The digest reports; it does not act.

Examples: "post this week's visibility digest with the CD↔owner agreement rate"; "show queued items aging past 3 days and the week's image spend".
