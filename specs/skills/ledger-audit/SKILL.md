---
name: ledger-audit
description: Pre-queue audit and atomic append — assert a piece has its ledger row, alt text, and a clean lint; append the LedgerRow and write-once AuditEntry; bounce anything incomplete back.
---

# ledger-audit

The Publishing & Operations Agent's QUEUE-stage integrity step (PRD §9.4, §10.1 `[QUEUE]`,
§12.2). It is the gatekeeper between a rendered, CD-passed piece and the Approval Queue. A
piece missing its ledger row, its alt text, or a clean lint **bounces back**. It also owns the
append (write) side of the Content Ledger — one feed, one ledger across all agents.

## Inputs

- A piece that has passed CD review and the CD post-render multimodal pass.
- Its `Asset`(s) (with `alt_text`), `Draft` ledger fields, and the `ledger-lint` result.
- The Content Ledger and the append-only `AuditEntry` log (a protected tab or DB), plus the
  Calendar/Queue sheet.

## Procedure

1. **Assert ledger-row completeness.** Every required field present: date, piece_id, agent,
   channel/format, topic→idea sentence, hook pattern, caption shape, visual-treatment label,
   language, status. Missing any → bounce back with the gap named.
2. **Assert alt text.** Every `Asset` (each carousel slide) has non-empty `alt_text`. Missing
   → bounce to the Visual Production Agent (alt text is authored in VISUALIZE by
   `compose-caption`).
3. **Assert clean lint.** Confirm `ledger-lint` returned PASS for this piece. If not present
   or BLOCKED → bounce back to drafting.
4. **Atomic append.** On all-clear, append the `LedgerRow` using atomic, append-only writes.
   Killed/rejected ideas are also recorded (status reflects the outcome) so the anti-repetition
   memory stays complete.
5. **Write the audit entry.** Append a write-once `AuditEntry { action, actor_agent,
   approver_human?, target, timestamp }`. The orchestrator is the sole writer of derived
   status; never overwrite an existing audit row.
6. **Build the handoff bundle + queue.** Assemble the per-piece bundle (final caption in the
   correct language, hosted image(s) in order, alt text, channel, first-comment hashtags ready
   to paste, optional `location_tag` / `collaborator_handles`) and place the `QueueItem` into
   the Approval Queue for the owner gate under `[[APPROVAL_MODE]]`.

## Output

A complete `LedgerRow` + write-once `AuditEntry` + a `QueueItem` with handoff bundle in the
Approval Queue — or a bounce-back naming exactly what was missing. Publish remains idempotent
(publish-once guard keyed by `piece_id`).

## When to use / When NOT

- **Use** at the QUEUE stage for every piece before it reaches the human gate, and to append
  the ledger row for any approved or killed piece.
- **Do NOT use** to evaluate rotation rules pre-CD (that is `ledger-lint`), to judge craft, or
  to publish. The owner's Status-cell edit is an approval *signal*, not a competing write —
  never treat the human-editable queue sheet as the audit trail.

Examples: "audit and queue the approved Tuesday piece"; "append the ledger row for a rejected idea so it's remembered for 30-day idea re-run checks".
