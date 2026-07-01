# Research & Claims Bank — [[BRAND_NAME]] (generic canon template)

> **Status:** product-agnostic template. Brand values arrive at resolve time from the Brand Kit via `[[VARIABLE]]` substitution (PRD §7). Do not hard-code any brand fact here.
>
> **Owner agent:** Research & Verification Agent. **Approver:** the brand owner (human). **Escalation owner for sensitive/regulated claims:** the brand owner, routed via the Managing Editor.

> **Why this document exists.** Research-grounded insight is the credibility anchor of the feed, but requesting research per-piece is friction — so agents quietly stop making claims and the content loses its authority. This bank inverts the flow: the Research & Verification Agent maintains a standing pool of **pre-verified, pre-worded claims** that content agents lift directly. No per-piece research ticket is needed for anything already in the bank.
>
> **The official channel cannot be wrong on the internet.** Every entry carries a status. Only `VERIFIED` entries may ship. Authorship and verification are **separated** — producing a locked sentence is one step; flipping it to `VERIFIED` requires the independent verification protocol of §4. Numeric fidelity is additionally enforced deterministically at the publish boundary by the Policy Server's claim-grounding gate (PRD §14.2).

---

## 1. Status model

- **PENDING** — a lead. Plausible, sourced from memory or a secondary mention. **May not be used in any published content.**
- **VERIFIED** — the Research & Verification Agent has (a) located the primary source live, (b) confirmed the finding matches the wording, (c) locked an approved sentence, (d) recorded `source_url`, `source_hash`, and access date, and (e) cleared the independent verification protocol (§4). Content agents may use the locked sentence (or tighten it within §2) **without a new research ticket**.
- **RETIRED** — source retracted, aged out, failed re-verification, or pulled by the owner. **Never use.** Kept for history and audit.

A claim may only move `PENDING → VERIFIED` through §4. Any VERIFIED entry whose `source_hash` no longer matches on re-fetch is moved back to `PENDING` (or `RETIRED` if the source is gone) and **immediately pulled from shipping**.

## 2. Wording rules (apply to every use, no exceptions)

- **Hedged verbs only.** "associated with," "found," "reported," "linked to," "may support." Never "proves," "cures," "treats," "guarantees," "fixes" (or any verb on `[[CLAIMS_FORBIDDEN]]`).
- **Name the source when the claim is the hook.** Source + year, with the lead author when it reads naturally. This specificity is a feature, not clutter.
- **Honor `[[REQUIRED_FRAMING]]`.** Any claim whose topic appears in `[[REQUIRED_FRAMING]]` must carry the mandated framing verbatim in spirit (e.g. a sensitive-population finding never implies an offering replaces professional treatment or care). When in doubt, route to the owner via the Managing Editor.
- **Stay inside `[[CLAIMS_ALLOWED]]`; never enter `[[CLAIMS_FORBIDDEN]]`.** A locked sentence that drifts toward a forbidden claim is rejected, not softened.
- **Numbers only as published.** Never round up, never invent percentages, never generalize a specific count into a vaguer larger one.
- **One claim per caption.** A research carousel may carry up to three, one per slide.
- **Comparative claims** are permitted only if `[[COMPARATIVE_CLAIMS_ALLOWED]]` is true; otherwise no claim may compare the brand or offering to a named or implied competitor.
- **Locked wording is locked.** Content agents may lift a locked sentence verbatim or tighten it further within these rules. **Never loosen it**, never re-introduce a clause the verification record intentionally dropped.

## 3. The bank

> The standing pool of claims. Every row carries a status; **only `VERIFIED` rows may ship.** New leads enter as `PENDING`. The table starts empty — the Research & Verification Agent populates it from the Brand Kit's topical territory (`[[EVERGREEN_PILLARS]]`, `[[OFFERINGS]]`) and the owner's source material, then runs the §4 protocol.

| ID | Claim lead | Likely source | Status |
|----|------------|---------------|--------|
| *(none yet — populate via §4)* | | | |

**Topical organization.** Group rows under headings that mirror the brand's own territory (`[[EVERGREEN_PILLARS]]` and per-offering claim sets keyed by `[[OFFERING_ID]]`) once entries exist. Keep the brand's highest-value, most-cited claims at the top of their group and verify them first.

### 3a. Traditional, cultural, or experiential claims — never framed as research

Some brands make claims that are **teachings, heritage, craft lore, or lived experience**, not empirical findings. These are cited to their proper source — text, tradition, founder, or maker — and are **never dressed as science**. The distinction is part of the brand's integrity. The Research & Verification Agent flags any draft that blurs a teaching/experiential claim into a research claim (or vice versa). Such claims do not live in the §3 bank; they belong to the voice/knowledge canon.

## 4. Independent verification protocol (authorship is separated from verification)

Producing the locked sentence is one step. **Flipping a claim to `VERIFIED` requires every applicable gate below to pass.** Source retrieval is bound by `[[SOURCE_ALLOWLIST]]` / `[[SOURCE_DENYLIST]]`: pull from primary and authoritative sources on the allowlist (the source's own site, the publisher, the primary record); never from denylisted sources (blogs, forums, unverified social, AI summaries).

1. **Automated grounding.** Via the sanitized `research_fetch` tool: the `source_url` resolves, and **every numeric figure and named statistic in the locked sentence appears on the fetched page.** Any failure keeps the claim `PENDING`.
2. **Independent semantic confirmation.** A **second-model verifier** (a separate model call, mirroring the Policy Server's semantic referee, PRD §14.2) confirms the locked sentence **faithfully represents the source's population, design, and finding** — not an over-reach, not a population swap, not a stretched conclusion.
3. **`source_hash` capture + re-verify.** The `source_hash` is computed and stored at verification time. On scheduled re-verify and on a lightweight periodic check, the source is re-fetched and compared; a changed or missing source moves the entry to `RETIRED` / `PENDING` and pulls it from shipping.
4. **Owner / Creative Director spot-audit.** The owner or Creative Director spot-audits a **small sample** of `VERIFIED` entries (not every entry) against ground truth.
5. **Second-source rule (conditional).** If `[[REQUIRE_SECOND_SOURCE_FOR_QUANTITATIVE]]` is set, any **quantitative** claim (a count, percentage, effect size, or other figure) additionally requires a **second corroborating source** before it may flip to `VERIFIED`.

When verifying, write the **locked sentence** as caption-ready, hedged, source+year named, and within the §2 wording rules; for any topic in `[[REQUIRED_FRAMING]]`, carry the mandated framing and flag it to the owner **before first use**. Record `source_url`, `source_hash`, and access date, then flip the status with a one-line change-summary note.

If a lead cannot be confirmed: mark it `RETIRED` with one line on what was wrong. **"Cannot verify" is a respected verdict** — it is a successful outcome of this protocol, not a failure of it.

> **Deterministic backstop at publish.** Independent of this protocol, the Policy Server enforces claim-grounding at `caption_compose` / publish (PRD §14.2): any caption containing a statistic, percentage, study year, or research verb must match a `VERIFIED` `locked_sentence` by a near-verbatim normalized comparison, and every numeric/percentage/year token must exactly equal that locked sentence's numbers — otherwise the publish is blocked. This makes numeric overclaims structurally impossible at the boundary; the §4 protocol is what fills the bank with safe entries in the first place.

## 5. Decay / re-verification rule

Re-verify every `VERIFIED` entry every `[[CLAIM_REVERIFY_MONTHS]]` months. Re-verification re-runs §4: re-fetch the source, recompute and compare `source_hash`, re-confirm semantics. An entry that fails re-verification is moved to `PENDING` or `RETIRED` and pulled from shipping the same day.

## 6. Push, not just pull

When `[[RESEARCH_POST_MIN_PER_WEEK]] > 0`, the Research & Verification Agent posts a weekly **research drop** on the editorial-calendar task: one `VERIFIED` entry plus a suggested angle that ties the finding to a concrete, everyday moment for `[[AUDIENCE_PERSONA]]`. This is how research-led content happens proactively instead of never. When `[[RESEARCH_POST_MIN_PER_WEEK]]` is `0`, the standing research slot and its enforcement are dropped; the Research & Verification Agent remains a constant role and still vets any factual claim or testimonial that arises (gated by the Brand Kit's citation requirement).

## 7. Locked entries (verified — caption-ready records)

> One full verification record per `VERIFIED` entry. Content agents may lift the locked sentence verbatim or tighten it within §2 — **never loosen it.** This section starts empty; the Research & Verification Agent appends a record each time a claim clears §4.

**Record template (one per `VERIFIED` entry):**

```
### <ID> — <short label>

- Locked sentence (<word count> words): <caption-ready, hedged, source+year named, within §2>
- Source: <author(s), year, title, venue, identifiers>
- source_url: <primary, allowlist-compliant URL>
- source_hash: <hash captured at verification>
- Accessed: <YYYY-MM-DD>
- Verification notes: <population, design, finding; which §4 gates passed; any clause
  intentionally dropped or wording corrected to match the source, and why; required-framing flag
  if the topic is in [[REQUIRED_FRAMING]]>
```

---

## 8. Schema reference (system of record)

Claims persist in the **system of record (Google Sheets / Google Drive)** — as the durable Claim Bank memory (PRD §8.1, §17). One row per claim.

| Column | Meaning |
|--------|---------|
| `id` | stable claim identifier |
| `brand_id` | owning brand (multi-brand deployments) |
| `status` | `PENDING` \| `VERIFIED` \| `RETIRED` |
| `locked_sentence` | caption-ready, hedged, source+year-named wording (the only text content agents may ship) |
| `source_url` | primary, allowlist-compliant source URL |
| `source_hash` | hash captured at verification; re-compared on re-verify and periodic checks |
| `accessed_at` | date the source was last fetched and confirmed |
| `reverify_at` | next re-verification due date (`accessed_at` + `[[CLAIM_REVERIFY_MONTHS]]` months) |

---

*Owner: Research & Verification Agent. Approver: brand owner. Sensitive/regulated claims escalate to the owner via the Managing Editor. This is a generic canon template; all brand values resolve from the Brand Kit at runtime.*
