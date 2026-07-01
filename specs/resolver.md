# resolver.md — the `[[VARIABLE]]` registry and resolver contract

> Build artifact for **Agent Atelier**. Sources: PRD §7 (intro: two resolution targets),
> §7.2 (Brand Kit schema), §7.2.1 (resolver contract / buildability), §7.3 (seeding/wiring),
> §14.6 (context hygiene).
>
> This document is **generic and product-agnostic**. It defines how every brand-specific
> `[[VARIABLE]]` placeholder in the canon and agent templates is resolved at runtime, and
> where each resolved value is allowed to land. The engine docs themselves never change
> between brands (PRD §7.3, G1); only the resolved values do.

---

## 0. Mental model

A `[[VARIABLE]]` is a placeholder embedded in **canon docs** and **agent instruction
templates**. At **prompt-assembly time** (runtime, not at storage time — PRD §7.2.1
"Timing"), the resolver replaces each placeholder with a value drawn from the brand's
`brand_kit.yaml`, falling back to an environment default, and failing closed if a
**required** variable cannot be resolved.

There are **two resolution targets**, one mechanism (PRD §7 intro):

- **Target A — model-visible.** Brand facts, voice, audience, visual config, canon values.
  These are substituted into the text the model sees (prompts, canon, style guides) and
  into render/Composer configuration.
- **Target B — auth-layer-only (secrets).** API tokens for the image provider, Google, and
  Instagram. These are resolved **only into the tool/MCP auth layer** (env vars / request
  headers) at call time, and **never** inlined into model-visible context (PRD §7 intro, §14.6).

None of the 53 brand tokens below are themselves secrets — they are all Target A. The
secret class is a **separate token namespace** (`[[SECRET:*]]`, §3.3) that the same resolver
routes exclusively to Target B. `[[IMAGE_PROVIDER]]` is the bridge: it is a model-visible
selector that *also* tells the auth layer which secret key to fetch (§3.3).

Serialization rules (PRD §7.2.1): scalars inline; lists comma-joined inline **or** bulleted
(each registry row states which is canonical per use site); objects/maps via a defined
per-key format. **No raw YAML is ever dumped into a prompt.**

---

## 1. `[[VARIABLE]]` REGISTRY

Legend:
- **Req?** — `required` (fail-closed if unresolved, §4) · `optional` (may resolve empty) ·
  `cond` (conditionally required; condition in Notes).
- **Serialization** — `scalar` (inline) · `comma` (comma-joined inline list) ·
  `bullet` (newline bullet list) · `comma|bullet` (per-use-site; default listed first) ·
  `bool` · `int` · `hex` · `path` · `object:<format>`.
- **Target** — `model` (model-visible prompt / canon / render config) · `auth` (auth-layer-only).
- Fail-closed governance fields (PRD §7.2 / §14.2) are flagged **⛔ fail-closed**.

### 1.1 Identity

| Token | brand_kit field | Req? | Serialization | Target | Notes |
|---|---|---|---|---|---|
| `[[BRAND_NAME]]` | `brand_name` | required | scalar | model | Used verbatim everywhere the brand is named. |
| `[[BRAND_SHORT_NAME]]` | `brand_short_name` | optional | scalar | model | Full brandmark line (distinct from `[[WORDMARK_TEXT]]`). Default → `brand_name`. |
| `[[LOCALE]]` | `locale` | required | scalar | model | Primary locale string. Anchors local detail + language judgment. |
| `[[LANGUAGES]]` | `languages` | required | comma\|bullet | model | First entry = primary (§7.6 language rule). Inline comma list at use sites. |
| `[[MISSION]]` | `mission` | required | scalar | model | 1–2 sentences; anchors agent judgment. May span lines; emitted as one scalar block. |
| `[[BRAND_TYPE]]` | `brand_type` | required | scalar | model | Enum (`educational`, `product_commerce`, …). Selects active hook/shape pack (§9.1). |

### 1.2 Audience

| Token | brand_kit field | Req? | Serialization | Target | Notes |
|---|---|---|---|---|---|
| `[[AUDIENCE_PERSONA]]` | `audience_persona` | required | scalar | model | The one concrete reader in the writer's head. |
| `[[AUDIENCE_PAINS]]` | `audience_pains` | optional | comma\|bullet | model | Bulleted in canon; comma-joined in tight prompts. |
| `[[SCROLL_TEST_PERSONA]]` | `scroll_test_persona` | required | scalar | model | Used by the two-second scroll-test quality gate. |

### 1.3 Brand voice

| Token | brand_kit field | Req? | Serialization | Target | Notes |
|---|---|---|---|---|---|
| `[[VOICE_DESCRIPTORS]]` | `voice_descriptors` | required | comma\|bullet | model | Comma-joined inline. |
| `[[VOICE_DO]]` | `voice_do` | required | bullet\|comma | model | Bulleted in `brand_voice` canon. |
| `[[VOICE_DONT]]` | `voice_dont` | required | bullet\|comma | model | Bulleted; reinforces prohibitions. |
| `[[READING_LEVEL]]` | `reading_level` | optional | scalar | model | Default → `"plain, conversational"`. |
| `[[SAMPLE_LINES_GOOD]]` | `sample_lines_good` | optional | bullet | model | 1–3 exemplar on-brand lines; one per bullet. |
| `[[SAMPLE_LINES_BAD]]` | `sample_lines_bad` | optional | bullet | model | 1–3 off-brand lines to avoid; one per bullet. |

### 1.4 Compliance & safety  (⛔ three fail-closed fields)

| Token | brand_kit field | Req? | Serialization | Target | Notes |
|---|---|---|---|---|---|
| `[[CLAIMS_ALLOWED]]` | `claims_allowed` | optional | bullet\|comma | model | Permitted claims (with citation conditions). |
| `[[CLAIMS_FORBIDDEN]]` | `claims_forbidden` | **required ⛔** | bullet\|comma | model | MUST be owner-confirmed. Empty/unconfirmed = block publish (§14.2, §15.1). |
| `[[NON_DISCLOSURE_RULES]]` | `non_disclosure_rules` | **required ⛔** | bullet | model | Bind words AND image. MUST be elicited explicitly. |
| `[[REQUIRED_FRAMING]]` | `required_framing` | **required ⛔** | object:`framing-list` | model | List of `{topic, framing}`. MUST be elicited explicitly. Format §2.2. |
| `[[COMPARATIVE_CLAIMS_ALLOWED]]` | `comparative_claims_allowed` | required | bool | model | Compiles to a hard-rule when `false` (§14.2). |
| `[[POLITICAL_CONTENT_ALLOWED]]` | `political_content_allowed` | required | bool | model | Compiles to a hard-rule when `false` (§14.2). |

> The three ⛔ fields fail closed at **two** layers: (a) schema validation rejects an
> unconfirmed Brand Kit; (b) the resolver fails closed if the placeholder is still unresolved
> at prompt-assembly (§4). "Unknown = block publish, route to human."

### 1.5 Research policy

| Token | brand_kit field | Req? | Serialization | Target | Notes |
|---|---|---|---|---|---|
| `[[SOURCE_ALLOWLIST]]` | `source_allowlist` | required | comma\|bullet | model | Domain-appropriate authoritative/primary sources. |
| `[[SOURCE_DENYLIST]]` | `source_denylist` | optional | comma\|bullet | model | Default → `["blogs","forums","reddit","unverified social"]`. |
| `[[CLAIM_REVERIFY_MONTHS]]` | `claim_reverify_months` | optional | int | model | Default → `6`. Drives Claim Bank re-verification (§8.2). |
| `[[REQUIRE_SECOND_SOURCE_FOR_QUANTITATIVE]]` | `require_second_source_for_quantitative` | optional | bool | model | Default → `false`. High-stakes brands set `true`. |

### 1.6 Topical territory

| Token | brand_kit field | Req? | Serialization | Target | Notes |
|---|---|---|---|---|---|
| `[[EVERGREEN_PILLARS]]` | `evergreen_pillars` | required | bullet\|comma | model | Evergreen agent's territory. |
| `[[LOCAL_DETAIL_BANK]]` | `local_detail_bank` | optional | comma\|bullet | model | Anti-drab anchor bank. May resolve empty. |

### 1.7 Offerings  (list → per-offering expansion, §2.3)

| Token | brand_kit field | Req? | Serialization | Target | Notes |
|---|---|---|---|---|---|
| `[[OFFERINGS]]` | `offerings` | required | object:`offering-list` | model | Whole list; expands to one Offering Brief per entry (§7.4). |
| `[[OFFERING_ID]]` | `offerings[].id` | required (per entry) | scalar | model | Stable id; referenced by `standing_week` tracks (`offering:<id>`). |
| `[[OFFERING_NAME]]` | `offerings[].name` | required (per entry) | scalar | model | Used verbatim. |
| `[[OFFERING_BRIEF]]` | `offerings[].one_liner` | required (per entry) | scalar | model | Accurate, never-trivialized one-liner. Resolved inside each Offering Brief's scope. |

### 1.8 Channels & cadence

| Token | brand_kit field | Req? | Serialization | Target | Notes |
|---|---|---|---|---|---|
| `[[CHANNELS]]` | `channels` | required | comma\|bullet | model | Active publishing channels. |
| `[[STANDING_WEEK]]` | `standing_week` | required | object:`week-map` | model | Day→`{track,[language],[flag],[notes]}`. Format §2.2. Seeds `cadence_plan`. |
| `[[POSTS_PER_WEEK_TARGET]]` | `posts_per_week_target` | required | int | model | Cadence target. |
| `[[MAX_POSTS_PER_WEEK]]` | `max_posts_per_week` | required | int | model | Hard ceiling (§9.5). |
| `[[RESEARCH_POST_MIN_PER_WEEK]]` | `research_post_min_per_week` | optional | int | model | Default → `1`. `0` disables the standing research slot + enforcement. |

### 1.9 Contact / CTA  (used EXACTLY; never invented)

| Token | brand_kit field | Req? | Serialization | Target | Notes |
|---|---|---|---|---|---|
| `[[CONTACT_WHATSAPP]]` | `contact_whatsapp` | cond | comma\|bullet | model | List of numbers. Required unless `[[CONTACT_INSTAGRAM]]` present (≥1 contact). |
| `[[CONTACT_INSTAGRAM]]` | `contact_instagram` | cond | scalar | model | `@handle`. Required unless `[[CONTACT_WHATSAPP]]` present. |
| `[[CTA_STYLE]]` | `cta_style` | required | scalar | model | e.g. `soft`. Governs CTA discipline. |
| `[[CTA_FORBIDDEN_PHRASES]]` | `cta_forbidden_phrases` | optional | comma\|bullet | model | Default → `["register now","book now","sign up","limited spots"]`. |

### 1.10 Visual identity → Composer / visual canon

| Token | brand_kit field | Req? | Serialization | Target | Notes |
|---|---|---|---|---|---|
| `[[LOGO_ASSET]]` | `logo_asset` | required | path | model | Asset path; consumed by the Composer (file reference, not a secret). |
| `[[WORDMARK_TEXT]]` | `wordmark_text` | required | scalar | model | Short locator under the logo (distinct from `[[BRAND_SHORT_NAME]]`). |
| `[[PALETTE_HEX]]` | `palette_hex` | required | comma | model | Accent-rule gradient stops, comma-joined. |
| `[[ACCENT_DARK_BG]]` | `accent_dark_bg` | optional | hex | model | Scrim/type accent on DARK photos. Default → first `palette_hex` stop. |
| `[[ACCENT_LIGHT_BG]]` | `accent_light_bg` | optional | hex | model | Scrim/type accent on LIGHT photos. Default → darkened `palette_hex` stop. |
| `[[HEADLINE_FONT]]` | `headline_font` | required | scalar | model | Serif headline. |
| `[[LABEL_FONT]]` | `label_font` | required | scalar | model | Small-caps kicker/label. |
| `[[VISUAL_REGISTER]]` | `visual_register` | optional | scalar | model | Aesthetic register description (premium/warm/real-life; NOT stock/spa). |
| `[[VISUAL_VARIETY]]` | `visual_variety` | optional | scalar | model | Enum `balanced`\|`high`. Default → `balanced`. Narrows §9.2 treatment menu. |
| `[[VISUAL_STRATEGY]]` | `visual_strategy` | optional | scalar | model | Enum `concept_led`\|`product_led`. Default → `concept_led`. |
| `[[IMAGE_PROVIDER]]` | `image_provider` | required | scalar | model **+ auth selector** | Stable token (default `gemini_image_pro`). Model-visible AND selects the §3.3 secret key. |
| `[[IMAGE_QUALITY_TIER]]` | `image_quality_tier` | optional | scalar | model | Enum `medium`\|`high`. Default → `medium`. FLOOR/default; CD "premium" may upgrade a piece, never downgrade (§9.2). |

### 1.11 Publishing & approval

| Token | brand_kit field | Req? | Serialization | Target | Notes |
|---|---|---|---|---|---|
| `[[APPROVAL_MODE]]` | `approval_mode` | required | scalar | model | Enum `human`\|`auto`\|`auto_after_trust`. Gated by `auto_publish_enabled` master switch (§12.3). |
| `[[TRUST_THRESHOLD]]` | `trust_threshold` | cond | object:`trust-block` | model | Required iff `approval_mode == auto_after_trust`. `{window_pieces, min_approval_rate, max_avg_human_edits, zero_policy_violations}`. Format §2.2. |

### 1.12 Image-model naming caution (resolver-relevant)

`[[IMAGE_PROVIDER]]` resolves to a **stable token**, decoupled from marketing names so a
rename cannot break config (PRD §14.3, §17):

| Token value | Means (confirm exact name + API ID at build time) |
|---|---|
| `gemini_image_pro` | **default** — the Gemini-native image+edit model (marketing name **Nano Banana Pro**). The operational model alias used in calls is `gemini-flash-latest`. |
| `imagen` | Google-native fallback. |
| `replicate_<model>` | cross-provider, e.g. `replicate_gpt_image` → `openai/gpt-image-1` on Replicate. |

The resolver treats the token as an opaque literal; the **provider abstraction**
(`ImageGenerator` interface) maps token → concrete model id + the auth secret key. Confirm
all model names/IDs at build time; do not hardcode marketing names into canon.

---

## 2. Serialization formats

### 2.1 Scalars and scalar-like

- `scalar` → emitted inline, trimmed, no surrounding quotes. Multi-line scalars (e.g.
  `[[MISSION]]`) preserve internal newlines but are never wrapped in YAML block syntax.
- `bool` → lowercase `true`/`false`.
- `int` → bare integer.
- `hex` → `#RRGGBB`, uppercased.
- `path` → POSIX-relative path under the brand bundle (e.g. `assets/logo.png`); never
  resolved to an absolute filesystem path inside model-visible text.

### 2.2 Lists and objects

- `comma` → `a, b, c` (single line).
- `bullet` → one `- item` per line.
- `comma|bullet` / `bullet|comma` → both are valid; the **canonical default** is the first
  named form. Each canon/agent use-site declares its choice in a trailing comment, e.g.
  `[[VOICE_DO]] <!--bullet-->`. The resolver honors the use-site directive; absent a
  directive it uses the registry default.

**`object:framing-list`** (`[[REQUIRED_FRAMING]]`) — one bullet per entry:

```
- topic: <topic> — framing: <framing>
```

**`object:week-map`** (`[[STANDING_WEEK]]`) — one bullet per day, omitting absent keys:

```
- mon: track=evergreen
- wed: track=evergreen, flag=research_grounded
- tue: track=offering:<id>, language=<lang>
```

**`object:trust-block`** (`[[TRUST_THRESHOLD]]`) — flat `key=value` line list:

```
- window_pieces=<int>
- min_approval_rate=<0..1>
- max_avg_human_edits=<int>
- zero_policy_violations=<bool>
```

### 2.3 `object:offering-list` and per-offering expansion

`[[OFFERINGS]]` does not normally appear inline. At wiring time (PRD §7.3, §7.4) it expands
into **one Offering Brief per entry**. Within each Offering Brief's resolution scope, the
per-entry tokens are bound to that entry:

```
[[OFFERING_ID]]    = offerings[i].id
[[OFFERING_NAME]]  = offerings[i].name
[[OFFERING_BRIEF]] = offerings[i].one_liner
```

Optional per-entry keys (`is_flagship`, `funnels_from`) are exposed to the Offering Brief
template as `[[OFFERING_IS_FLAGSHIP]]` / `[[OFFERING_FUNNELS_FROM]]` (optional, default empty)
but are out of the top-level registry scope. When `[[OFFERINGS]]` *is* requested inline (e.g.
a catalog line) it serializes as a bullet list of `name — one_liner`.

---

## 3. Resolution targets and the secret split

### 3.1 Target A — model-visible

All 53 registry tokens above are Target A. They land in: agent instruction prompts, canon
docs, channel style guides, and Composer/render configuration. Composer config (palette,
fonts, logo path, accents) is render-layer but treated as model-visible-class because it
contains no secrets.

### 3.2 Hard rule: no secret ever enters Target A

The resolver MUST refuse to substitute any secret value into a Target-A destination. A secret
appearing in a model-visible template is a build error (§4, `ERR_SECRET_IN_MODEL_CONTEXT`).

### 3.3 Target B — auth-layer-only secrets

Secrets live in a vault, referenced by name, resolved **only into the tool/MCP auth layer**
(env vars / request headers) at call time (PRD §7 intro, §14.6, §15). They use a distinct
namespace so they can never be confused with brand tokens:

| Secret token | Vault ref (example) | Selected by | Destination |
|---|---|---|---|
| `[[SECRET:IMAGE_PROVIDER_KEY]]` | `secrets.image_provider_api_key` | `[[IMAGE_PROVIDER]]` value | image-tool auth header |
| `[[SECRET:GOOGLE_TOKEN]]` | `secrets.google_oauth_token` | system-of-record / Drive | Google MCP auth |
| `[[SECRET:INSTAGRAM_TOKEN]]` | `secrets.instagram_graph_token` | publish tool | Instagram MCP auth |

`[[IMAGE_PROVIDER]]` is the only bridge between the two targets: its **value** is
model-visible (the pipeline needs to know which provider/aesthetic), but it also tells the
auth layer **which** `[[SECRET:IMAGE_PROVIDER_KEY]]` to fetch. The secret value itself is
never emitted into the prompt.

---

## 4. Resolver contract (PRD §7.2.1) — invariants

1. **Timing.** Resolution happens at **prompt assembly (runtime)**, per use. Stored docs
   remain templates; values are never baked in.
2. **Precedence.** `brand_kit value → environment default → error`. (This is the
   "environment fallback.")
3. **Fail-closed.** Any unresolved **required** token blocks the run, drafts/publishes
   nothing, and surfaces the gap to the owner. Optional tokens may resolve empty.
4. **No recursion.** Resolved values are literals; they are never re-scanned for further
   `[[...]]` substitution.
5. **Secret split.** Secrets resolve only into the auth layer; never into model-visible text.
6. **Serialization discipline.** Emit per the registry/use-site directive; never dump raw YAML.

```gherkin
Scenario: Unresolved required variable blocks the run
  Given a canon template references a required [[VARIABLE]] absent from the Brand Kit and environment
  When an agent assembles its prompt
  Then the run is blocked and the gap is surfaced to the owner
  And nothing is drafted or published
```

---

## 5. Reference resolver pseudocode

```python
# resolve(template, brand_kit, env, registry, vault, scope) -> resolved_text
#
# template : str             — canon / agent template containing [[TOKENS]]
# brand_kit: dict            — parsed, schema-validated brand_kit.yaml
# env      : dict            — environment defaults (the fallback layer)
# registry : dict[str,Spec]  — the table in §1: token -> Spec
# vault    : SecretsVault    — name-referenced secrets; values never returned to caller
# scope    : ResolveScope    — MODEL  (Target A: prompt/canon/composer)
#                              | AUTH  (Target B: tool/MCP auth layer)
#                            — plus optional per-offering binding (§2.3)

PLACEHOLDER = r"\[\[([A-Z0-9_:]+)\]\]"   # uppercase; ':' allows the SECRET: namespace

def resolve(template, brand_kit, env, registry, vault, scope):
    errors = []
    out = []
    cursor = 0

    for match in finditer(PLACEHOLDER, template):
        out.append(template[cursor:match.start()])
        cursor = match.end()
        token = match.group(1)                      # e.g. "VOICE_DO" or "SECRET:GOOGLE_TOKEN"
        directive = read_use_site_directive(template, match)   # e.g. <!--bullet-->

        # ---- (A) SECRET namespace: route ONLY to the auth layer ----------------
        if token.startswith("SECRET:"):
            if scope.target != AUTH:
                errors.append(Err("ERR_SECRET_IN_MODEL_CONTEXT", token))
                continue
            # selector bridge: image key chosen by the model-visible IMAGE_PROVIDER value
            ref = secret_ref_for(token, brand_kit)  # e.g. image_provider -> api_key name
            if not vault.has(ref):
                errors.append(Err("ERR_SECRET_MISSING", token))   # fail-closed
                continue
            # Inject into the auth layer side-channel; the literal is NEVER appended to `out`.
            scope.auth_bind(token, vault.fetch(ref))
            continue

        # ---- (B) brand tokens: model-visible only ------------------------------
        spec = registry.get(token)
        if spec is None:
            errors.append(Err("ERR_UNKNOWN_TOKEN", token))        # fail-closed
            continue
        if spec.target == AUTH:
            errors.append(Err("ERR_BRAND_TOKEN_NOT_FOR_AUTH", token))
            continue

        # ---- precedence: brand value -> env default -> error -------------------
        value = lookup(brand_kit, spec.field, scope.binding)      # incl. per-offering bind
        if is_empty(value):
            value = env.get(spec.env_key)                          # environment fallback
        if is_empty(value):
            value = spec.default                                   # registry static default
        if is_empty(value):
            if spec.required_in(brand_kit):   # honors conditional (cond) requirements
                errors.append(Err("ERR_REQUIRED_UNRESOLVED", token))  # FAIL CLOSED
                continue
            value = ""                                             # optional -> empty

        # ---- serialize (NO recursion: literal, not re-scanned) -----------------
        literal = serialize(value, spec.serialization, directive)
        assert "[[" not in literal or spec.allow_literal_brackets  # never re-resolved
        out.append(literal)

    out.append(template[cursor:])

    # ---- fail-closed gate: block the whole run if ANY error ---------------------
    if errors:
        block_run_and_surface_to_owner(errors)   # nothing drafted, nothing published
        raise ResolveBlocked(errors)

    return "".join(out)


def required_in(spec, brand_kit):
    if spec.req == REQUIRED:
        return True
    if spec.req == CONDITIONAL:
        return spec.condition(brand_kit)   # e.g. TRUST_THRESHOLD iff approval_mode==auto_after_trust
                                           # e.g. CONTACT_* iff the other contact is absent
    return False                            # OPTIONAL


def serialize(value, kind, directive):
    form = directive or kind.default_form           # use-site overrides registry default
    match form:
        case "scalar":  return str(value).strip()
        case "bool":    return "true" if value else "false"
        case "int":     return str(int(value))
        case "hex":     return normalize_hex(value)
        case "path":    return as_relative_path(value)         # never absolute in MODEL scope
        case "comma":   return ", ".join(map(str, value))
        case "bullet":  return "\n".join(f"- {x}" for x in value)
        case "framing-list":
            return "\n".join(f"- topic: {e.topic} — framing: {e.framing}" for e in value)
        case "week-map":
            return "\n".join("- " + day + ": " + kv_join(slots) for day, slots in value.items())
        case "trust-block":
            return "\n".join(f"- {k}={v}" for k, v in value.items())
        case "offering-list":
            return "\n".join(f"- {o.name} — {o.one_liner}" for o in value)
    raise Err("ERR_UNKNOWN_SERIALIZATION", kind)
```

### 5.1 Notes on the pseudocode

- **Precedence** is exactly `brand_kit → env → static default → error` (step B). The
  environment layer is the documented "environment fallback" (§7.2.1).
- **Fail-closed** is enforced two ways: required-unresolved appends an error and the final
  gate refuses to return any text if *any* error occurred — so a single missing required
  token blocks the entire assembly (the §4 / Gherkin guarantee).
- **No recursion**: `serialize` returns literals that are appended directly; the function
  never re-runs `resolve` over them, and the assertion guards against accidental
  re-substitution.
- **Secret split**: the `SECRET:` namespace is the only path that touches `vault`, and it is
  hard-gated to `scope.target == AUTH`. A brand token whose registry target is `AUTH`, or a
  secret token in a MODEL scope, both fail closed — secrets can never reach model-visible text.
- **Conditional requirements** (`cond` rows: `[[TRUST_THRESHOLD]]`, `[[CONTACT_WHATSAPP]]`,
  `[[CONTACT_INSTAGRAM]]`, per-offering tokens) are evaluated by `required_in` against the
  live Brand Kit, so they fail closed only when their condition makes them mandatory.

---

## 6. Build-time checklist

- [ ] Every `[[TOKEN]]` appearing in any canon/agent template has a registry row here.
- [ ] The three ⛔ fail-closed fields are owner-confirmed before first resolution.
- [ ] `[[IMAGE_PROVIDER]]` token value, concrete model id, and `gemini-flash-latest` alias
      are confirmed against the provider at build time (§1.12); no marketing name hardcoded.
- [ ] No secret value is reachable from any MODEL-scope resolution path.
- [ ] Use-site list/object directives are present where the non-default form is wanted.
- [ ] Resolver unit test reproduces the §4 Gherkin: missing required → run blocked, nothing drafted.
