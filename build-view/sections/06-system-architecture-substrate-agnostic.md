<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §6 (source lines 160–232). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 6. System architecture (substrate-agnostic) + recommended stack

### 6.1 Logical components

```
┌────────────────────────────────────────────────────────────────────┐
│                         AGENT ATELIER STUDIO                         │
│                                                                      │
│  ┌──────────────┐   ┌───────────────────┐   ┌────────────────────┐  │
│  │  Brand Kit   │   │  Canon / Engine   │   │  Agent Company     │  │
│  │  + Onboarding│──▶│  Docs (harness    │──▶│  (8 roles incl.    │  │
│  │  (config)    │   │  static+dynamic)  │   │  intake)           │  │
│  └──────────────┘   └───────────────────┘   └─────────┬──────────┘  │
│                                                        │             │
│  ┌──────────────────────────────────────────────────┐ │            │
│  │  Orchestration layer (minimal)                    │◀┘            │
│  │  scheduler/heartbeats · task graph · run budgets  │              │
│  │  · cost circuit-breaker · observability/audit     │              │
│  └───────────────┬──────────────────────────────────┘              │
│                  │                                                   │
│  ┌───────────────▼─────────┐   ┌─────────────────────────────────┐  │
│  │  Production pipeline     │   │  Tool layer (MCP)               │  │
│  │  idea→draft→lint→review→ │   │  image-gen · caption-composer · │  │
│  │  visual→CD render-pass→  │   │  Drive · Sheets · web-research ·│  │
│  │  queue→approve→publish   │   │  Instagram publish              │  │
│  └───────────────┬─────────┘   └─────────────────────────────────┘  │
│                  │                                                   │
│  ┌───────────────▼─────────────────────────────────────────────┐    │
│  │  Approval & System-of-Record                                 │    │
│  │  Google Sheets/Drive (MVP gate + record) + Review app (P5)   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────┘
```

*The **Studio Floor UI** (§12.4) is the live operator console layered over the Approval & System-of-Record box and the production pipeline — the visible, interactive view of the agent company (Phase 5).*

### 6.2 Substrate-agnostic orchestration requirements

The system needs an orchestration substrate that provides — however implemented:

- **R-ORCH-1 Scheduling / heartbeats.** Wake agents on a cadence and on events.
- **R-ORCH-2 Task graph.** Durable units of work ("issues/tickets") with parent/child links, assignee, status (`todo → in_progress → in_review → blocked → done/cancelled`), and a **blocked-by** relationship so a draft can wait on a review and auto-wake when it clears.
- **R-ORCH-3 Shared documents.** Versioned canon/engine docs readable by all agents, writable by their owners.
- **R-ORCH-4 Agent identity & permissions.** Each agent has an identity, a role, allowed tools, and a budget (see §14).
- **R-ORCH-5 Run budgets & circuit-breaker.** A **run-level** accumulator of total tokens (input+output across all LLM calls in a run) **and** a hard per-run iteration/step cap; exceeding either aborts the run and pauses the agent. (Separate from, and not to be confused with, a per-call `max_output_tokens` truncation cap.) See §13.2.
- **R-ORCH-6 Observability/audit.** Every run and tool call traced; state is queryable ("what's in the queue, for how long, what stalled").
- **R-ORCH-7 Human checkpoints.** A way to present an agent's output to a human and block on sign-off.

These mirror Paperclip's platform features but are stated as capabilities so they can be built on Antigravity primitives or a thin custom runner. See §13 for the concrete default control loop and a capability→primitive table.

### 6.3 Recommended Google-native stack

| Concern | Default (Google-native) | Pluggable alternative |
|---|---|---|
| Agent runtime / framework | **Google ADK** (Agent Development Kit) agents | Any MCP-compatible agent runtime |
| Reasoning model (editorial, judge) | **Gemini 3 Pro** (high-reasoning tier) | — |
| Operational model (ops, formatting) | **`gemini-flash-latest`** alias (fast tier; the alias auto-tracks the current Flash so config never names a model that may not be GA) — intelligent model routing (Day 1) | — |
| Mechanical model (formatting, ledger ops, digest) | **Flash-Lite** tier (cheapest; optional third tier for purely deterministic work) — confirm name/availability at build time | — |
| Hosting / managed runtime, sessions (durable memory → Sheets/Drive SoR, §8.1) | **Vertex AI Agent Engine** (durable Sessions — see §13.2; confirm the current product name, e.g. a possible "Gemini Enterprise" umbrella, at build time). **Durable cross-run memory = Sheets-keyed** (a `memory` namespace in the SoR); **no dependency on Agent Engine Memory Bank GA** — Memory Bank is a documented future upgrade, not a build requirement | Cloud Run / self-host |
| Image generation | **Nano Banana Pro** (the Gemini-3-era Gemini-native image+edit model; the Brand Kit selects it via the stable token `gemini_image_pro` — confirm the marketing name + API ID at build time, §14.3); **Imagen** fallback | **Replicate `gpt-image-*`** (cross-provider; the OpenAI line on Replicate is `openai/gpt-image-1`) |
| Caption/typography compositing | **Caption-Composer service** (see §11) | any image-text renderer |
| System of record / history / calendar / ledger / **default human approval gate** | **Google Sheets + Google Drive** | DB + object store (recommended migration past single-process / single-brand / low-cadence) |
| Built-in approval UI + live agent console | **Agent Atelier Review app** + the **Studio Floor UI** (live agent-company console — graph, activity feed, intervention, trust panel; §12.4) (richer in-product surface, **Phase 5** — not part of the minimal set) | — |
| Scheduling | **Cloud Scheduler** / Agent Engine cron | cron |
| Tool integration protocol | **MCP** (one integration, every framework) | — |
| Inter-agent comms | in-process handoffs (single ADK deployment, default); **A2A** only where deployment genuinely splits agents | — |
| Notifications | **Gmail / Google Chat** (optional) | — |
| Build/dev environment | **Google Antigravity** (agentic IDE, built-in sandboxed browser for E2E checks) | Gemini CLI |

> **Simplicity guard (owner direction).** Add a Google tool only when it earns its place. A minimal deployment runs with just **Gemini + ADK + Drive + Sheets + one image provider** (approval via the Sheets gate). Calendar, Gmail/Chat, the Review app, A2A-as-services, and any DB/Pub-Sub/Firestore upgrade are *optional* enhancements, explicitly flagged as such throughout.

---

