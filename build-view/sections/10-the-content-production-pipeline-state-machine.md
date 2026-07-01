<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §10 (source lines 1026–1190). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 10. The content production pipeline (state machine)

### 10.1 Per-piece flow

```
[PLAN]            Managing Editor creates weekly slots (incl. language axis) → assigns owner agent per slot
   │
[IDEATE+DRAFT]    Content agent:
   │                1. read Content Ledger → write down what NOT to repeat
   │                2. choose the piece's LANGUAGE (§7.6)
   │                3. find the idea (angle lenses / offering seed-angles); research slot starts from a VERIFIED claim
   │                4. choose hook + shape + format within the active pack's rotation limits
   │                5. write caption (one idea, ≥1 concrete detail, image-first, length cap)
   │                6. write the visual brief (MESSAGE→FEELING→TREATMENT[+image,words,light_mood]) onto the Draft
   │                7. assemble draft doc (idea+ledger fields, caption, hashtags, visual_brief, ≤8-line compliance block)
   │
[LEDGER LINT]     Ops deterministic ledger-linter (§9.4): countable-rotation violations hard-block BEFORE CD
   │
[REVIEW]          Creative Director (child review task; draft is BLOCKED-BY it):
   │                Gate 0 Scroll Test + Gate 1 Compliance (incl. fail-closed safety fields, §15.1)
   │                verdict: approve | revise(≤2) | reject ;  round-3 → escalate Managing Editor
   │
[VISUALIZE]       Visual Production Agent (on approve):
   │                generate text-free image(s) (concept_led | product_led) → OCR text-free check (§11.2)
   │                → composite brand typography → channel-format → host (Drive) → author alt text → attach
   │
[CD RENDER PASS]  Creative Director post-render multimodal pass on the rendered artifact (§15.2 dim 3):
   │                quality bar + non-disclosure-in-image + "visibly different"; fail → back to Visual
   │
[QUEUE]           Publishing & Operations Agent:
   │                ledger audit (row + alt text present) → build handoff bundle → Approval Queue (system of record)
   │
[HUMAN GATE]      Owner approves/edits/rejects in Google Sheets (MVP) or the Review app (P5)
   │
[PUBLISH]         manual handoff by owner  OR  auto-publish (if enabled + adapter exists + gates pass) → Instagram (+ others)
   │
[RECORD]          append/confirm ledger row · append-only audit entry · archive · capture corrections for §15.3
```

**Stage ↔ status ↔ Task mapping + the closed legal-transition set (Day-5 SDD: a state machine is only buildable against a pinned transition set).** Three vocabularies coexist — pin the mapping:

| Stage(s) | `QueueItem.status` | `Task.status` |
|---|---|---|
| PLAN, IDEATE+DRAFT, LEDGER LINT | Draft | todo → in_progress |
| REVIEW, VISUALIZE, CD RENDER PASS | CD Review | in_review |
| QUEUE | Approval Queue | in_review (blocked-by human) |
| HUMAN GATE → Approve | Approved | in_progress |
| PUBLISH | Published | done |
| RECORD / reject / stale | Archived | done / cancelled |

**Legal transitions only** (else rejected + logged): `Draft→CD Review→{Approval Queue | Draft(revise) | Archived(reject)}`; `Approval Queue→{Approved | CD Review(Request changes) | Archived(Reject)}`; `Approved→{Published | CD Review(Request changes) | Archived(stale/reject)}`; `Published→Archived`. Human intent enters as an **Owner Action** value (§12.2) — `Approve` / `Request changes` / `Reject` / `Mark posted` — and the **orchestrator remains the sole writer of the derived `Status`**; the owner never writes `Status` directly. **"Request changes" routes back to CD Review under the same `piece_id`** (a new Draft attempt); **Reject Archives and records a killed idea** (§9.4). *(The mapping table above describes the **forward pass**; during an owner Request-changes with `route_to=content`, the Task re-enters the IDEATE+DRAFT / LEDGER LINT stages while `QueueItem.status` is held at `CD Review` (§12.5) — status is pinned by this legal-transition set, never derived from stage alone for that loop.)*


### 10.2 Key acceptance scenarios

```gherkin
Scenario: Standing-week production respects anti-repetition (deterministic)
  Given a brand with a configured standing week and a populated Content Ledger
  When a content agent drafts the next piece and the ledger-linter runs
  Then a draft repeating a hook within 3 posts, a back-to-back shape, an aphorism over the 1-in-5 cap,
       an idea re-run within 30 days, or a back-to-back visual-treatment label is hard-blocked before CD review
  And the draft includes its ledger fields and chosen language

Scenario: Creative Director rejects compliant-but-dead work
  Given a draft that passes every compliance checklist
  But repeats a hook shape seen in the last three posts and has no specific detail
  When the Creative Director reviews it
  Then the verdict is reject, naming the sameness and the missing specificity concretely

Scenario: A claim cannot ship unverified (deterministic + judge)
  Given a draft caption containing a statistic, percentage, study year, or research verb
  When the piece reaches caption_compose / publish
  Then the Policy Server structural gate requires a near-verbatim match to a VERIFIED locked_sentence
       and every numeric/percentage/year token to equal that locked_sentence's numbers, else BLOCK
  And the CD Gate-1 judge is a secondary catch

Scenario: Non-disclosure guardrail binds words and image
  Given the brand has a non_disclosure_rule about a proprietary mechanism
  When a caption (CD Gate 1) or a rendered image (CD post-render multimodal pass) would reveal it
  Then the piece is rejected; in auto mode the Policy Server also blocks at publish

Scenario: Safety field unconfirmed fails closed
  Given a relevant safety field (claims_forbidden / non_disclosure_rules / required_framing) is empty or owner-unconfirmed
  When a piece in that risk area reaches Gate 1 / the publish gate
  Then it is blocked and routed to a human (never treated as "nothing forbidden")

Scenario: Human approval gate, default mode
  Given approval_mode is "human"
  When a piece reaches the Approval Queue
  Then it is not published until the owner approves (in Sheets or the Review app)

Scenario: Optional auto-publish after trust (precedence + adapter-aware)
  Given auto_publish_enabled is true
  And approval_mode is "auto" (or "auto_after_trust" with the trust_threshold met)
  And the piece passed all gates
  When publishing runs
  Then it auto-publishes to configured channels that have a registered publish adapter
  And remaining configured channels are queued for manual handoff
  And the action is recorded in the append-only audit trail
```

### 10.3 Acceptance scenarios for blocker-grade behaviors

```gherkin
Scenario: Run-level cost circuit-breaker aborts a runaway run
  Given a run whose accumulated total tokens OR step count exceeds its configured cap
  When the cap is crossed mid-run
  Then the harness aborts the run and pauses the agent, and sets the affected piece `exception = Breaker-Paused` (§17)
  And the incident is logged; a per-call max_output_tokens truncation is NOT what fired

Scenario: OCR text-free check forces a regenerate
  Given a freshly generated pre-composite image
  When the deterministic Cloud Vision OCR detects baked glyphs
  Then the image is rejected and regenerated before any typography is composited

Scenario: Publish is idempotent under duplicate approval polling
  Given a piece already published once
  When the Sheets poller observes the Approved status again
  Then the publish-once guard keyed by piece_id prevents a second post

Scenario: A non-image URL is blocked at publish
  Given an asset URL that returns text/html (a Drive viewer page) instead of image bytes
  When the pre-publish byte-serving check runs
  Then publish is blocked until a raw image/* (HTTP 200) URL is provided

Scenario: Retiring a claim recalls every in-flight piece that depends on it
  Given a VERIFIED Claim-Bank entry is moved to RETIRED or PENDING (source_hash mismatch on re-fetch, or manual)
  When the re-verify / retirement check runs
  Then every non-Published piece whose Draft.claim_refs (§17) includes that entry is pulled back to IDEATE+DRAFT for re-grounding
  And an Approved-but-unpublished dependent is first removed from the Approval Queue (status → CD Review) before re-grounding
  And every already-Published dependent is flagged to the owner as a post-publication correction candidate (§14.3)
  And each recall is written to the append-only audit trail, naming the retired entry and the affected piece_id

Scenario: Secrets never enter model-visible context
  Given a prompt template referencing a secret placeholder
  When the resolver runs
  Then the secret resolves only into the tool/MCP auth layer (env/headers), never into prompt text

Scenario: One policy violation resets the auto-publish trust window
  Given approval_mode auto_after_trust accumulating toward trust_threshold
  When a single policy violation or reject occurs
  Then the trust window resets and auto-publish is not recommended
```

---

**Bounded recovery loops (Day-4 Denial-of-Wallet: bound every back-edge above the breaker).** The REVIEW loop is capped at revise≤2 then escalates (§15.1); the three other back-edges this pipeline is prone to are capped the same way so they cannot spin against the expensive **run-level** breaker (a backstop, never the primary control). Every loop is **harness-counted, never LLM-counted**:
- **IDEATE+DRAFT ↔ LEDGER LINT** — `Task.lint_attempts` (§17, default **2**); on exceed set `exception=Lint-Stuck` and escalate to the Managing Editor (§15.1) — a repeatedly-unlintable slot means a saturated ledger for the period, not another retry.
- **CD RENDER PASS → Visual** (the §10.1 `fail → back to Visual` edge) — `Task.cd_render_rounds` (§17, default **2**); round 3 escalates to the ME (mirrors revise).
- **VISUALIZE OCR-regenerate** (the §10.1 `OCR fail → regenerate` edge, §11.2) — `Task.render_attempts` (§17, default **3**); on exceed set `exception=Render-Stuck`, route to the owner with the verbatim OCR/CD evidence, and offer a **plain-template fallback** — never an unbounded regenerate.
- **Provider transient error** — at most `N` retries with backoff; any non-transient error or live 404 **stops and escalates** (§14.3) — never a silent model swap.

```gherkin
Scenario: A ledger-saturated slot escalates instead of looping forever
  Given a content agent's draft is hard-blocked by the ledger-linter
  When re-drafting reaches Task.lint_attempts (2) still blocked
  Then the piece is set exception=Lint-Stuck and escalates to the Managing Editor (§15.1), the blocking rule recorded

Scenario: A persistently text-baking image stops regenerating and asks for help
  Given the OCR text-free check keeps failing the regenerated image
  When regeneration reaches Task.render_attempts (3)
  Then the piece is set exception=Render-Stuck and routed to the owner with the verbatim OCR evidence and a plain-template fallback
```


