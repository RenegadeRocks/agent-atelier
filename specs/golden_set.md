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
  idea_sentence: "The steel tumbler and dabarah on a Church Street drizzle morning."
  hook: "The Church Street drizzle"
  shape: "observation->turn"
  caption: "The Church Street drizzle hits different with a steel tumbler. We roast it light so the jaggery notes cut through the damp air. No espresso machine required. DM us 'FRESH' to try this month's roast."
  hashtags: ["#kanvacoffee", "#bengaluru"]
  visual_brief: { message: "The quiet morning moment", feeling: "let in — like a friend at the roastery just handed you a cup", treatment: "premium, alive", image: "A close up of a steel tumbler and dabarah on a windowsill with rain outside.", words: "none", light_mood: "natural", check: "scrim behind every line" }
  rendered_ref: null
  alt_text: "A steel tumbler and dabarah on a windowsill in the rain."
  compliance_block: { claims_used: [], non_disclosure_ok: true, political: false, comparative: false }
owner_label: { decision: approve, expected_cd: approve, gate: null, source: corrections_log, decided_at: 2026-07-01 }
rationale: "Passes Gate 0 (one idea, concrete detail, image carries it, visibly different) and Gate 1. Authentic representation of the brand's desired_feeling."
version: { added_in: v2, status: active }
```

### gs-002 — positive — shutter moment
```yaml
id: gs-002
kind: positive
artifact:
  channel: instagram
  offering_id: null
  idea_sentence: "The 96 hour window between roasting and brewing."
  hook: "Roasted Tuesday."
  shape: "observation->meaning"
  caption: "Roasted Tuesday. At your door by Saturday. That's the whole trick. The 96 hours matter more than the origin label. DM us 'FRESH' to try this month's roast."
  hashtags: ["#kanvacoffee", "#freshroast"]
  visual_brief: { message: "Freshness focus", feeling: "let in — like a friend at the roastery just handed you a cup", treatment: "premium", image: "A hand holding a fresh bag of coffee with the Tuesday roast log handwritten on it.", words: "none", light_mood: "soft", check: "no leak" }
  rendered_ref: null
  alt_text: "A fresh bag of Kanva coffee with a handwritten Tuesday roast date."
  compliance_block: { claims_used: [], non_disclosure_ok: true, political: false, comparative: false }
owner_label: { decision: approve, expected_cd: approve, gate: null, source: corrections_log, decided_at: 2026-07-02 }
rationale: "Great use of local detail bank. Evokes the exact brand vibe without feeling like an ad."
version: { added_in: v2, status: active }
```

### gs-003 — positive — roastery workshop
```yaml
id: gs-003
kind: positive
artifact:
  channel: instagram
  offering_id: "roastery_subscription"
  idea_sentence: "First Crack Sundays hands-on brewing workshop."
  hook: "The first crack pops"
  shape: "story->invite"
  caption: "The first crack sounds like popcorn and smells like burnt sugar. Come learn how to hear it. Join our 3-hour hands-on brewing workshop at the roastery, the last Sunday of every month. DM us for a seat."
  hashtags: ["#kanvacoffee", "#roastery"]
  visual_brief: { message: "Hands-on learning", feeling: "let in — like a friend at the roastery just handed you a cup", treatment: "warm, inviting", image: "A small group of people bathed in warm amber roastery light, leaning in close to the roasting drum, looking captivated as they listen for the first pop.", words: "none", light_mood: "warm", check: "no text" }
  rendered_ref: null
  alt_text: "People gathered at a coffee roastery workshop."
  compliance_block: { claims_used: [], non_disclosure_ok: true, political: false, comparative: false }
owner_label: { decision: approve, expected_cd: approve, gate: null, source: corrections_log, decided_at: 2026-07-03 }
rationale: "Directly promotes the flagship offering while maintaining the warm, inviting tone. Good hook and clear CTA."
version: { added_in: v2, status: active }
```

### gs-004 — NEGATIVE — tattered-log hygiene REJECT
```yaml
id: gs-004
kind: negative
artifact:
  channel: instagram
  offering_id: "roastery_subscription"
  idea_sentence: "The Tuesday roast log, handwritten."
  hook: "The Tuesday roast log"
  shape: "observation->turn"
  caption: "The Tuesday roast log, handwritten. Every batch recorded by hand. Join our next First Crack Sunday workshop."
  hashtags: ["#kanvacoffee", "#roastery"]
  visual_brief: { message: "The handwritten roast log.", feeling: "authentic", treatment: "close-up on the paper", image: "A close up of a handwritten logbook with dark coffee stains and tattered edges.", words: "none", light_mood: "warm", check: "no text" }
  rendered_ref: null
  alt_text: "A coffee-stained, tattered handwritten roast logbook."
  compliance_block: { claims_used: [], non_disclosure_ok: true, political: false, comparative: false }
owner_label: { decision: reject, expected_cd: reject, gate: render_pass, source: corrections_log, decided_at: 2026-07-05 }
rationale: "stains and tatter are a hygiene signal for an F&B brand; wrong desired_feeling"
version: { added_in: v2, status: active }
```

### gs-005 — NEGATIVE — split-collage REJECT
```yaml
id: gs-005
kind: negative
artifact:
  channel: instagram
  offering_id: "roastery_subscription"
  idea_sentence: "Different ways to brew your coffee at home."
  hook: "Brew it your way"
  shape: "list->cta"
  caption: "Brew it your way. From pour-over to french press, we have the beans for you. Get your subscription today."
  hashtags: ["#kanvacoffee", "#brewathome"]
  visual_brief: { message: "multiple brewing methods", feeling: "informative", treatment: "split-screen collage", image: "A split-screen collage showing four different coffee brewing methods.", words: "none", light_mood: "bright", check: "FAILS: split collage" }
  rendered_ref: null
  alt_text: "A collage of four different coffee brewing methods."
  compliance_block: { claims_used: [], non_disclosure_ok: true, political: false, comparative: false }
owner_label: { decision: reject, expected_cd: reject, gate: render_pass, source: corrections_log, decided_at: 2026-07-06 }
rationale: "split-collage layouts feel like an ad, not a moment; visibly breaks the 'real human moment' constraint"
version: { added_in: v2, status: active }
```

### gs-006 — NEGATIVE — input-directive-on-image REJECT
```yaml
id: gs-006
kind: negative
artifact:
  channel: instagram
  offering_id: null
  idea_sentence: "A relaxing afternoon with a cup of coffee."
  hook: "Afternoon pause"
  shape: "observation->meaning"
  caption: "Afternoon pause. Take a moment for yourself. The perfect time for a fresh brew."
  hashtags: ["#kanvacoffee", "#afternoon"]
  visual_brief: { message: "relaxing afternoon", feeling: "calm", treatment: "premium", image: "A cup of coffee on a table with a book. The image contains large text that literally says 'insert text here'.", words: "model-baked, NOT composited", light_mood: "soft", check: "FAILS: text directive" }
  rendered_ref: null
  alt_text: "A cup of coffee with text saying insert text here."
  compliance_block: { claims_used: [], non_disclosure_ok: true, political: false, comparative: false }
owner_label: { decision: reject, expected_cd: reject, gate: render_pass, source: corrections_log, decided_at: 2026-07-06 }
rationale: "input-directive-on-image; generated the literal prompt words 'insert text here' instead of the hook"
version: { added_in: v2, status: active }
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
