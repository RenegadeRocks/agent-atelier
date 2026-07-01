<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §0 (source lines 16–29). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 0. How to read this spec

This document is written as a **spec-driven development (SDD)** artifact, following Day 5 of the course ("Spec-Driven Production-Grade Development"). The spec — not the code — is the **Architectural North Star** and the source of truth. The implementing agent (Antigravity / Gemini CLI / ADK) should treat this as the `/specs` root and regenerate code from it; the code is disposable, the spec is durable.

Per the course's Gemini-optimal formatting guidance, this spec uses a **hybrid Markdown + conditional YAML** style:

- **Markdown** carries narrative, intent, and "the why."
- **YAML blocks** carry structured configuration and schemas (kept flat, nesting ≤ 3, to avoid the reasoning "format tax").
- **Gherkin (`Scenario / Given / When / Then`)** carries acceptance behaviour, so the builder implements behaviour, not vibes.

**Build posture for the implementing agent:** Architect mode, **no YOLO**. Propose the folder structure and tech stack first for confirmation; generate tests, docs, and logging alongside features. **Model and library versions are deliberately deferred to build time** (see §14.3, §18.1): pin every library/model version then, and verify the *current* Gemini / ADK / image-model (Nano Banana / Imagen) / Instagram Graph API identifiers and limits against live docs before using them — do not trust the training cutoff.

---

