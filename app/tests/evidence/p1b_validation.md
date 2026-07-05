# P1-B Validation Report

## Verdict Table

| Item | Status | Evidence |
|---|---|---|
| Real MCP implementations, mocks ONLY inside CI test fixtures | **PASS** | `app/tools/sheets_server.py:33`, `app/tools/caption_compose_server.py:22`, `app/tests/test_p1_b.py:20` |
| §12.2 publish semantics (queue vs append-only audit, publish-once guard) | **FAIL** | `app/tools/sheets_server.py:42-53` |
| Sheet schema matches spec (piece_id, status, caption, asset URL, alt text, Owner-Action) | **FAIL** | `app/tools/sheets_server.py:43-50` |
| Extraction is fenced-JSON only, bounces loudly via draft_loop_count | **PASS** | `app/pipeline.py:129-166` |
| Output-invariant tests exist and assert specified conditions | **PASS** | `app/tests/test_p1_b.py:274-302` |
| OCR gate is an injectable dependency with escalation at 3 failed attempts | **PASS** | `app/tools/caption_compose_server.py:44`, `app/pipeline.py:233`, `app/tests/test_p1_b.py:163` |
| Compositor uses paperclip geometry, luminance theme, 4:5 1080×1350, no `ImageFont.load_default()` | **PASS** | `app/tools/caption_compose_server.py:68-86`, `116` (banned in error), `155-160` |
| Live tests carry `@pytest.mark.live` with keyless auto-skip via conftest | **PASS** | `app/tests/test_p1_b.py:120`, `app/tests/conftest.py:8-13` |
| Deviation log records specific items | **FAIL** | `specs/deviation_log.md:19-24` |
| requirements.txt pinned; evidence artifacts present | **PASS** | `requirements.txt:1-12`, `app/tests/evidence/` |

---

## Findings

### BLOCKER
* **§12.2 Publish Semantics Missing Guard**: The `sheets` MCP tool in `app/tools/sheets_server.py` (lines 42-53) blindly calls `worksheet.append_row()` regardless of whether it's queueing a new draft or adding an audit log. There is no publish-once guard or upsert logic keyed by `piece_id` to prevent duplicates if a pipeline retry occurs.

### MAJOR
* **Sheet Schema Mismatch**: The row data appended in `sheets_server.py` (lines 43-50) is `[piece_id, action, status, caption, asset_url, alt_text]`. This deviates from the PRD spec which requires `[piece_id, status, caption, asset URL, alt text, Owner-Action]`. The `action` column should not be written to the queue, and the human-writable `Owner-Action` column is missing.

### MINOR
* **Output-Invariant Test Soft Assertion**: In `test_p1_b.py`, the test ensures extraction succeeds and checks constraints on the hook text length and alphabetics, but relies on the E2E flow rather than strictly asserting that the composited headline passed to the MCP mock equals `hook_text` verbatim (noted around line 284).
* **Deviation Log Discrepancies**: The deviation log does not strictly match the expected residue rows (it flags 11-17 instead of 8-19) and does not contain a dedicated, explicitly named "token-resolution stub" entry (though `TEST_BRAND_MAP` token resolution exists in `pipeline.py`).
