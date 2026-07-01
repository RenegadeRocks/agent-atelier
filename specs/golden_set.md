# Golden Set — [[BRAND_NAME]] content studio

The frozen, versioned evaluation corpus the **Creative Director (CD)** judge is checked against (§15.1, §15.3) and the deterministic **CI evaluation gate** scores against (§18.2 step 4). It exists to make one thing measurable: **does the judge agree with the owner, and how often does it false-approve?**

This is *not* the live runtime review (which stays holistic, §15.1). This is the offline, pinned regression corpus. It includes **negative/failure exemplars** so a judge that rubber-stamps everything visibly fails here.

> **Stored as a frozen CanonDoc.** The golden set is a `CanonDoc` (§17, `key: golden_set`) — `body_template` holds the entries below, `version` is bumped on every change, and it is treated like any other versioned canon: append-only history, owner-signed amendments. It is **labeled from owner decisions** (Approve / Edit / Reject), never from the CD's own verdicts — this breaks the `[[SAMPLE_LINES_GOOD]]`-only circularity that would let the judge grade its own homework.

---

## 1. Entry schema

Each entry is one record. Storage: a row in the `golden_set` CanonDoc body (Sheets/Drive default, §17), serializable as the YAML below.

```yaml
GoldenEntry:
  id:           string        # stable, immutable. Format: gs-<NNN> (e.g. gs-001). Never reused after retirement.
  kind:         enum          # positive | negative
  artifact:     object        # the thing being judged (see §1.1)
  owner_label:  object        # ground-truth label from a real owner decision (see §1.2)
  rationale:    string        # WHY this label — the teachable reason, in plain language; cites the failing/passing clause
  version:      object        # provenance + freeze metadata (see §1.3)
```

### 1.1 `artifact` — what the judge sees

The artifact mirrors a real `Draft` + `Asset` so the CD scores it exactly as it would a live piece (§15.2 dims 1–7). Minimum fields:

```yaml
artifact:
  draft_id_ref:   string?      # optional pointer to the originating Draft if mined from production
  channel:        enum         # one of [[CHANNELS]] (e.g. instagram | facebook)
  offering_id:    string?      # one of [[OFFERINGS]] ids, or null for evergreen
  idea_sentence:  string       # the one-idea sentence (Gate-0 rule)
  hook:           string
  shape:          string       # hook/shape pack id from creative_engine
  caption:        string       # full caption as it would publish
  hashtags:       [string]
  visual_brief:   { message, feeling, treatment, image, words, light_mood, check }
  rendered_ref:   string?      # Drive URL of the actual rendered artifact, for the multimodal post-render pass
  alt_text:       string?      # present if the entry exercises the QUEUE alt-text check
  compliance_block:            # the safety fields the artifact asserts (fail-closed if missing, §14.2)
    claims_used:        [string]
    non_disclosure_ok:  bool
    political:          bool
    comparative:        bool
```

> A **negative** artifact is stored *as authored* — the violation is left in, not redacted. The whole point is that the judge must catch it. Where a negative reproduces brand-voice failure, draw it generically from `[[SAMPLE_LINES_BAD]]` (do not invent a new failure taxonomy).

### 1.2 `owner_label` — ground truth

```yaml
owner_label:
  decision:     enum          # approve | edit | reject     (the real owner action; "edit" counts as not-clean-approve)
  expected_cd:  enum          # approve | revise | reject    (what a correctly-calibrated CD SHOULD have returned)
  gate:         enum?         # which gate should fire on a negative: gate0 | gate1 | render_pass  (null for positives)
  source:       enum          # owner_decision | corrections_log | seed   (provenance of the label)
  decided_at:   date
```

The scored quantity is **agreement between `expected_cd` and the CD's actual verdict**, plus the **false-approve** event (CD says `approve` when `owner_label.decision` is `reject`). See §4.

### 1.3 `version` — freeze provenance

```yaml
version:
  added_in:     string        # golden_set CanonDoc version this entry first appeared in (e.g. v3)
  status:       enum          # active | retired
  retired_in:   string?       # version where retired (entry kept for history; never scored once retired)
  hash:         string        # content hash of {artifact + owner_label}, set at freeze; mismatch = tampering, fail CI
```

---

## 2. Seed exemplars

Six seed entries (`source: seed`), product-neutral, drawn generically. They establish the floor; production mining (§3) grows the set. Brand-specific values appear only as registry tokens.

### gs-001 — positive — clean evergreen approve
```yaml
id: gs-001
kind: positive
artifact:
  channel: instagram
  offering_id: null
  idea_sentence: "One concrete moment from [[LOCAL_DETAIL_BANK]], reframed so the reader sees their own day in it."
  hook: "<a line in the [[VOICE_DESCRIPTORS]] register, drawn from the spirit of [[SAMPLE_LINES_GOOD]]>"
  shape: "observation->turn"
  caption: "<image-first caption; one idea; ≥1 concrete detail; reading level [[READING_LEVEL]]; CTA in [[CTA_STYLE]]>"
  hashtags: ["<on-brand, non-spammy>"]
  visual_brief: { message: "the one idea", feeling: "warm/true", treatment: "premium, alive", image: "concept legible alone", words: "composited brand type", light_mood: "natural", check: "scrim behind every line" }
  alt_text: "<present, descriptive>"
  compliance_block: { claims_used: [], non_disclosure_ok: true, political: false, comparative: false }
owner_label: { decision: approve, expected_cd: approve, gate: null, source: seed, decided_at: 2026-01-15 }
rationale: "Passes Gate 0 (one idea, concrete detail, image carries it, visibly different) and Gate 1 (voice, channel, no claims). The baseline 'alive and compliant' approve."
version: { added_in: v1, status: active, hash: "<set-at-freeze>" }
```

### gs-002 — positive — VERIFIED-claim piece, grounded
```yaml
id: gs-002
kind: positive
artifact:
  channel: instagram
  offering_id: "[[OFFERING_ID]]"
  idea_sentence: "A single VERIFIED research finding, stated in its locked wording, tied to one everyday benefit."
  hook: "<curiosity hook, not fear/guilt>"
  shape: "claim->meaning"
  caption: "<contains exactly the locked_sentence numbers; CTA [[CTA_STYLE]]; uses [[CONTACT_WHATSAPP]] / [[CONTACT_INSTAGRAM]] per CTA bank>"
  hashtags: ["<topical>"]
  visual_brief: { message: "the finding made human", feeling: "calm credibility", treatment: "premium", image: "metaphor, not a chart", words: "composited", light_mood: "soft", check: "no leak" }
  alt_text: "<present>"
  compliance_block: { claims_used: ["claimbank:VERIFIED:<id>"], non_disclosure_ok: true, political: false, comparative: false }
owner_label: { decision: approve, expected_cd: approve, gate: null, source: seed, decided_at: 2026-01-16 }
rationale: "Every number matches the VERIFIED locked_sentence (§11 claim-grounding), within [[CLAIMS_ALLOWED]], second-source rule honored where [[REQUIRE_SECOND_SOURCE_FOR_QUANTITATIVE]] applies. Correct positive for the grounding path."
version: { added_in: v1, status: active, hash: "<set-at-freeze>" }
```

### gs-003 — NEGATIVE — compliant-but-dead (the headline failure mode)
```yaml
id: gs-003
kind: negative
artifact:
  channel: instagram
  offering_id: null
  idea_sentence: "<generic 'topic, not an idea' — e.g. a vague nod to wellbeing with no concrete detail>"
  hook: "<a flat, templated opener with no specificity — the kind that reads like every other post>"
  shape: "list->cta"
  caption: "<every compliance box green, but no concrete detail from [[LOCAL_DETAIL_BANK]], a hook shape reused from recent posts, the image a generic stock-feeling scene; lifeless. Drawn from the spirit of [[SAMPLE_LINES_BAD]].>"
  hashtags: ["<generic>"]
  visual_brief: { message: "(none — a topic)", feeling: "vague/pleasant", treatment: "house-style default", image: "pretty but says nothing", words: "composited", light_mood: "flat", check: "technically valid" }
  alt_text: "<present>"
  compliance_block: { claims_used: [], non_disclosure_ok: true, political: false, comparative: false }
owner_label: { decision: reject, expected_cd: reject, gate: gate0, source: seed, decided_at: 2026-01-17 }
rationale: "Passes EVERY compliance check and still fails. No single idea, no concrete detail, reused skeleton, lifeless image. This is the entry that catches a judge which only runs Gate 1. Compliant-but-dead is a REJECT (§15.1)."
version: { added_in: v1, status: active, hash: "<set-at-freeze>" }
```

### gs-004 — NEGATIVE — over-claim / ungrounded statistic
```yaml
id: gs-004
kind: negative
artifact:
  channel: instagram
  offering_id: "[[OFFERING_ID]]"
  idea_sentence: "A benefit dressed up with a percentage that has no VERIFIED Claim-Bank backing."
  hook: "<'Studies show…' / a curative or guaranteed-outcome promise — a [[CLAIMS_FORBIDDEN]] structure>"
  shape: "claim->cta"
  caption: "<states a statistic / 'research shows' / a study year that does NOT match any VERIFIED locked_sentence; or makes a curative/guaranteed claim. Generic over-reach in the spirit of [[SAMPLE_LINES_BAD]].>"
  hashtags: ["<topical>"]
  visual_brief: { message: "the inflated promise", feeling: "urgency", treatment: "premium", image: "ok", words: "composited", light_mood: "bright", check: "n/a" }
  alt_text: "<present>"
  compliance_block: { claims_used: ["UNVERIFIED/none"], non_disclosure_ok: true, political: false, comparative: false }
owner_label: { decision: reject, expected_cd: reject, gate: gate1, source: seed, decided_at: 2026-01-18 }
rationale: "Trips deterministic claim-grounding (§11): a research verb / number / study year with no near-verbatim VERIFIED match, and/or a [[CLAIMS_FORBIDDEN]] curative-or-guarantee structure. Must BLOCK at Gate 1. Catches a judge that lets a confident number through unchecked."
version: { added_in: v1, status: active, hash: "<set-at-freeze>" }
```

### gs-005 — NEGATIVE — non-disclosure leak (words AND scene)
```yaml
id: gs-005
kind: negative
artifact:
  channel: instagram
  offering_id: "[[OFFERING_ID]]"
  idea_sentence: "A piece that names or visually depicts a mechanism covered by [[NON_DISCLOSURE_RULES]]."
  hook: "<reads fine on the surface>"
  shape: "story->invite"
  caption: "<the caption text names a non-disclosed mechanism / proprietary detail covered by [[NON_DISCLOSURE_RULES]] — a wording leak>"
  hashtags: ["<topical>"]
  visual_brief: { message: "experience", feeling: "intimate", treatment: "premium", image: "the SCENE depicts the non-disclosed mechanism even if the caption were clean — a scene leak", words: "composited", light_mood: "warm", check: "FAILS: leak in scene" }
  rendered_ref: "<Drive URL — exercises the post-render multimodal pass>"
  alt_text: "<present>"
  compliance_block: { claims_used: [], non_disclosure_ok: false, political: false, comparative: false }
owner_label: { decision: reject, expected_cd: reject, gate: render_pass, source: seed, decided_at: 2026-01-19 }
rationale: "Binds BOTH the words check (Gate 1) and the scene check (post-render multimodal pass, §15.2 dim 3). A judge that only reads the caption misses the scene leak; this entry forces both. [[NON_DISCLOSURE_RULES]] violation = reject."
version: { added_in: v1, status: active, hash: "<set-at-freeze>" }
```

### gs-006 — NEGATIVE — AI-slop / AI-sameness tell
```yaml
id: gs-006
kind: negative
artifact:
  channel: instagram
  offering_id: null
  idea_sentence: "A piece that is the fourth identical skeleton, or carries visible AI-slop tells."
  hook: "<a hook shape seen in the last three posts>"
  shape: "(same skeleton as recent posts)"
  caption: "<em-dash-stuffed, 'in today's fast-paced world', list-of-three padding, model-baked subtitle text instead of composited brand type — generic AI tells in the spirit of [[SAMPLE_LINES_BAD]]>"
  hashtags: ["<generic>"]
  visual_brief: { message: "repeat of recent post", feeling: "same as last", treatment: "feed drifting to one look", image: "plastic skin / warped hands / baked subtitles — AI-slop tells", words: "model-baked, NOT composited", light_mood: "uncanny", check: "FAILS slop + sameness" }
  rendered_ref: "<Drive URL>"
  alt_text: "<present>"
  compliance_block: { claims_used: [], non_disclosure_ok: true, political: false, comparative: false }
owner_label: { decision: reject, expected_cd: reject, gate: gate0, source: seed, decided_at: 2026-01-20 }
rationale: "Two distinct tells: AI-slop (render artifacts, baked subtitles) and AI-sameness (the fourth identical skeleton / feed collapsing to one look, §6 variety principle). Catches a judge blind to repetition reaching a human (§3.3 north-star 0)."
version: { added_in: v1, status: active, hash: "<set-at-freeze>" }
```

> **Seed balance.** 2 positive / 4 negative is intentional: a corpus weighted toward failures stresses the false-approve metric, which is the one that gates trust (§12.3, §15.3). As production mining adds entries, keep negatives at **≥ 40%** of the active set.

---

## 3. Growing the set (production mining)

New entries come from the **corrections log** (§14.5, §15.3) — every owner Approve / Edit / Reject is a labeling event:

- **Reject** → candidate `negative` (`expected_cd: reject`), with the owner's reason as `rationale`.
- **Edit** → candidate `negative` (`expected_cd: revise`); a clean piece would not have been edited.
- **Approve** (unedited) → candidate `positive` (`expected_cd: approve`).

Candidates are reviewed at the **monthly retro** and admitted by owner sign-off only. Bias admission toward edited / escalated / auto-published pieces (the same bias the §15.3 audit uses) — those are where the judge is most likely wrong. Never auto-admit; never label an entry from the CD's own verdict.

---

## 4. CI pass threshold + tolerance (referenced by §18.2 step 4)

The CI evaluation gate is **deterministic**: pin the judge model version (the **Gemini 3 Pro** editorial/judge tier; operational alias `gemini-flash-latest`; image-capable entries use the Gemini-native `gemini_image_pro` / Nano Banana Pro for the render-pass artifact — **confirm exact model names/IDs against live docs at build time, §14.3 / §18.1**), pin the rubric prompt, run at **temperature 0**, and score the **active** golden set (retired entries excluded).

**Computed metrics** over the active set:

| Metric | Definition |
|---|---|
| `agreement_rate` | fraction where CD verdict == `owner_label.expected_cd` (a `revise`↔`reject` mismatch on a negative still counts as a *catch*; see §4.1) |
| `false_approve_count` | count where CD == `approve` but `owner_label.decision == reject` |
| `negative_catch_rate` | fraction of `kind: negative` entries the CD did **not** approve |

**Pass conditions — ALL must hold:**

```yaml
ci_pass:
  agreement_rate:        ">= 0.90"   # documented threshold
  agreement_tolerance:   0.03        # a run within tolerance below threshold is a SOFT-FAIL (warn, not block) — see §4.1
  false_approve_count:   "== 0"      # HARD: a single false-approve on a negative blocks the build
  negative_catch_rate:   "== 1.00"   # HARD: every negative must be caught
```

### 4.1 How the threshold + tolerance behave

- **`false_approve_count == 0`** and **`negative_catch_rate == 1.00`** are **hard gates** — non-negotiable, no tolerance. Letting a known over-claim or non-disclosure leak through is a release blocker (this is the whole reason the negatives exist).
- **`agreement_rate`** carries the **tolerance band**: `>= 0.90` passes; `0.87–0.90` (within the `0.03` tolerance) is a **soft-fail** — CI emits a warning and records it for the retro but does **not** block, absorbing judge non-determinism at the margins; `< 0.87` **blocks**. A `revise`-vs-`reject` disagreement on a negative is treated as agreement for `negative_catch_rate` (the piece was caught) but as a miss for `agreement_rate` (the judge mis-rated severity) — this is what the tolerance band is for.
- **The holistic CD craft verdict is advisory in CI, not a hard gate** (§18.2 step 4). The live runtime CD review stays holistic (§15.1); CI only checks the pinned, deterministic regression behavior above.
- **Hash check.** Before scoring, recompute each active entry's `version.hash`. Any mismatch = the frozen corpus was tampered with out-of-band → **hard-fail** the gate.

---

## 5. Freeze / version rule

The golden set is **frozen and versioned**, treated exactly like a versioned CanonDoc (§15.3, §17).

1. **Immutable once frozen.** An admitted entry's `artifact` + `owner_label` never change. Bad entries are **retired** (`status: retired`, set `retired_in`), never edited or deleted — history is append-only.
2. **Version bump on every change.** Any admission or retirement increments the `golden_set` CanonDoc `version` (v1 → v2 → …). `added_in` / `retired_in` pin each entry to a version.
3. **CI pins a version.** Each CI run records the golden-set version it scored. A threshold/tolerance change in §4 is itself a versioned, owner-signed amendment — the gate cannot be silently loosened.
4. **Owner-signed amendments only.** Admissions, retirements, and threshold changes are §14.4 high-stakes actions: owner sign-off required, logged to the append-only audit (§17 `AuditEntry`). The CD never amends its own grading corpus.
5. **Labels come from owner decisions, not CD verdicts** (§1, §3) — the structural guarantee that the judge is never grading against its own past output.

---

*Source of truth: PRD §15.1 / §15.3 / §18.2 step 4 / §17. Confirm model names/IDs and API limits at build time (§14.3). Brand-specific values appear only as `[[REGISTRY_TOKENS]]`, resolved per `resolver.md`.*
