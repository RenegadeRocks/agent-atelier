# P5-B Validation Report — Studio Floor UI (as-built vs contract + logged deviations)

- **Validator:** independent read-only adversarial audit (P5-B validator pass)
- **Date:** 2026-07-06
- **HEAD audited:** `97938de` (main, "P4-B Final Validation and Compliance") after `git pull --ff-only`
- **Requirements loaded:** `specs/contracts/P5-B.md`; `build-view/sections/12-review-approval-publishing-system-of-record.md` §12.4 (L157–388) + §12.5 (L391–497); logged deviations `specs/deviation_log.md:253-261` (both P5-B entries, 2026-07-06)
- **Method:** content-level verification (files opened and read in full; tests executed; server started and probed live; fixtures parsed and diffed independently). No repo file modified except this report.

---

## Verdict table

| # | Item | Verdict | Evidence (file:line) |
|---|------|---------|----------------------|
| 1a | UI self-contained — no external network resources | **PASS** | Scan test `app/tests/test_p5_b.py:280-285` passes; independent grep for `https?://` in `src=`/`href=`/`@import`/`import`/`url()` positions across all three files → **zero hits**. Only `href` is the local `styles.css` (`ui/studio-floor/index.html:7`); only `src` is the local `app.js` (`index.html:180`). The single `https://` occurrence in `index.html` is *data* inside the inline demo JSON (asset URLs/permalink, `index.html:178`) — rendered as text only (`app.js:709-710` puts `asset_url` in a `<span class="mono">`, never an `<img>`), so nothing is ever fetched. `styles.css:11-14` uses system font stacks only; no `fonts.googleapis`, no `cdn.` |
| 1b | Floor / Pipeline / Company render from state | **PASS** | Floor: `renderFloor()` `app.js:276-386` derives every station state from `brandPieces()`/`brandEvents()`; Pipeline: `renderPipeline()` `app.js:463-487` lanes over the six-status enum from state; Company: `renderCompany()` `app.js:490-511` — org cards are the spec-constant eight agents + quiet/empty state derived from `brandPieces().length` (`app.js:500-502`). Approachable-subset (ON-FAIL-blessed) |
| 1c | §12.4 states as real code paths: loading / per-tab empty / error / offline-with-dimming / first-run demo badge | **PASS** | Loading: `body.loading` (`index.html:9`) + skeleton (`index.html:169`, `styles.css:530-535`), cleared at `app.js:176,197`. Per-tab empty: Floor `#floorEmpty` (`index.html:50`, `app.js:286`), Pipeline `lanes-empty` (`app.js:467-471`), Company empty-note (`app.js:500-502`), feed-quiet (`app.js:563`), tray-quiet (`app.js:579`). Error (nothing loadable): `app.js:174-179` distinct banner. Offline w/ last-known dimming: `S.offline` → banner + `layout.dimmed` (`app.js:219-227`, `styles.css:169` opacity .55) and chip "▲ Offline — showing last-known" (`app.js:221`). First-run demo: `#demoBadge` "DEMO DATA" (`index.html:15`), shown when demo-sourced (`app.js:217`) |
| 2a | Inline demo fixture drift-tested vs `data/demo-state.json`, substantive | **PASS** | `test_inline_demo_state_mirrors_canonical_fixture` (`app/tests/test_p5_b.py:157-170`): parses the inline block, un-escapes `<\/`, asserts **parsed-JSON equality** with the canonical file **and** runs the shared shape validator (`validate_state`, `tools/export_floor_state.py:265-320` — 40+ per-field checks incl. monotonic `seq`, status enum, trust-window keys). `test_demo_state_valid` (`test_p5_b.py:140-154`) additionally asserts *content*: verbatim CD note, an R2/2 revise loop, a waiting human-gate piece, a Published piece, a Safety-Blocked exception, 3 brands. Test executed → PASSED (see §Test runs). Independent re-diff by this validator: `inline == canonical: True`, 8 pieces / 29 events / 3 brands, all six statuses present, R2 loop + Safety-Blocked present. The fixture is rich real content, not placeholders |
| 2b | Floor Actions disabled w/ visible reason on demo or file://; enabled only for real served state | **PASS** | `actionsDisabledReason()` `app.js:655-664` returns a reason when `location.protocol === 'file:'` **or** `S.demo`; drawer applies `disabled aria-disabled title=` to all three action buttons (`app.js:712-714, 739-741`) plus a visible `⚠` note (`app.js:743`, styled `styles.css:517-519`); defense-in-depth re-check inside `submitAction()` (`app.js:757`). `S.demo` is true whenever the load fell back to `demo-state.json` or the inline block (`app.js:161-187`); it is false only when `data/state.json` was actually fetched over HTTP — i.e., a real export served by `floor_serve.py`. (See MINOR-1: the fixture's `"demo":true` *field* is not itself checked) |
| 3a | `build_state()` pure over the as-built 6-col Queue / 7-col Audit shapes | **PASS** | Pure: `tools/export_floor_state.py:174-262` — no env/file/network access; clock injectable via `generated_at`. Queue shape `[piece_id, status, caption, asset_url, alt_text, owner_action]` matches the as-built writer `app/tools/sheets_server.py:43-50`; Audit 7-col `[piece_id, verb, status, detail, actor, ts, operator_id]` matches `sheets_server.py:94-102` and `_event_from_row` (`export_floor_state.py:102-131`, pads short rows). (See MINOR-2 for the one legacy 3-col audit writer) |
| 3b | `needs_you` derivation | **PASS** | `export_floor_state.py:214-220`: Approval Queue + blank Owner-Action → needs_you "Waiting at the human gate"; any fail-closed/breaker/publish-fail/escalation marker from audit (`_BLOCK_PATTERNS` L38-43, `_exception_from_events` L134-139) → needs_you + exception. `test_build_state_needs_you` (`test_p5_b.py:97-112`) covers all four cases incl. "Owner Action already written → not needs_you" — PASSED |
| 3c | Trust math vs kit `trust_threshold`, recommendation-only | **PASS** | `_trust_for_brand` (`export_floor_state.py:142-171`) reads `kit["trust_threshold"]` over defaults, computes window/rate/edits/violations; `met` requires the full window. Tests `test_build_state_trust_math` + `test_trust_not_met_on_violation_or_thin_window` (`test_p5_b.py:115-135`) — PASSED. **No code path flips** `approval_mode`/`auto_publish_enabled`: grep across `tools/export_floor_state.py`, `tools/floor_serve.py`, `tools/apply_floor_actions.py`, `ui/studio-floor/app.js` → reads only (`export_floor_state.py:160-161`, `app.js:601-603`); zero assignments/updates. Server verb set structurally excludes any trust verb (`floor_serve.py:30-34`) |
| 3d | Env-leak test plants a sentinel and proves the writer REFUSES | **PASS** | `test_write_state_asserts_on_leak` (`test_p5_b.py:261-266`): `monkeypatch.setenv("SENTINEL_SECRET", …)` then **injects the sentinel into a caption** and asserts `write_state` raises `AssertionError` — the refusal path in `_assert_no_env_leak` (`export_floor_state.py:323-328`, every env value ≥8 chars) called from `write_state` (`export_floor_state.py:331-340`) *before* any bytes hit disk. Companion `test_no_env_value_lands_in_projection` (`test_p5_b.py:251-258`) proves the clean path. Both executed → PASSED |
| 3e | gspread/config imports only inside `main()` | **PASS** | Module top-level imports are stdlib only (`export_floor_state.py:14-19`); `import gspread` L372, `from app.agents.config import SHEET_ID` L378, `import yaml` L396 — all inside `main()`; `datetime` inside `build_state` (L177). Empirically proven: the test suite imports the module via `importlib` on this machine, where `gspread` is **not installed** (`ModuleNotFoundError` confirmed), and passes |
| 4a | `floor_serve.py` binds 127.0.0.1 only | **PASS** | `HOST = "127.0.0.1"` (`tools/floor_serve.py:26`), `ThreadingHTTPServer((HOST, PORT), …)` (L204). **Live-verified:** server started; `lsof -iTCP:8787 -sTCP:LISTEN` → `TCP 127.0.0.1:8787 (LISTEN)` (not `*:8787`); `GET /` served index.html (200, 28,355 B) |
| 4b | POST /action validates the verb set | **PASS** | `VALID_ACTIONS = {approve, request_changes, reject}` (`floor_serve.py:30-34`); rejection at `handle_action` L120-124. **Live-verified:** `POST {"action":"set_status"}` → `400 {"error": "action must be one of ['approve', 'reject', 'request_changes']"}`; unknown path → 404; malformed JSON → 400. `test_invalid_action_is_400` also PASSED |
| 4c | Writes ONLY Owner-Action column + 7-col audit append | **PASS** | `GspreadSheetClient.set_owner_action` updates a single cell in col F only (`floor_serve.py:45,56-61`); `append_audit` appends (L63-68); `handle_action` writes exactly `[piece_id, "owner_<verb>", "", detail, "human", ts, operator_id]` (L150-153) — the 7-col shape. No method on the client can write Status (class has none; guard at L71-78 asserts none is exposed). `test_approve_writes_owner_action_and_audit_never_status` (`test_p5_b.py:188-206`) asserts exact call sequence, the 7 audit fields, and zero status surface — PASSED |
| 4d | Structural test: a Status-writing client is refused | **PASS** | `test_status_writing_client_is_refused` (`test_p5_b.py:237-246`): a `BadClient` exposing `set_status` → `pytest.raises(AssertionError)` from `_assert_no_status_writer` (`floor_serve.py:71-78`), invoked *before* any write (`handle_action` L147). Executed → PASSED. (See MINOR-3: guard is name-heuristic + bare `assert`) |
| 4e | No-creds path: 202 + queue to actions.jsonl; applier marks applied w/o deleting history | **PASS** | `handle_action` client-None branch → append JSONL record `applied:false`, return `202 {queued:true}` (`floor_serve.py:135-145`); `test_missing_creds_queues_to_jsonl` PASSED. `apply_floor_actions.apply_actions` (`tools/apply_floor_actions.py:37-69`): skips `applied` records (L42-43), sets `applied=true` + `applied_at` in place (L65-66), failures annotated `apply_error` and retained; `save_records` (L32-34) rewrites all records — **nothing is ever deleted**; the same `_assert_no_status_writer` + Owner-Action-only client is reused (L20, 39, 56-60). Code-verified (no live Sheets on this machine; no-creds path returns 1 "stay queued", L100-103) |
| 5a | Trust ladder display-only | **PASS** | `renderTrust` (`app.js:583-615`) renders HTML only — no controls, no POST; when the window is met it surfaces **only a recommendation**: "Enabling is an owner-only Vibe-Diff action taken outside this console; nothing flips here" (`app.js:594-595`) + the explicit display-only note (`app.js:613-614`). Combined with 3c (zero write paths) and 4b (server verb set): trust cannot flip through this console |
| 5b | Connection chip honest — no fake "Live" | **PASS** | Chip states: `◌ Snapshot — exported <age> ago` / `◌ Demo snapshot — exported <age> ago` / `▲ Offline — showing last-known` (`app.js:219-225`); tooltip declares the poll-of-an-export mechanic (`index.html:21`). grep for a "Live" chip state across app.js/index.html → none. Matches deviation `specs/deviation_log.md:254` ("connection chip honestly displays snapshot age") |
| 5c | Replay/follow labeled as reconstruction from the audit record | **PASS** | `journeyHtml` header: "Replay (from audit record — nothing re-runs)" (`app.js:628`, class `replay-note`, `styles.css:496`); journey is rendered purely from recorded events (`pieceEvents`, `app.js:105-108, 618-629`) — no dispatch, no fetch |
| 5d | Sienna human accent consistent; deviation logged | **PASS** | `--human` = `#DD7A50` dark / `#A6491C` light (`styles.css:35,61`), applied at the desk station (`styles.css:258-259,278,315`), feed "you" rows (`styles.css:454-455`), org card (`app.js:507-509`), actor hue (`app.js:22-24`). Zero violet/purple values anywhere (grep hits are only the deviation comments, `styles.css:3-8,308`, `app.js:22-23`). Deviation present: `specs/deviation_log.md:257-258` ("human accent is **warm sienna, replacing the spec's violet** everywhere") |
| 6 | Tests: local 13 + CI green at HEAD | **PARTIAL** | The verbatim required local run **errors 13/13 at fixture setup** — caused NOT by P5-B but by a P4-B cross-track change: the autouse fixture `app/tests/conftest.py:15-21` (commit `18af224`) imports `app.pipeline` → `google.adk` for every test, and this machine lacks the live stack. With a validator-side `sys.modules` shim for `app.pipeline` only (repo untouched), **all 13 P5-B tests PASS in 0.02s** (verbatim below). CI at HEAD `97938de` is **green** and runs the full suite (`.github/workflows` CI job: `pip install -r requirements.txt` + `pytest app/tests/`): run **28783468553** (CI, success, 27s) and **28783468069** (verify-build-view, success). See MAJOR-1 |

**Verdict count: 17 PASS · 1 PARTIAL (item 6, cross-track cause) · 0 FAIL**

---

## Test runs (verbatim tails)

### Required local command (fails — cross-track conftest, see MAJOR-1)

`python3 -m pytest app/tests/test_p5_b.py -v` @ `97938de`:

```
>   from google.adk import runners
E   ModuleNotFoundError: No module named 'google'

app/pipeline.py:4: ModuleNotFoundError
=========================== short test summary info ============================
ERROR app/tests/test_p5_b.py::test_build_state_pieces_and_monotonic_seq - Mod...
ERROR app/tests/test_p5_b.py::test_build_state_needs_you - ModuleNotFoundErro...
ERROR app/tests/test_p5_b.py::test_build_state_trust_math - ModuleNotFoundErr...
ERROR app/tests/test_p5_b.py::test_trust_not_met_on_violation_or_thin_window
ERROR app/tests/test_p5_b.py::test_demo_state_valid - ModuleNotFoundError: No...
ERROR app/tests/test_p5_b.py::test_inline_demo_state_mirrors_canonical_fixture
ERROR app/tests/test_p5_b.py::test_approve_writes_owner_action_and_audit_never_status
ERROR app/tests/test_p5_b.py::test_invalid_action_is_400 - ModuleNotFoundErro...
ERROR app/tests/test_p5_b.py::test_missing_creds_queues_to_jsonl - ModuleNotF...
ERROR app/tests/test_p5_b.py::test_status_writing_client_is_refused - ModuleN...
ERROR app/tests/test_p5_b.py::test_no_env_value_lands_in_projection - ModuleN...
ERROR app/tests/test_p5_b.py::test_write_state_asserts_on_leak - ModuleNotFou...
ERROR app/tests/test_p5_b.py::test_ui_is_self_contained - ModuleNotFoundError...
============================== 13 errors in 0.08s ==============================
```

### Same suite with a validator-side `app.pipeline` shim (P5-B substance — passes)

Shim: a scratchpad pytest plugin pre-registering a stub `app.pipeline` in `sys.modules` (the P5-B tests never touch the pipeline; the shim only neutralizes the unrelated conftest import). Repo untouched.

```
app/tests/test_p5_b.py::test_build_state_pieces_and_monotonic_seq PASSED [  7%]
app/tests/test_p5_b.py::test_build_state_needs_you PASSED                [ 15%]
app/tests/test_p5_b.py::test_build_state_trust_math PASSED               [ 23%]
app/tests/test_p5_b.py::test_trust_not_met_on_violation_or_thin_window PASSED [ 30%]
app/tests/test_p5_b.py::test_demo_state_valid PASSED                     [ 38%]
app/tests/test_p5_b.py::test_inline_demo_state_mirrors_canonical_fixture PASSED [ 46%]
app/tests/test_p5_b.py::test_approve_writes_owner_action_and_audit_never_status PASSED [ 53%]
app/tests/test_p5_b.py::test_invalid_action_is_400 PASSED                [ 61%]
app/tests/test_p5_b.py::test_missing_creds_queues_to_jsonl PASSED        [ 69%]
app/tests/test_p5_b.py::test_status_writing_client_is_refused PASSED     [ 76%]
app/tests/test_p5_b.py::test_no_env_value_lands_in_projection PASSED     [ 84%]
app/tests/test_p5_b.py::test_write_state_asserts_on_leak PASSED          [ 92%]
app/tests/test_p5_b.py::test_ui_is_self_contained PASSED                 [100%]

============================== 13 passed in 0.02s ==============================
```

### CI at HEAD (full suite — not run locally per instructions)

`gh run list --repo RenegadeRocks/agent-atelier --limit 2`:

```
completed  success  P4-B Final Validation and Compliance  CI                 main  push  28783468553  27s  2026-07-06T10:00:24Z
completed  success  P4-B Final Validation and Compliance  verify-build-view  main  push  28783468069  12s  2026-07-06T10:00:24Z
```

The CI job installs `requirements.txt` and runs `pytest app/tests/` — so the green run **includes the 13 P5-B tests**.

### Live server smoke (this validator)

`tools/floor_serve.py` started with no creds/gspread → bind `127.0.0.1:8787` confirmed via lsof; `GET /` → 200 (28,355 B index.html); `POST /action {"action":"set_status"}` → 400 with the verb-set error; `POST /other` → 404; malformed JSON → 400. Server stopped; `ui/studio-floor/data/` unchanged (only `demo-state.json` — no residue written).

---

## Findings

### BLOCKER

*None.*

### MAJOR

1. **The P5-B deterministic suite can no longer run standalone without the live stack — the contract-mandated local verification fails verbatim (cross-track cause: P4-B).** `app/tests/conftest.py:15-21` (autouse fixture `mock_semantic_review_judge`, added in P4-B commit `18af224`) does `import app.pipeline` for **every** non-live test; `app/pipeline.py:4` imports `google.adk` (plus `dotenv` and the full agent stack). Result: `pytest app/tests/test_p5_b.py` errors 13/13 at setup on any machine without the live deps — directly contradicting the P5-B test file's own design contract ("deterministic tests — no network, no live creds", `app/tests/test_p5_b.py:1`) and the build-protocol's local-full-suite-before-push rule for dep-light machines. The P5-B code itself is not at fault (13/13 pass when only that import is neutralized; CI green). **Fix suggestion (for the builder, not applied):** guard the fixture — `pipeline = sys.modules.get("app.pipeline")` or try/except ImportError, or scope the fixture to the pipeline test modules instead of autouse-global.

### MINOR

1. **The fixture's `"demo": true` flag is not honored as a defense-in-depth signal.** `S.demo` is set purely by *load path* (`app.js:161-187`); the fixture field (`data/demo-state.json` top level, `index.html:178`) is never read. If demo content were ever copied/served as `data/state.json`, Floor Actions would enable against fictional `piece_id`s (a 502/KeyError at the sheet, but a click-into-failure path the P5-B round-2/3 deviation set out to remove). One-line hardening: `demo = demo || data.demo === true` in `poll()`.
2. **One legacy 3-col audit writer mis-parses under the projection.** `app/tools/sheets_server.py:63` appends `[piece_id, "publish_refused", "<message>"]` — the human-readable message lands in the audit row's *status/stage* position. `_event_from_row` (`tools/export_floor_state.py:102-131`) therefore renders such events with the message in the stage chip and an empty detail. Severity/exception mapping stays correct (`alert` / `Publish-Failed` via `_BLOCK_PATTERNS`), so nothing is hidden — but the "where & why" evidence for a refused publish displays in the wrong slot. Fix belongs in `sheets_server.py` (write the 7-col shape it itself defines at L94-102).
3. **`_assert_no_status_writer` is a name-based heuristic using bare `assert`** (`tools/floor_serve.py:71-78`): stripped under `python -O`, and a hostile client could write Status through a method not containing "status". Acceptable as the v1 structural guard it is documented to be (the real live client simply has no such method), but worth an explicit exception (not `assert`) at P6.
4. **`ui/studio-floor/data/state.json` and `actions.jsonl` are runtime artifacts with no `.gitignore` entry** (checked: `git check-ignore` matches neither). A real exported projection (brand captions, asset URLs) or a queued-actions file could be committed by accident later. Add both to `.gitignore`.
5. **`POST /action` has no origin check.** Bound to 127.0.0.1 and JSON-preflight blocks ordinary cross-origin fetch, but a crafted `enctype="text/plain"` form on a malicious page can produce a parseable JSON body against `localhost:8787` (classic localhost-CSRF). Low risk in the v1 owner-laptop/demo posture; note for the P5-A/P6 hardening pass (check `Origin`/`Sec-Fetch-Site`, or require a local token).
6. **Doc drift:** the P5-B v1 deviation entry says "12 deterministic tests" (`specs/deviation_log.md:255`); the file contains **13**.

---

## Deviation-log conformance (audited as-built vs the two 2026-07-06 P5-B entries)

- Poll-based snapshot console, no WebSocket relay — conforms (`app.js:7-9,153-203`); chip wording honest (5b).
- No StudioEvent emitters; in-flight = last-known by construction — conforms (export derives events solely from the Audit sheet, `export_floor_state.py:180-191`).
- Floor Actions v1 = Approve/Request-changes/Reject as 1:1 Owner-Action writes + audit appends; Unstick/Edit-task/Re-route/Inject-note/Post-Kit rendered disabled with "wires in at P5-A / P3" tooltips — conforms (`floor_serve.py:30-34,150-153`; `app.js:715-724`).
- Audit 4→7 cols additive — conforms (`floor_serve.py:36-37,151-153`; `sheets_server.py:94-102`; MINOR-2 is the one pre-existing 3-col writer).
- `rev` captured/audited, not enforced — conforms (`app.js:761` sends `rev`; `floor_serve.py:148` records it in detail; no rev check — logged as the P5-A item).
- Stack deviation (no Node; vanilla SPA + stdlib server) — conforms; contract ON-FAIL blesses the approachable subset (`specs/contracts/P5-B.md:14`).
- Sienna-for-violet owner-taste deviation — logged (`specs/deviation_log.md:257-258`) and applied consistently (5d).
- Demo-action safety (disabled with visible reason on demo/file://) — conforms (2b).
- UTF-8 `read_text` fix — conforms (`export_floor_state.py:348,352`, `apply_floor_actions.py:26`, `floor_serve.py` writes with explicit encoding).

## Prior-validator-escape check (content, not existence)

Per the P5-A lesson (`specs/deviation_log.md:263-266`), this audit opened and verified deliverable *contents*: the demo fixture is 8 fully-populated pieces / 29 narrative events / 3 brands with real captions (incl. Hindi), CD notes, and permalinks — not placeholders; the inline block is byte-equivalent as parsed JSON to the canonical file; the served index.html is the real 28 KB console; the tests assert behavior (call sequences, refusal paths, sentinel leaks), not existence.
