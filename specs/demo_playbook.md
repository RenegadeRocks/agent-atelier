# Demo Playbook — the ≤5-minute video + how to demo fast

> **The single most important fact (§21.3): the demo is a RECORDED ≤5-min YouTube video +
> the public repo README ("a stranger must be able to run the full system end to end" —
> the accepted live-demo substitute).** Nothing is demoed live to judges. So the studio's
> weekly rhythm never has to be waited out — it is *simulated on a controlled clock and
> recorded in segments as the build passes each gate.* This file is the authored plan for
> that: the demo-mode mechanics the build must include, the seeding, the shot list, and
> the capture discipline. Owner: the human. Consumed at P1-B onward; central at P3/P5.

---

## 1. Demo mode — three mechanics the build includes from day one

None of these is a new subsystem; each is already implied by the PRD and doubles as test
infrastructure. Build them as such:

1. **The injectable logical clock (`--as-of <datetime>` on the orchestrator tick).**
   P3's VERIFY literally requires "run a simulated week", and every §13.1 rule (Monday
   tick, Friday digest, 30-day windows, `target_date` staleness, brand-local tz math) is a
   pure function of "now" — so the tick and the linter take an injected `now` instead of
   reading the wall clock (wall clock is just the default). **This is demo mode.** A shell
   loop that fires the tick with `--as-of` Mon 09:00, Tue 10:00 … Fri 16:00 compresses a
   week into ~2 minutes, with real drafts, real lint bounces, a real digest.
2. **`environment=preview` is the demo sandbox.** Policy already blocks
   `instagram_publish`/`notify` there — simulate freely, nothing escapes. The finale
   publish runs in `production` against the **test Instagram account** (a dedicated
   Business/Creator account for the demo brand — never a real brand's handle).
3. **Seeding scripts (fixtures, not hacks).** A `demo/seed/` step that loads: (a) a
   2-week **ledger history** so rotation rules have something to fire against; (b) 3–4
   queued pieces with **pre-generated, pre-composited images** (so the queue/Review-app
   shots have no dead air); (c) one **planted rotation-violating draft** (P3's VERIFY
   needs it anyway) and one **planted ungrounded-claim caption** (P4-A's). Seeds are
   fixtures the tests also use — write once, use twice.

**Latency honesty:** image generation is the only slow live step (~10–60s). Show it live
ONCE (it's impressive once), pre-generate everything else.

## 2. The 5-minute video arc (mirrors §21.2's own demo section)

| # | ~sec | Shot | The point it scores |
|---|------|------|---------------------|
| 1 | 20 | Cold open: the Sheets queue / Studio Floor with a seeded week of finished pieces | "this thing ships real content" |
| 2 | 50 | **Onboard the demo brand live** (intake interview montage: source-ingest → safety elicitation → first-light showing BOTH probe artifacts — the safe post AND the blocked near-miss) | Brand Kit in; fail-closed safety; the G3 interview |
| 3 | 60 | **One piece end-to-end, live:** on-demand ask → ME delegates → draft (ledger-first) → linter pass → CD Gate-0/1 verdict → image generated live → typography composited → lands in queue | multi-agent + MCP + the pipeline; "a real tool-call in the demo" (§21.2) |
| 4 | 45 | **Fast-forward a week** (`--as-of` loop): slots fill, the planted violator **bounces at the linter** with the rule named, Friday digest posts | determinism; the anti-slop machinery visibly working |
| 5 | 45 | **Governance money-shots:** unconfirmed safety field → publish BLOCKED; the ungrounded claim → BLOCKED at compose; approve one piece → manual **Post Kit** export; (if wired) one real auto-publish to the test IG account, idempotency guard shown | Day-4 security; fail-closed; act-tier HITL |
| 6 | 30 | **The G1 finale:** the AOL feed and the demo-brand feed **side by side — same code, zero changes, two brands** | the core promise: studio constant, brand = config |
| 7 | 15 | The harness behind it: contracts, deviation log, CI drift-guard — one screen, one sentence | §21.2 §4, BUNNY credibility |

Under 5:00 with cuts. Record with voiceover last; capture raw segments first.

## 3. Capture-as-you-build (the discipline that makes the video cheap)

Every contract's VERIFY step already says "capture the run" (§18.4.5 evidence). **Record
those captures as screen video, not just logs** — each gate's evidence IS a video segment:
P1-B's end-to-end run = shot 3's raw material; P2-B's first-light = shot 2; P3's simulated
week + linter bounce = shot 4; P4-A's blocked scenarios = shot 5; P6/P2-A's two-brand run =
shot 6. By P5-A you have every segment and only record the connective tissue. **Do not
leave the video for July 6.**

## 4. The demo brand (input quality = output quality)

The second brand is **fictional-but-realistic** — modeled on real Indian D2C patterns but
with an invented identity (`demo/brand-packs/`). NOT a cloned real brand: publishing to a
real brand's identity or using its marks in a public competition video is a legal and
ethical foot-gun, and judges may recognize it. Fictional + dense beats real + risky.

Richness bar (what actually drives output quality — mirror the AOL kit's density):
- a **real-sounding founder story + mission** (feeds S2/P4 hooks);
- **2 offerings** with accurate one-liners + funnel relationship;
- **voice sample lines, good AND bad** (the judge calibrates on these);
- **genuine safety constraints** (coffee/wellness health-claim traps — great first-light
  material: "antioxidants cure X" is a perfect blocked-probe);
- a **local detail bank** with ≥10 concrete sensory anchors (the specificity rule feeds
  on this — it is the single highest-leverage input field);
- palette/fonts/register + a `product_led`-appropriate visual strategy.
The pack ships as **intake INPUTS** (source doc + owner answer sheet), so the video shows
the Strategist building the kit — not a pre-filled kit appearing by magic. A pre-validated
kit sits alongside as fallback if the live interview segment fights the clock.

## 5. Pre-flight checklist (owner, before recording)

- [ ] **REQUIRED, do first:** GCP project — Sheets/Drive APIs on, service account shared
      to the demo sheet, Gemini + image-model keys in the vault (P1-B needs all of this).
      `python3 tools/build_view_split.py --verify` green.
- [ ] **OPTIONAL (auto-publish finale only):** a test Instagram Business/Creator account +
      content-publishing API access. The manual Post Kit + mark-as-posted path needs NO
      API account and is fully submission-worthy on its own — P5-A's ON-FAIL names manual
      handoff as the unaffected default. Skip this under deadline pressure.
- [ ] `demo/seed/` loaded; images pre-generated; one planted violator + one planted
      ungrounded claim in place.
- [ ] AOL kit + demo-brand kit both validate; both feeds seeded for the side-by-side.
- [ ] Screen-record every VERIFY capture from P1-B onward (shot list above).
