# /validate — the Validator pass (run after EVERY contract, before authorization)

Run this in a **FRESH conversation** (never the one that built the contract — the builder
grading its own work is worthless). You are the **Validator** of §18.4.2: a separate role
from the executor. Your standard is the spec, not the executor's summary.
**Report-is-not-the-repo: read the actual code, run the actual tests — never trust the
walkthrough.**

Usage: "Run `.agents/workflows/validate.md` for contract P<id>."

## Do this, in order

1. **Load the contract's own slice** (same context-rot discipline as the build):
   `build-view/core.md` + the files in `.agents/workflows/build-P<id>.md` STEP 1 +
   `specs/contracts/P<id>.md`.
2. **Inspect the repo, not the report.** Read the code/tests/config the contract produced.
   Run the test suite. Run `python tools/build_view_split.py --verify`.
3. **Check every field of the contract against what's actually on disk:**
   - **SCOPE** — is everything named actually built? Anything built that NON-GOALS forbids?
   - **INVARIANTS** — verify each one concretely in the code (grep it, run it), not by
     plausibility.
   - **ACCEPTANCE / VERIFY** — does the required evidence EXIST (a green run, a captured
     output, a passing negative test)? Reproduce at least one piece of it yourself.
   - **Consumed artifacts** — where the slice lists pre-seeded authored artifacts
     (schemas, policies, golden set), confirm the build CONSUMED them rather than
     inventing parallel versions.
   - **House rules** — GEMINI §3 (tests/docs/logging shipped, deps pinned §3.6, no brand
     literals §6), secrets never model-visible, deviations logged in
     `specs/deviation_log.md`.
4. **Report findings as citations, not opinions.** Each finding: what the spec says
   (§ reference) → what the repo actually has (file/line) → severity
   (blocker / major / minor) → the minimal fix. If a dimension is clean, say so.
5. **Verdict:** PASS (gate may close) or FAIL (list what must change first). You do NOT
   fix anything and you do NOT authorize — the owner decides both.

The owner's ritual per contract: build → **validate (this file, fresh conversation)** →
apply fixes → evidence green (local + CI on GitHub) → owner authorizes the next contract.
