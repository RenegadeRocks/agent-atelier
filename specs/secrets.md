# Secrets & the vault — spec

> Source: PRD §14.6 (sandboxing & secrets), §7 intro (two-target resolver), §7.2 / §17 (`secrets_ref`), §16 (integrations), §11 (auto-publish constraints).
>
> **The one invariant.** Secrets are referenced by name from the Brand Kit, stored in a vault, and resolved **only into the tool/MCP auth layer** (env vars / request headers) at call time. A secret value **never** enters model-visible context — not a prompt, not a canon doc, not a draft, not a trace/log payload, not an error message surfaced to a model. This is the second of the resolver's two targets (§7 intro): brand *facts* resolve into prompts; secret *references* resolve into auth only.
>
> **Build-time caution (§0, §14.3).** Every model name/ID, API host, scope string, and token-lifetime below is **deferred to build time**. The image default is the Gemini-native model token `gemini_image_pro` (Nano Banana Pro); the operational model alias is `gemini-flash-latest`. **Confirm names/IDs, API hosts, scopes, and token TTLs against live provider docs before wiring.** Do not trust the training cutoff; do not refuse a configured model on the belief it doesn't exist (only a live 404 is evidence).

---

## 1. Vault choice — Google Secret Manager (default)

The default vault is **Google Secret Manager (GSM)**. Rationale, consistent with the Google-native posture (§6):

- One IAM/audit plane with the rest of the stack (Drive/GCS/Sheets/Vertex). No second identity provider.
- Resource-level IAM (per-secret `secretAccessor` bindings) gives true least-privilege without a custom ACL layer.
- Native **versioning**, **rotation policy + Pub/Sub rotation notifications**, **CMEK**, and **Cloud Audit Logs** (`DATA_READ` on `AccessSecretVersion`) satisfy the §14.6 / §14.5 audit requirement out of the box.
- Pluggable: the `secrets_ref.vault` field is an enum, so a deployment may target another backend (`hashicorp_vault`, `aws_secrets_manager`) without touching agent code — the **Secrets Resolver** (§4) is the only component that binds to a backend.

**Non-goals.** Secrets are never committed to the repo, never placed in `brand_kit.yaml`, never in a `.env` checked into source, never in Sheets/Drive (the editable system-of-record), and never in agent memory / Session state. The Brand Kit stores **references only**.

GSM secret-id charset is `[A-Za-z0-9_-]` (no `/`). The naming convention in §3 uses `__` as the namespace separator for that reason.

---

## 2. `BrandKit.secrets_ref` schema

`secrets_ref` is a sibling of `assets_ref` on the BrandKit (§17: `BrandKit: { brand_id, fields per §7.2, assets_ref, secrets_ref, version }`). It contains **pointers**, never material.

```yaml
# Lives on the BrandKit record (NOT in the model-visible brand_kit.yaml body).
# Stored references only — every value here is a vault locator or non-secret routing hint.
secrets_ref:
  vault: google_secret_manager        # google_secret_manager (default) | hashicorp_vault | aws_secrets_manager
  project: "<gsm-host-gcp-project-id>"  # the GCP project that hosts the secrets (may differ from the runtime project)
  namespace: "atelier__<brand_id>"      # per-brand secret-id prefix; isolates one brand's secrets from another's
  default_version: "latest"             # "latest" | a pinned integer; per-key override allowed in `keys`

  # Each entry maps a logical key -> a GSM secret-id (resolved to projects/<project>/secrets/<id>/versions/<ver>).
  # Only keys relevant to the brand's enabled integrations need be present. Missing-but-required => fail-closed (§4).
  keys:
    image_provider_token:    "atelier__<brand_id>__image_provider_token"     # see §3.1 (may be absent on Vertex-native path)
    google_credentials:      "atelier__<brand_id>__google_credentials"       # see §3.2
    instagram_access_token:  "atelier__<brand_id>__instagram_access_token"   # see §3.3
    instagram_page_id:       "atelier__<brand_id>__instagram_page_id"        # see §3.3; FACEBOOK-LOGIN PATH ONLY

  # Non-secret routing hints (safe to store in the clear; they parameterize WHICH auth shape to assemble).
  image_provider_kind: "gemini_vertex"   # gemini_vertex | gemini_api | imagen_vertex | replicate
  google_auth_kind:    "service_account" # service_account (ADC) | oauth_user (refresh-token)
  instagram_login_path: "instagram_login" # instagram_login (preferred, no Page) | facebook_login (needs Page id)
```

Schema rules:

- **References only.** A linter rejects any `secrets_ref` value that looks like a credential (JWT shape, `AIza…`, `IGQ…`, PEM blocks, long high-entropy strings). If material is found, the kit fails validation.
- **`*_kind` fields are not secrets.** They tell the resolver which env/header shape to assemble (§3) and stay out of prompts anyway (auth-layer config).
- **Fail-closed coupling.** Which keys are *required* is derived from the brand's enabled integrations: `image_generate` always; `drive`/`sheets`/`research_fetch` require `google_credentials`; `instagram_publish` (auto-publish only) requires `instagram_access_token` (+ `instagram_page_id` iff `instagram_login_path == facebook_login`). A required key whose secret is absent/inaccessible blocks the dependent tool and routes to the owner (§4, §14.2).

---

## 3. Named secret keys per integration

One row = one vault secret. The **value shape** column says what bytes the secret holds; **maps to** says where the resolver injects it at call time (§4). Confirm exact env-var names / header forms / hosts at build time.

### 3.1 Image provider (`image_generate` — Nano Banana Pro default; §16)

The image token depends on `image_provider_kind`. The default token `gemini_image_pro` over **Vertex AI** carries **no separate secret** — it authenticates with the same Google service account as Drive/Sheets (§3.2). A standalone `image_provider_token` exists only on the AI-Studio or Replicate paths.

| `image_provider_kind` | Secret key | Value shape | Maps to (auth layer) |
|---|---|---|---|
| `gemini_vertex` (default, `gemini_image_pro` on Vertex) | — (none; reuses `google_credentials`) | n/a | ADC for `aiplatform`; see §3.2 |
| `imagen_vertex` (fallback) | — (none; reuses `google_credentials`) | n/a | ADC for `aiplatform`; see §3.2 |
| `gemini_api` (Gemini API / AI Studio) | `image_provider_token` | API key (`AIza…`-shape) | env `GEMINI_API_KEY` **or** header `x-goog-api-key: <key>` |
| `replicate` (`replicate_<model>`, optional) | `image_provider_token` | Replicate API token | env `REPLICATE_API_TOKEN` **or** header `Authorization: Bearer <token>` |

Notes: the operational text model uses the `gemini-flash-latest` alias and also authenticates via the same Google path on Vertex (no extra token). When `image_provider_kind` is a Vertex path, `secrets_ref.keys.image_provider_token` should be **absent** — its presence on a Vertex deployment is a config smell and is warned.

### 3.2 Google (`drive` / `sheets` / `research_fetch` / Vertex models / optional `notify`,`calendar`)

`google_auth_kind` selects the credential shape.

| `google_auth_kind` | Secret key | Value shape | Maps to (auth layer) |
|---|---|---|---|
| `service_account` (default) | `google_credentials` | Service-account key JSON **(or, preferred, a Workload-Identity binding with NO stored key — see §5)** | written to a sandbox-private tmp file; env `GOOGLE_APPLICATION_CREDENTIALS=<path>` → ADC. Library auto-adds `Authorization: Bearer <minted-token>` per call. |
| `oauth_user` | `google_credentials` | JSON `{ client_id, client_secret, refresh_token }` | resolver exchanges `refresh_token` → short-lived access token at the token endpoint; injects header `Authorization: Bearer <access_token>`; never stores the access token |

The same `google_credentials` secret backs **all** Google tools — the differentiation is **scope** (§5), not separate secrets. GCS byte-serving for the auto-publish image URL (§11) uses this same identity (signed-URL signing or a public/`storage.objectViewer` object).

### 3.3 Instagram (`instagram_publish` — the only launch publish adapter; auto-publish path only; §11/§16)

The manual handoff path needs **no** Instagram secret (the owner publishes by hand). These keys are required **only** when auto-publish is enabled.

| `instagram_login_path` | Secret key | Value shape | Maps to (auth layer) |
|---|---|---|---|
| `instagram_login` (preferred, **no linked Page**) | `instagram_access_token` | Long-lived Instagram access token (Business/Creator account) | query param `access_token=<token>` on the Graph API call **or** header `Authorization: Bearer <token>` (confirm current form at build) |
| `facebook_login` (legacy, **needs linked Page**) | `instagram_access_token` | Long-lived Page access token | as above |
| `facebook_login` only | `instagram_page_id` | The linked Facebook **Page id** (used to resolve the IG Business user id) | **routing param**, not a credential — injected into the request path/params, never a prompt |

Notes: a **Business/Creator** account is required on both paths; only the legacy `facebook_login` path needs the linked Page id, which is why `instagram_page_id` is conditional. Prefer `instagram_login` (no Page). `instagram_page_id` is low-sensitivity but is kept in the vault for one-place rotation and so it, too, stays out of model context. The publish-then-comment step (first-comment hashtags, §11) reuses the same token.

---

## 4. Resolution at call time (the Secrets Resolver)

The Secrets Resolver is a distinct component from the `[[VARIABLE]]` **context** resolver (§7.2.1). The context resolver substitutes brand facts into prompts; the Secrets Resolver substitutes credentials into the tool/MCP auth layer. **They never share a destination.**

1. **Trigger.** An MCP tool / SDK client is about to make an external call. The harness asks the Secrets Resolver for the auth bundle for that integration + brand.
2. **Fetch.** Resolver reads `secrets_ref`, builds the GSM resource name `projects/<project>/secrets/<id>/versions/<version>`, and calls `AccessSecretVersion` using the **runtime service account's** identity (resource-level `secretAccessor`, §5).
3. **Inject.** Per §3, the resolver sets the env var(s) for the scoped child/sandbox process **or** attaches the header(s) to the outbound request. Service-account JSON is materialized to a `0600` file inside the sandbox tmpfs and the path handed via `GOOGLE_APPLICATION_CREDENTIALS`; OAuth refresh tokens are exchanged for short-lived access tokens just-in-time.
4. **Use & discard.** Minted access tokens and any materialized key files are **memory/tmpfs-only**, scoped to the call (or a short in-process cache bounded well under token TTL), and zeroed/unlinked after. Nothing is persisted to Drive/Sheets/logs.
5. **Never to model.** The resolver has **no path** into prompt assembly, draft text, Session/Memory state, or trace span attributes. Spans record *that* `instagram_publish` ran and *which* secret key id (the locator) was read — never the value. Tool error strings are scrubbed of `Authorization`/`access_token`/key material before any model sees them (relevant to §14.3's "capture the verbatim error" — capture it for the human/audit, redact it for the model).
6. **Missing/inaccessible required secret = fail-closed.** Block the dependent tool, write an audit entry, and route to the owner (§14.2). Never silently fall back to an unauthenticated or alternate credential.

```gherkin
Scenario: Secrets never enter model-visible context   # PRD §13 (mirrors the §14.6 invariant)
  Given a prompt template referencing a secret placeholder
  When the resolver runs
  Then the secret resolves only into the tool/MCP auth layer (env/headers), never into prompt text

Scenario: A required publish secret is missing
  Given approval_mode auto and instagram_publish enabled
  And the instagram_access_token secret is absent or the runtime SA lacks accessor on it
  When the publish tool is invoked
  Then the resolver fails closed, writes an audit entry, and routes the piece to the owner
  And no unauthenticated or fallback credential is attempted
```

---

## 5. Least-privilege scoping

**Per-brand isolation.** Every secret is namespaced `atelier__<brand_id>__*`. IAM `roles/secretmanager.secretAccessor` is granted **at the secret resource level** to the **specific runtime service account for that brand's agents** — never `roles/secretmanager.admin` and never a project-wide accessor binding. Brand A's runtime identity cannot read Brand B's secrets.

**Split identities by trust tier (mirrors the Policy Server tiers, §13.1).**

- A **read/produce** SA used by content/visual/research tools: accessor on `google_credentials` (+ `image_provider_token` if present); Google scopes limited to `drive.file` (studio-created files only, *not* full `drive`), `spreadsheets`, `devstorage.read_write` on the one assets bucket, `generativelanguage`/`aiplatform`. **No** accessor on the Instagram secrets.
- A **publish** SA used only by Publishing & Operations: accessor on `instagram_access_token` (+ `instagram_page_id` on the Facebook-Login path) and on `google_credentials` strictly for GCS byte-serving of the publish asset. This SA is the only identity that can read the publish token, matching `instagram_publish` being the only act/external-irreversible tool (§13.1).

**Prefer no stored key at all.** For Google, prefer **Workload Identity / Application Default Credentials** (Cloud Run / Agent Engine attached SA) so there is **no service-account JSON in the vault**. Store a SA key only when ADC is impossible; if stored, it is the most sensitive secret here and gets the tightest accessor + shortest rotation (§6).

**Audit.** Enable Cloud Audit Logs `DATA_READ` on `AccessSecretVersion`; every secret access is attributable to an SA and ties into the append-only audit trail (§14.5). CMEK on the secrets; deny-by-default on the host project.

---

## 6. Rotation

| Secret | Lifetime / driver | Rotation policy |
|---|---|---|
| `instagram_access_token` | Long-lived IG/Page tokens are short-lived by our standards (commonly ~60 days — **confirm current TTL at build**) | **Auto-refresh** via the platform refresh endpoint on a scheduled job at ~80% of TTL (e.g. day ~50). On success, write a **new GSM version** and move `default_version` forward (or keep `latest`). On refresh failure, **fail-closed + alert the owner** (`notify`) well before expiry; never let auto-publish run on an expired token. |
| `image_provider_token` (`gemini_api` / `replicate`) | Provider API keys, no hard expiry | Scheduled rotation ~every 90 days: mint new key at provider → add new GSM version → verify a probe call → disable/destroy old version. |
| `google_credentials` — `service_account` JSON | High blast radius | **Eliminate** where possible via Workload Identity (no key). If a key exists: rotate ~every 90 days, overlapping (create new → cut over → disable old → destroy after a grace window). Enable GSM **rotation policy + Pub/Sub** rotation reminders. |
| `google_credentials` — `oauth_user` (refresh token) | Refresh tokens are long-lived but revocable | Re-consent / re-mint if revoked or on suspected compromise; access tokens are minted just-in-time and never stored, so only the refresh token rotates. |
| `instagram_page_id` | Stable identifier, not a credential | Rotate only if the linked Page changes; low sensitivity. |

**Mechanics.** Use GSM versioning for zero-downtime rotation: add the new version, verify with a health probe, then disable+destroy the prior version (don't destroy before cutover). Resolver caches respect TTL so a new version is picked up promptly. A `rotation_due` check feeds the weekly visibility digest (§14.5) so an expiring Instagram token is never a silent stall. On any suspected leak: destroy the version, mint+publish a new one, and force-evict resolver caches.

---

## 7. Build-time checklist (confirm against live docs — §0/§14.3)

- [ ] Confirm GSM secret-id charset/limits and the exact `projects/<p>/secrets/<id>/versions/<v>` form.
- [ ] Confirm the image path: is `gemini_image_pro` (Nano Banana Pro) on **Vertex** (ADC, no token) or **Gemini API** (key)? Set `image_provider_kind` accordingly; omit `image_provider_token` on Vertex paths.
- [ ] Confirm `gemini-flash-latest` alias is reachable on the chosen Google auth path (no separate secret).
- [ ] Confirm current Instagram **long-lived token TTL**, the **refresh** endpoint, and the auth form (`access_token` query param vs `Authorization` header).
- [ ] Confirm the login path: **Instagram-Login (no Page, preferred)** vs **Facebook-Login (needs `instagram_page_id`)**; only the latter requires the Page id secret.
- [ ] Confirm minimal OAuth scopes per tool (`drive.file` over full `drive`, `spreadsheets`, GCS object scope, `aiplatform`/`generativelanguage`).
- [ ] Prefer Workload Identity / ADC; store a SA JSON key only if unavoidable, then tighten rotation.
- [ ] Wire Cloud Audit Logs `DATA_READ` on `AccessSecretVersion`; verify secret values are redacted from spans and from model-visible tool-error strings.
