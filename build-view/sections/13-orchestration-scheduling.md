<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §13 (source lines 1734–1817). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 13. Orchestration & scheduling

### 13.1 Heartbeats & the weekly rhythm

Agents are woken by schedule and events. Canonical rhythm: **Monday** the Managing Editor creates the weekly editorial-calendar task and (if applicable) the Research agent posts its drop; **through the week** content agents draft into their slots and the CD reviews (pre- and post-render); **Friday** Ops posts the visibility digest; **monthly** the CD runs the retro.



**Timezone & date semantics (Day-1 economics — one cron, many brand-local clocks; Day-5 SDD determinism).** "Monday", "Friday", "within 3 posts", "30 days", `target_date`, and `LedgerRow.date` are all date-sensitive, but no clock is named — a single UTC cron would fire every brand's Monday wrong on multi-brand.
- **All day/window math uses the Brand Kit `timezone` (IANA).** Cloud Scheduler fires in UTC; the tick derives each brand's **local** day and runs that brand's Monday/Friday/monthly logic when it is that day **in the brand's tz** (DST handled by the zone).
- **`LedgerRow.date` is the brand-local ISO date**; the §9.4 linter's 3-post / 30-day / 1-in-5 windows and the §9.5 `target_date` staleness check evaluate in brand-local time.
- **One cron services all brands**; per-brand gating is by local time, not extra crons.

### 13.2 The default control loop + cost control

**Default control loop (no new infrastructure).** A single **Cloud Scheduler** cron fires a periodic orchestrator "tick" (the Managing Editor as orchestrator, an ADK workflow agent) that scans the Task store, dispatches ready tasks, and advances/clears `blocked_by` edges — i.e. R-ORCH-2 auto-wake = **poll-based graph advancement** (and, within a single ADK process, the in-process blocked-by wake of §13.3). The Task store lives in **Sheets/Drive** by default (entity in §17), DB as the pluggable alternative. Firestore / Pub-Sub are named **only as optional flagged upgrades** for true event-wake at scale.

**R-ORCH capability → concrete default primitive:**

| Capability | Default primitive |
|---|---|
| R-ORCH-1 scheduling/heartbeats | Cloud Scheduler cron → orchestrator tick |
| R-ORCH-2 task graph + blocked-by wake | Task entity in Sheets + poll-based graph advancement (in-process wake within one ADK process) |
| R-ORCH-3 shared docs | versioned CanonDocs in Sheets/Drive |
| R-ORCH-4 identity/permissions | ADK agent identities + Policy Server (§14.2) |
| R-ORCH-5 budgets/circuit-breaker | run-level token accumulator + iteration cap (below) |
| R-ORCH-6 observability | OpenTelemetry-style spans + the weekly digest |
| R-ORCH-7 human checkpoint | Sheets status gate / Review app + Vibe-Diff |

**Cost control (encodes the real incident).** The harness wrapping the ADK runner maintains a **per-run accumulator of total tokens** (input+output across **all** LLM calls in the run) **and** enforces a **hard per-run iteration/step cap**; if either is exceeded mid-run, the run is **aborted and the agent paused**, tied to per-agent (and per-`offering_id`) monthly budgets. A per-call `max_output_tokens` is a **separate baseline truncation cap — explicitly not the breaker.** *(This encodes the owner's ~631k-token runaway-loop lesson; Day-4 "Denial-of-Wallet"/observability is the conceptual umbrella. Trajectory/loop-drift detection is a future layer.)* Above ~80% of budget, only critical work proceeds.

**Sessions vs Memory (reconciliation).** (1) Each scoped run gets a **fresh session** — its working/conversation context starts clean. (2) "Durable Sessions" (Agent Engine) means each run's session is **reliably persisted for audit/replay**, *not* reused across runs — so "durable" and "fresh per run" do not conflict; the per-run session is persisted, **not** ephemeral. (3) The durable **cross-run** store holding the §8.1 Memory facts is **Sheets-keyed memory** (the `memory` namespace in the SoR); Agent Engine Memory Bank is a documented future upgrade, **not** a build dependency.

**Paused-by-default (optional cost mode).** Agents *may* run paused and be dispatched one run at a time, then re-paused — a purely **optional** cost-control mode (default deployments run normal schedules). The failure to avoid is a **silent, unobserved pause** (the canon retired first-piece self-pause; §9.5/§2.3): dispatch stays owner-driven and any paused routine **must surface in the weekly visibility digest** (§14.5).

**Crashed-run recovery & at-least-once safety (the poll loop's failure modes).** Poll dispatch (R-ORCH-2) is inherently *at-least-once* and cannot, by itself, tell a dead run from a working one.
- **Lease + heartbeat.** A dispatched Task stamps `Run.lease_until` (§17); the runner refreshes `Run.heartbeat_at` each step. A later tick that finds an in-progress Task whose `lease_until` has passed with a stale `heartbeat_at` declares the run **orphaned** (`Run.status=crashed`, `error_class=lease_expired`) and re-dispatches `attempt+1` with `parent_run_id` set. At the attempt cap it stops, sets the piece's `exception = Run-Failed` (§17), and raises a **CRITICAL/urgent** owner alert (§14.4.1) — the concrete detector behind §12.4's silent stall.
- **Idempotency on every expensive/external action.** The publish-once guard generalizes: `image_generate`, `caption_compose`, `drive_upload`, and `claim_bank_write` are keyed by `(piece_id, stage, attempt-input-hash)` — a **sub-scope of the canonical §12.2 published-registry**, not a separate scheme — so a re-dispatched or double-ticked Task never double-spends image budget or duplicates a ledger/claim row (Day-4 Denial-of-Wallet).
- **Partial-artifact cleanup on breaker abort.** Orphaned partials (a half-generated `Asset` with no `byte_url`, an in-progress Task) are **marked, not deleted**; "Unstick & resume" (§12.4) resumes from the last idempotency checkpoint, the aborted attempt's spend is retained for audit, and the accumulator resets.

```gherkin
Scenario: A crashed run is detected and safely re-dispatched
  Given a Task whose Run is in-progress but lease_until has passed with a stale heartbeat_at
  When the next orchestrator tick scans the Task store
  Then it marks the run crashed (error_class=lease_expired) and re-dispatches attempt+1 with parent_run_id set
  And on reaching the attempt cap it sets the piece exception=Run-Failed and raises an urgent owner alert instead of looping

Scenario: A double-dispatched expensive action does not double-spend
  Given two overlapping ticks dispatch the same VISUALIZE Task
  When image_generate is called twice for the same (piece_id, stage, attempt-input-hash)
  Then the idempotency guard returns the first result and no second image is generated or billed
```

**Dependency-graph safety (no silent permanent block).** Each tick validates the `blocked_by` graph it advances. A piece whose `blocked_by` contains an **archived/killed/never-completing** task, or any **cycle** (creatable by the §12.4 "Re-route handoff / send back a stage" intervention), would otherwise wait forever with no error. The tick detects both, sets the piece's `exception = Dep-Broken`, and routes it to the owner **naming the offending edge** — never aging into a silent stall.

```gherkin
Scenario: A re-route that creates a dependency cycle is caught, not silently stalled
  Given an owner re-routes a piece such that Task A is blocked_by B and B is blocked_by A
  When the next orchestrator tick validates the blocked_by graph
  Then the cycle is detected, the piece is given exception=Dep-Broken, and it is surfaced to the owner with the offending edge named
  And the same handling applies when a blocked_by points at an archived/killed task that can never complete
```


### 13.3 Inter-agent communication

- Default to a **single in-process ADK deployment** with in-process handoffs (parent/child tasks + blocked-by wake). Split agents into separate **A2A** services (with Agent Cards) **only where deployment genuinely requires it** — an optional enhancement per the simplicity guard.
- **The GOTO problem (stated correctly):** do **not** wrap an unbounded, collaborative agent as a bounded **MCP tool** — that injects unstructured control flow into the orchestrator, which is exactly why **A2A** exists as a separate agent-to-agent protocol. Reserve MCP for bounded tools; use A2A for agent reach.

- **A sample Agent Card (authored even though A2A is default-off) (Day 2).** So A2A is *shown, not merely named*, one card is authored at `specs/agent_cards/creative-director.json` — the CD is the natural first split (a stateless judge):
```yaml
# creative-director.agent-card (A2A) — illustrative
name: "Creative Director"
description: "Sole quality judge: Gate-0 Scroll Test + Gate-1 Compliance + post-render multimodal pass; returns a verdict, never edits."
url: "https://<deployment>/a2a/creative-director"
skills: [ "review-draft", "render-pass" ]
input_modes:  [ "application/json" ]
output_modes: [ "application/json" ]   # verdict: approve|revise|reject + notes
auth: { scheme: "oauth2", scopes: [ "read:draft", "write:review" ] }
```
Reserve this for a genuine deployment split (the simplicity guard, §6.3); in the default single ADK process the role is an in-process handoff — but the card exists so the capability is **demonstrable, not theoretical** (registered in Appendix D).

---

