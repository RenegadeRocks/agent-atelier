<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §21 (source lines 2579–2647). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 21. Capstone submission (Kaggle Vibe Coding — Agents for Business)

> **Track:** Agents for Business. **Platform:** Google Antigravity (Gemini 3 + ADK). **Build envelope:** the complete Agent Atelier (P0–P6, §19) built in sequence and submitted by **July 6, 2026, 11:59 PM PT**. **Thesis to land:** *the studio is constant; the brand is configuration* — built under the §18.4 build-governance harness, which is the differentiator. **Lead with the working system; land the method.**

### 21.1 Course-concept coverage (the rubric anchor)

≥3 course concepts are required; this PRD hits **all of them** (Appendix B is the full map). Name each one *as implemented in the finished system* and point to the code that runs it:

- **Day 1** — Agent = Model + Harness (§5.1); factory model (§5.2); context engineering / static-vs-dynamic / progressive disclosure (§5.3, §7.3, §8.3) — including the sixth *Examples* context type as dynamic few-shot (§5.3) and *context-rot / RAG-for-tools* tool-definition disclosure (§8.3); conductor vs orchestrator (§5.4, §13); economics / model routing (§6.3, §13.2).
- **Day 2** — MCP, "one integration, every framework" (§16), with a per-server transport / output-schema / MCP-Inspector contract (§16.1) and the `notify` capability contract (§16.2); A2A / Agent Cards / the GOTO problem (§13.3) — one illustrative Creative-Director Agent Card authored (§13.3, Appendix D).
- **Day 3** — Agent Skills / progressive disclosure / SKILL.md (§8.3, §18.3); read/draft/act ladder (§14.1).
- **Day 4** — 7-Pillar security (§14) — incl. untrusted-content / Confused-Deputy / agentic identity / egress governance (§14.7), Zero Ambient Authority + JIT downscoping + file-tree allowlist (§14.1, §14.6), and Red/Blue/Green agentic SecOps (§15.4); 7-dimension evaluation + LLM-as-judge with **session convergence** as the eval unit (§15, §15.3); AgBOM / Intent Drift / Trust Decay (§17, §12.3, §13.2); checkpoint-before-mutate + Planner-phase threat-modelling (§14.4); the notification & escalation model with dead-man's switch (§14.4.1, §14.5); Denial-of-Wallet / observability (§13.2, §14.5); supply-chain hygiene (§18.2).
- **Day 5** — Spec-Driven Development (this PRD + Gherkin, §0); Policy Server (§14.2); `[[VARIABLE]]` resolver (§7, §7.2.1); HITL / Vibe-Diff (§14.4); Antigravity build workflow (§18); **the build-governance harness itself (§18.4)**.

This breadth is itself a differentiator — but the *method* (§18.4) is the wedge: a real, fully-specified product built under a governed harness, not a notebook that ran once.

### 21.2 Writeup skeleton (≤2,500 words; Kaggle penalizes over-limit)

Fill the brackets; keep the total under cap. Lead with the working system; land the BUNNY method as the differentiator; describe the **complete built system** accurately.

**Title + subtitle (~25 words)**
- **Title:** Agent Atelier — *"A Product-Agnostic AI Content Studio: the studio is constant, the brand is configuration."*
- **Subtitle:** one line naming the business problem + the agent approach (e.g. "An 8-agent ADK studio that turns a one-time Brand Kit into an always-on, governed social feed for any brand").

**1. The business problem (~250 words) — why this matters, money on the line.** Open with the enterprise pain: a steady, on-brand, factually-safe social feed is expensive, manual, and doesn't scale across brands — every new brand today means **re-engineering** (rewriting agent prompts + canon by hand). State the cost lever: onboarding becomes a *config action, not an engineering action*. Ground it in reality — this generalizes a **real, working system** (Paperclip/AOL, an 8-agent studio producing live wellness content); attribute the team's prior work. *Evidence:* one line on the existing system's real output cadence.

**2. What Agent Atelier is (~300 words) — the system, concretely.** One paragraph: describe a brand once via a guided interview → a company of **8 cooperating agents** plans, writes, illustrates, quality-reviews, queues → a human approves → publish. Name the 8 agents + one-line mandates (it's a *company*, not a prompt). The core innovation: the **Brand Kit** — all brand-specific facts in config; generic agents reference `[[VARIABLE]]`s; the same agents run for a coffee brand, an NGO, a SaaS, a meditation school. The governance promise: every piece passes safety + compliance + quality gating before a human sees it; HITL by default, auto-publish only once *trusted* (measured). *Evidence:* the §6.1 architecture diagram (also the cover image); a screenshot of a piece in the Sheets queue.

**3. Agent architecture & the course concepts (~600 words) — the technical heart; hit the rubric.** Be explicit; judges look for concepts by name (§21.1). Cover: **multi-agent (ADK)** — the 8-role company, in-process handoffs, ME as orchestrator, the PLAN→IDEATE→LINT→REVIEW→VISUALIZE→QUEUE→PUBLISH pipeline; **MCP servers** — every external capability over MCP (`sheets`, `image_generate`, `caption_compose`, `drive`, `research_fetch`, `instagram_publish`) with a real tool-call in the demo; **Agent Skills** — SKILL.md L1/L2/L3 progressive disclosure; **Day-5 SDD** — the whole thing regenerates from the spec (`/specs` is truth, code is disposable — the strongest Day-5 alignment); **Day-4 security & eval** — the Policy Server (default-deny + claim-grounding + fail-closed), the run-level cost circuit-breaker (the real ~631k-token lesson), the read/draft/act ladder, the Creative Director as LLM-judge across 7 dimensions. One tight paragraph each + a pointer to where it lives in the repo.

**4. What makes it production-grade — the BUNNY method (~450 words) — the differentiator.** Name the method: a **spec-first, contract-governed** build with **validator/executor/authorizer separation**, **one-milestone-verified-before-the-next**, and **conscious-deviation logging** (§18.4). Tie it to Day 5's "spec-driven, production-grade, governed, observable fleet" thesis — demonstrated, not described. Concrete proof points (pick 2–3): the **prompt-contracts** governing each build unit (attach one); the **report-is-not-the-repo** discipline (verify against the codebase, not the description); the **fail-closed / honest-refusal / don't-fake-MCP** discipline baked into the contracts (if an integration can't be reached, the contract degrades to the *simplest conformant MCP server* — never a stub that pretends). The credibility framing: the build is governed end-to-end, so the writeup's claims are grounded in code that runs. *Evidence:* link the PRD (the SDD spec is itself a differentiator); attach one prompt-contract; the conscious-deviation log.

**5. Demo (~250 words) — what the judges will see.** Walk the ≤5-min video's arc in prose: a **Brand Kit in** → agents coordinate → a piece drafted → linted → CD-reviewed → image generated + typography composited → landed in the Sheets queue → "and here's the governed harness behind it." State the reproducibility path: the public repo + README run-steps (the accepted live-demo substitute); name the test brand (the AOL Appendix-A kit is a ready worked example). Show the full 8-agent pipeline end to end. *Evidence:* the YouTube link; the repo link; 2–3 key screenshots in the Media Gallery.

**6. Results, limitations, what's next (~250 words) — honest close.** What the complete system does; the §3.3 metrics model (hard **=0** only where a deterministic check makes it observable; **measured escape rates with CIs** where only an independent audit is honest — the evaluation is falsifiable by design). Limitations stated plainly (§20): image-model fidelity (mitigated by text-free + OCR + composited type + CD pass); static-assets-only v1 (a deliberate non-goal). What's next: more publishing channels (LinkedIn, X, TikTok), richer analytics-driven strategy loops, a self-serve onboarding console. Close on the thesis: *the studio is constant; the brand is configuration* — and the harness is why it's trustworthy.

### 21.3 Word-budget check

| Section | Target |
|---|---|
| Title/subtitle | 25 |
| 1. Business problem | 250 |
| 2. What it is | 300 |
| 3. Architecture + concepts | 600 |
| 4. The method (differentiator) | 450 |
| 5. Demo | 250 |
| 6. Results/limits/next | 250 |
| **Total** | **~2,125** (≈375 headroom under the 2,500 cap) |

### 21.4 Required attachments

- **Cover image** — the §6.1 architecture diagram.
- **Video** — ≤5-min on YouTube, attached to the Media Gallery.
- **Public project link** — the GitHub repo + README setup steps (the accepted substitute for a live demo); a stranger must be able to run the full system end to end.
- **Track** — select **Agents for Business** on the Writeup.

### 21.5 Submission checklist

- [ ] Writeup ≤2,500 words, **Agents for Business** track selected.
- [ ] Cover image attached (the architecture diagram).
- [ ] ≤5-min video on YouTube, attached to the Media Gallery.
- [ ] Public project link (GitHub repo + README setup steps) attached.
- [ ] Repo is public and the README lets a stranger run the full system end to end.
- [ ] Writeup accurately describes the **complete built system** (not aspiration).
- [ ] One prompt-contract + the conscious-deviation log attached as method evidence (§18.4).
- [ ] Submitted (not left as draft) before **July 6, 2026, 11:59 PM PT**.

---

