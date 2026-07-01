---
name: ledger-lint
description: Run the deterministic ledger-linter over a draft's fields against the trailing Content Ledger window and hard-block countable rotation-rule violations BEFORE Creative Director review.
---

# ledger-lint

The Publishing & Operations Agent's deterministic gate (PRD §9.4, §10.1 `[LEDGER LINT]`). It
is the mechanism that makes the "countable rotation violations = 0" guarantee true. It runs
on every draft, BEFORE CD review, and **hard-blocks** on any countable violation. It is
deterministic code, not a judge.

This is deliberately scoped: rendered-image "visibly different" judgment is NOT here — that
routes to the CD's post-render multimodal pass. There is intentionally no rigid gender/age/
clothing/posture/lighting hard-block (that would fight the variety principle).

## Inputs

- The `Draft` ledger fields: `hook`, `shape` (caption shape), `visual_label` (visual treatment
  label), `idea` (topic→idea sentence), `language`, `format`, `status`.
- The Content Ledger (Sheets), read over a pinned trailing window (e.g. last ~30 rows; each
  rule applies its own window).
- `[[RESEARCH_POST_MIN_PER_WEEK]]` (for the research-minimum rule).

## Procedure — the six countable checks

1. **Hook recency** — BLOCK if `hook` matches any hook used in the **last 3 posts**.
2. **Shape back-to-back** — BLOCK if `shape` equals the **immediately prior** post's shape.
3. **Aphorism cap** — BLOCK if the aphorism shape would exceed **1-in-5** of the trailing
   window.
4. **Idea re-run** — BLOCK if this `idea` re-runs an idea from the **last 30 days**.
5. **Research minimum** — when `[[RESEARCH_POST_MIN_PER_WEEK]] > 0`, BLOCK the week's queue
   from proceeding if the weekly research-minimum is not met (skip this rule entirely when the
   value is 0).
6. **Visual-treatment label back-to-back** — BLOCK if `visual_label` repeats the
   **immediately prior** recorded visual-treatment label.

For each violation, return a precise, machine-readable reason (rule id + the conflicting prior
row/piece_id) so the content agent can self-repair and re-draft.

## Output

`PASS` (proceed to CD review) or `BLOCK` with the list of failed rules and conflicting rows.
A BLOCK never reaches the CD. No side effects on the ledger.

## When to use / When NOT

- **Use** automatically on every draft immediately before CD review, and as a pre-check a
  content agent can self-run while drafting.
- **Do NOT use** for subjective sameness/craft/quality (that is the CD Gate 0 + post-render
  pass), for image "visibly different" judgment, or to append/audit ledger rows (that is
  `ledger-audit`). Do not soften a BLOCK into a warning — these rules are hard.

Examples: "lint this draft against the last 30 ledger rows before CD"; "check whether this week still needs its research-grounded post".
