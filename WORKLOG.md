# WORKLOG — mid-contract scratchpad

This is the **hand-off memory** between sessions and between PCs (office ↔ home). Keep it
current and commit+push before you stop (build-protocol §2). On the other machine, `git
pull` then run `.agents/workflows/resume.md`. Antigravity's chat/memory is per-machine and
does not travel between PCs — this file, plus the code and the spec, is what remembers.

**Overwrite the block below** each time you stop mid-contract. When a contract is fully
done + authorized, clear it and tick the contract in `BUILD-STATUS.md`.

---

## Current

- **Contract:** P1-B (Done)
- **Sub-tasks done:** Implemented functional file-based mock MCP servers for Sheets, Drive, Caption Compose, and Image Generate. Refactored the core pipeline (`app/pipeline.py`) into a state machine that respects review loops, escalations, and the visual/OCR text-free check loop. Wrote and passed Gherkin acceptance tests for the deterministic block limits and the successful queue routing.
- **Sub-tasks remaining:** None for P1-B.
- **Current file state / where the code is:** MCP servers successfully mock schemas without external API calls. `test_p1_b.py` is fully green and verifies state routing logic.
- **▶ NEXT ACTION (the one thing to do on resume):** Run `.agents/workflows/build-P2-A.md`.
- **Open questions / waiting on owner:** Authorized to move to P2-A.
- **Last commit:** State machine pipeline + MCP tool simulation + P1-B Tests.
- **Machine last worked on:** Office/Home (Leaving)

## DEVIATION LOG
- **[Date: 2026-07-04] Reverted physical object subject ban**: A product-content rule ("must be physical object, no screens/signs") was incorrectly injected into the test pipeline prompt to dodge the OCR loop. This was a deviation from the visual engine mandate (treatment should be driven by the message). It has been reverted. The pipeline now correctly relies on the text-free constraint appended to the image generation prompt and the OCR loop to enforce text-free images.
- **[Date: 2026-07-04] Font Fidelity**: Using `arialbd.ttf` (or system default) as an open-source stand-in for brand fonts during caption composition.
- **[Date: 2026-07-04] Image Target Backend**: Using Google Cloud Storage backend for the Drive tool due to service-account storage quota limits on the consumer Drive account.
- **[Date: 2026-07-04] Token Resolution Stub**: Added a hard-coded `TEST_BRAND_MAP` and substitution function applied at prompt assembly so agents don't emit `[[TOKENS]]`. The P1 contracts state brand facts are hard-coded until P2-A. The true dynamic Brand Kit resolver will replace this temporary stub at P2-A.
---

### Template (copy the shape above)

```
## Current
- Contract: P<id> (Phase <n>)
- Sub-tasks done: <bullet list>
- Sub-tasks remaining: <bullet list>
- Current file state: <which files exist, which are half-written, test red/green>
- ▶ NEXT ACTION: <one concrete next step>
- Open questions / waiting on owner: <...>
- Last commit: <hash / message>
- Machine last worked on: <office | home>
```
