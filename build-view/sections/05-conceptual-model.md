<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §5 (source lines 133–159). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 5. Conceptual model

### 5.1 Agent = Model + Harness (Day 1)

Agent Atelier is built on the course's central equation: **a raw model is not an agent; it becomes one when wrapped in a harness** — instructions/rule files, tools (MCP), sandboxes, orchestration logic, guardrails/hooks, memory, and observability. ~10% of behaviour is the model; ~90% is the harness. **Almost all of Agent Atelier's value and almost all of this spec is harness**: the canon documents, the per-agent instructions, the pipeline, the gates, the budgets. The model underneath (Gemini) is swappable.

### 5.2 The factory model (Day 1)

The owner's output is **not posts** — it is **the system that produces posts**. The owner (and the Managing Editor agent) operate the factory: define specs (the Brand Kit + canon), design guardrails, review/approve output. The agent "factory floor" plans → drafts → illustrates → verifies, looping failures back. This framing drives the whole architecture: invest in the harness, give agents *success criteria* (the quality bar) not keystroke instructions.

### 5.3 Context engineering: static vs dynamic (Day 1)

The studio's "knowledge" is engineered as six context types — **instructions, knowledge, memory, examples, tools, guardrails** — split into:

- **Static context** (always loaded, expensive): each agent's identity/instructions (`AGENTS.md`-style), the brand's voice/safety rules, persona.
- **Dynamic context** (loaded on demand, cheap): the relevant engine doc section, the relevant Offering Brief, a skill's body, a research entry — pulled per task via **progressive disclosure** (Day 3) so a hundred capabilities cost only their metadata until triggered.

This separation is *how* Agent Atelier stays product-agnostic and token-efficient: the static layer is generic engine + brand identity; the brand specifics are dynamic, retrieved from the Brand Kit and canon store as needed.

**The sixth context type — *Examples* (dynamic few-shot) (Day 1).** Of the six types (instructions · knowledge · memory · **examples** · tools · guardrails), *examples* is the one not to leave static. The Brand Kit's `sample_lines_good/bad` seed a *fixed* few-shot, but the studio accumulates the highest-signal corpus there is: **owner-approved (and owner-edited) published pieces.** At **IDEATE+DRAFT** a content agent retrieves a small, *dynamically selected* few-shot set — the K most-recent owner-approved pieces for this **track/offering/language**, plus 1–2 owner-*edited* pairs (draft → owner's edit) as "do-it-this-way" demonstrations — loaded as dynamic context. This makes the §15.3 improvement loop a **context-engineering loop**: approvals re-seed the writers, not just calibrate the judge. Selection reuses the Content Ledger + corrections log (§8.1/§9.4) — **no vector store** (recency + track/offering/language keys), consistent with §8.3's "Knowledge = keyed Sheets/Drive access, no semantic index."

### 5.4 Conductor and orchestrator (Day 1)

The human moves between **conductor** (real-time: "write me a post about X", approving a draft) and **orchestrator** (async: let the weekly routine run, check the queue later). The **Managing Editor agent** is itself an orchestrator over the other agents. Agent Atelier must support both human modes and the agent-orchestration mode.

---

