<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §2 (source lines 42–67). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 2. Background & motivation

### 2.1 What exists today (Paperclip / AOL engine)

The existing system is one configured "company" running on **Paperclip** (an open-source "AI agents that run a business" orchestration platform). It is a team of **8 agents** that collectively run a content engine:

- It produces **always-on educational/wellness content every 1–3 days**, plus **weekly program spotlights**, plus **campaign ladders** when a program has dates.
- Every claim is **research-grounded and citation-checked**; nothing factually wrong ships.
- The feed is governed for **variety** (no two posts look or read alike) and a hard **quality bar**.
- Finished posts land in a human **approval queue** (today: Notion); a human (the brand owner) does the final publish.

The intelligence and discipline live in a set of shared **canon documents** (a Creative Engine, a Visual Engine, a Research Bank, a Content Ledger, a Cadence Plan, plus voice/style/asset guides) and in **per-agent instruction files** (`AGENTS.md`) and **program knowledge briefs**. All of it is currently specific to Art of Living.

### 2.2 What we are building (and why now)

Two motivations:

1. **Product-agnostic reuse.** The user wants to run this same machine for other products. Today, rebuilding for a new brand means rewriting agent prompts and canon docs by hand. Agent Atelier makes "new brand" a *configuration* action, not an *engineering* action.
2. **A course capstone.** This is the capstone for the Kaggle 5-Day Vibe Coding agents course. The rebuild is a deliberate exercise of the course's frameworks (harness engineering, context engineering, MCP/A2A interoperability, agent skills, security & evaluation, spec-driven development) on Google Antigravity. Appendix B maps each course concept to where it is applied.

### 2.3 Why the existing design is worth preserving

The AOL engine encodes hard-won lessons (documented as dated "board directions" in its canon): feeds collapse into sameness without an explicit variety engine; compliant-but-boring is a failure, not a pass; per-piece research requests create friction so a *standing verified claim bank* works better; a silent paused routine can stall an engine for weeks, so **state must be observable**; an un-metered agent burned ~631k tokens once in a runaway loop, so **cost circuit-breakers are mandatory**. Agent Atelier preserves these as first-class, product-neutral requirements.

---

