<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §1 (source lines 30–41). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 1. Executive summary

Agent Atelier is a **product-agnostic AI content studio**: a small company of cooperating AI agents that autonomously plans, writes, illustrates, quality-reviews, and queues a varied, on-brand stream of social-media posts (Instagram-first, channel-extensible) for **any** product, service, cause, or brand.

It is the generalization of a working system. The user already runs a private build called **Paperclip** that produces Instagram content for *Art of Living Ludhiana* (a meditation/wellness organization). In that system everything is hard-wired to that one brand. Agent Atelier lifts every brand-specific fact out of the agents and into a **Brand Kit** — a configuration layer a user supplies once, through an intuitive guided intake. The same agent company, the same craft engine, the same governance then runs for a coffee brand, a SaaS tool, an NGO, a fashion label, or a meditation school — only the Brand Kit changes.

The core promise: **the studio is constant; the brand is configuration.**

This document specifies the complete system to be rebuilt on Google Antigravity — agents, prompts, the creative "engine" documents, the production pipeline, the approval/publishing flow, governance, evaluation, and the configuration model — in a way that is independent of any particular orchestration platform, while recommending a concrete Google-native stack.

---

