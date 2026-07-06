# P2-B Walkthrough: Brand Onboarding Strategist

## Changes Made
- Implemented `brand_strategist.py` using `google.adk.Agent` and the `intake-interview` skill.
- Created `source_ingest.py` to ingest local markdown/text files for auto-drafting non-safety fields, safely declining unsupported sources.
- Built `onboard_brand.py` as an interactive CLI for the owner to conduct the read/draft/act ladder with the Strategist.
- Addressed `ResolveBlocked` defect on launch by removing the `resolve()` fail-closed mechanism from the pre-kit Strategist template.
- Fixed the ingestion scope defect so the agent only reads from the `sources/` subdirectory (preventing it from peeking at the answer sheet).

## What Was Tested
- Deterministic test ensuring `source_ingest` gracefully declines unsupported formats.
- Deterministic test validating that empty safety fields marked as `confirmed: true` throw a `jsonschema.ValidationError`, structurally preventing the P2-A defect.
- Deterministic test ensuring `onboard_brand.py` ingestion scope correctly ignores files outside the `sources/` directory.
- Deterministic test ensuring `onboard_brand.py` launches without `ResolveBlocked` by keeping `[[TOKENS]]` literal.

## Verification Results & Known Deviations
- **Faithfulness Check & Validation**: As observed during the live session, the Strategist successfully elicited and compiled the Brand Kit. However, the initial hallucination where it claimed to have saved the kit has been addressed. The `onboard_brand.py` CLI now parses the YAML from the LLM's response, saves it to disk (under a deterministic slug), and validates it via `app/brand_kit.py`.
- **Deviation Log - Auto-Retry Loop**: An automatic retry loop was added in `onboard_brand.py`. On parse or validation failure, it intercepts the output and injects `specs/brand_kit.template.yaml` back to the Strategist up to 2 times, forcing strict adherence to the schema.
- **First-Light Probe**: The live session log confirms the Strategist correctly amended `claims_forbidden` to include the packaging rule (*"No invented sustainability, zero-waste, or eco-friendly packaging claims"*), successfully demonstrating the fail-closed first-light safety probe. This rule was successfully persisted to the saved YAML kit.
- **Pre-filled Fields Leak**: During the live session, the Strategist pre-filled fields (e.g. Locale: "C-Scheme") because it erroneously ingested the owner's `intake-answers.md` alongside the source documents. This defect has now been fixed and covered by a deterministic test.
