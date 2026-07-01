<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §16 (source lines 2139–2188). Do NOT hand-edit; regenerate with tools/build_view_split.py after PRD edits. -->

## 16. Integrations & interfaces (MCP-first)

Every external capability is exposed over **MCP** ("one integration, every framework").

| MCP tool/server | Purpose | Default impl |
|---|---|---|
| `image_generate` | text-free image generation | Nano Banana Pro (Gemini-native) / Imagen / Replicate |
| `caption_compose` | brand typography compositing | Caption-Composer service |
| `drive` | store/host assets, byte-serving for auto-publish, previews | Google Drive / GCS |
| `sheets` | calendar, ledger, queue, async approval, append-only audit | Google Sheets |
| `research_fetch` | sanitized, allowlist-bound source retrieval + grounding | Google Search grounding / sanitized fetcher |
| `instagram_publish` | publish to Instagram (the only launch adapter) | Instagram Platform content-publishing API (Instagram-Login path preferred) |
| `instagram_caption_edit` / `instagram_delete` *(post-publication correction; §14.3)* | owner-authorized correct-in-place / take-down of a live piece — **no new publish authority**, behind the §14.4 checkpoint | Instagram Platform content-publishing API |
| `notify` *(optional; fully contracted — §16.2)* | owner-reaching alerts, digests & escalations (severity-tiered, deduped, rate-capped) | Gmail / Google Chat |
| `calendar` *(optional)* | schedule slots | Google Calendar |
| `handoff_export` | materialize the channel-aware **Post Kit** (§12.3.1: zero-padded ordered slide files, caption/hashtag/alt copy-blocks, QR/send-to-phone link) + run the deterministic platform-export pre-check (§14.2) | Drive/GCS folder + Review-app/Studio-Floor view |

`handoff_export` reads through `drive`/`sheets` and `notify` and adds **no** new publish authority — a packaging + validation capability, **not** a poster. On the manual path the human remains the "act"; `handoff_export` is "draft" output (Day 3 read/draft/act). Mark-as-posted (§12.3.2) is the human's write back through `sheets`.

Agent identity, AGENTS.md/GEMINI.md instruction files, and **Agent Skills** (`.agent/skills/*/SKILL.md`, §8.3) are the other harness primitives. The cost circuit-breaker (§13.2) wraps the runner, not a tool.

#### 16.1 The MCP server contract (transport, schemas, Inspector-verified) — Day 2

Day 2's Connection step is *"list the tools **and validate the output schema**."* The table above names *what* each tool does; this pins *how* it is wired, so MCP is **real, not faked** (§18.4 ON-FAIL: never an inline function pretending to be a tool):
- **Transport, named per server.** Local/in-process tools (`caption_compose`, `sheets`, `drive`, `image_generate`) default to **stdio** (JSON-RPC 2.0 over stdin/stdout); remotely-hosted tools (`research_fetch`, `instagram_publish`, `notify`) default to **SSE/HTTP**. Each server declares its transport at registration; changing it is a §18.4.4 conscious deviation.
- **Declared input *and* output schema.** Every tool ships a JSON **output** schema, not just inputs (e.g. `image_generate` → `{ asset_url, prediction_id, provider, tier, width, height }`; `research_fetch` → `{ source_url, fetched_text, source_hash, fetched_at }`). A live response that fails its declared schema **fails closed** (the call errors; nothing proceeds).
- **Inspector-verified at build time.** P1-B VERIFY (§19.1) runs each tool through the **MCP Inspector**: query it, inspect its schema, capture one raw JSON-RPC call. The captured Inspector session is the §18.4.5 *report-is-not-the-repo* proof the tool *exists and conforms* — not a claim that it does.
- **Act-tier tool-input HITL.** Before any `act`-tier call (`instagram_publish`, `set_budget`), the *resolved* tool input is shown in the handoff/Vibe-Diff (§14.4) — Day 2's *"show tool inputs before calling the server."*
```gherkin
Scenario: An MCP tool is proven real via the Inspector, not described
  Given caption_compose is registered with a declared output schema
  When P1-B VERIFY runs the MCP Inspector against it
  Then the Inspector lists the tool, shows its input/output schema, and a raw JSON-RPC call returns schema-valid structured content
  And the captured Inspector session is committed as the P1-B evidence (report-is-not-the-repo)
```

#### 16.2 The `notify` capability contract — Day 2 adapter, Day 4 governed send

`notify` is the only out-of-band human-reaching tool, so it is **fully contracted** (a bare *optional* row is not buildable). It is an **act / external-irreversible** capability (§14.1) — governed and audited like publish (an external send is a Denial-of-Wallet surface, §14.4.1):
- **Payload:** `{ brand_id, severity(critical|action|digest), event_type, dedup_key, title, body_markdown, piece_id?, run_id?, deep_link?, recipients[] }`. `body_markdown` is plain-language (§12.4 voice), never a raw span dump.
- **Idempotency / dedup:** keyed by `dedup_key` over an open window — a re-send **updates**, never duplicates (distinct from the §12.2 publish idempotency hierarchy).
- **Severity & routing:** tiers map to the §8.2 `notifications` config (quiet-hours, digest schedule, `severity_floor`); **CRITICAL always breaks through** — it is the dead-man's-switch channel (§14.5).
- **Rate cap:** honors `notifications.max_sends_per_hour`; non-CRITICAL coalesces on cap; CRITICAL exempt.
- **Audit:** every send (and every failure) writes an `AuditEntry` with `actor_agent` = the emitting agent and `action = notify:{severity}`.
- **Secrets:** recipient addresses / channel tokens resolve **only into the tool/MCP auth layer** (§14.6) — never into a prompt or `body_markdown`.
- **Delivery:** retry-with-backoff on transient failure; on hard failure fall back to the pinned Sheets `ALERTS` row and log loudly. **A `notify` failure never blocks the pipeline (fail-open) but is never silent (fail-loud in audit).**


---

