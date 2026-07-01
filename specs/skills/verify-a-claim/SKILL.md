---
name: verify-a-claim
description: Verify a factual/statistical claim against allowlisted sources and produce a caption-ready, locked, hedged Claim-Bank entry — or return the respected verdict "cannot verify".
---

# verify-a-claim

The Research & Verification Agent's procedure for turning a candidate claim into a shippable
`ClaimBankEntry` (PRD §8.2, §9.3, §17). Only VERIFIED entries with locked wording may ship;
"Cannot verify" is a respected, first-class verdict.

Policy resolves from the Brand Kit: allowlist `[[SOURCE_ALLOWLIST]]`, denylist
`[[SOURCE_DENYLIST]]`, re-verify cadence `[[CLAIM_REVERIFY_MONTHS]]` months, second-source
requirement `[[REQUIRE_SECOND_SOURCE_FOR_QUANTITATIVE]]`, and mandatory hedges
`[[REQUIRED_FRAMING]]`.

## Inputs

- `claim`: the candidate sentence/statistic/year a content agent wants to use.
- Tool: `research_fetch` (allowlist-bound, sanitized retrieval + grounding).

## Procedure

1. **Scope the claim.** Identify numbers, percentages, study year, and research verbs
   (study/research/shows/found/reduced). These are what the publish-time Policy Server will
   match deterministically (PRD §14.2), so they must be exact.
2. **Retrieve from allowlisted sources only.** Use `research_fetch` against
   `[[SOURCE_ALLOWLIST]]`; reject anything on `[[SOURCE_DENYLIST]]` (blogs, forums, unverified
   social). Prefer primary/authoritative sources.
3. **Independent semantic confirmation.** A second-model verifier (Gemini, mirroring the §14.2
   semantic referee) confirms the locked sentence faithfully represents the source's
   population, design, and finding — not an overreach.
4. **Second source for quantitative.** If `[[REQUIRE_SECOND_SOURCE_FOR_QUANTITATIVE]]` is true,
   require a second corroborating source before VERIFIED.
5. **Lock the wording.** Write a caption-ready `locked_sentence`: hedged, source+year named,
   numerically faithful. Apply `[[REQUIRED_FRAMING]]` for clinical/sensitive topics and flag
   such claims to the owner before first use. Stay inside `[[CLAIMS_ALLOWED]]`; never assert
   anything in `[[CLAIMS_FORBIDDEN]]`.
6. **Hash + decay.** Store `source_hash`, `accessed_at`, and `reverify_at = now +
   [[CLAIM_REVERIFY_MONTHS]] months`. On re-verify / periodic check, re-fetch and compare; a
   changed or missing source → RETIRED or PENDING and pulled from shipping.
7. **Status + audit.** Set status `PENDING → VERIFIED` (or leave PENDING / set RETIRED). Append
   an audit entry. Owner/CD spot-audit a small VERIFIED sample, not every entry.

## Output

A `ClaimBankEntry { status, locked_sentence, source_url, source_hash, accessed_at, reverify_at }`,
or an explicit **"cannot verify"** result that blocks the claim from shipping. Confirm
model/tool names+IDs at build time.

## When to use / When NOT

- **Use** when a draft (especially a `research_grounded` slot) needs a statistic/percentage/
  study-year/research-verb, when a testimonial makes a factual assertion, or when a claim's
  `reverify_at` is due.
- **Do NOT use** for opinion/voice lines that make no factual claim, and never hand-edit a
  `locked_sentence` downstream — re-run this skill instead. Verification does not write captions.

Examples: "verify 'X reduces stress 23% (Author 2021)' against `[[SOURCE_ALLOWLIST]]`"; "re-verify all Claim-Bank entries past their reverify_at".
