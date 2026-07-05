# P1-B Validation Report

## Verdict Table

| Item | Status | Evidence |
|---|---|---|
| Real MCP implementations, mocks ONLY inside CI test fixtures | **PASS** | `app/tools/sheets_server.py:33`, `app/tools/caption_compose_server.py:22`, `app/tests/test_p1_b.py:20` |
| §12.2 publish semantics (queue vs append-only audit, publish-once guard) | **PASS** | `app/tools/sheets_server.py:52-107` |
| Sheet schema matches spec (piece_id, status, caption, asset URL, alt text, Owner-Action) | **PASS** | `app/tools/sheets_server.py:43-50` |
| Extraction is fenced-JSON only, bounces loudly via draft_loop_count | **PASS** | `app/pipeline.py:129-166` |
| Output-invariant tests exist and assert specified conditions | **PASS** | `app/tests/test_p1_b.py:274-313` |
| OCR gate is an injectable dependency with escalation at 3 failed attempts | **PASS** | `app/tools/caption_compose_server.py:44`, `app/pipeline.py:233`, `app/tests/test_p1_b.py:163` |
| Compositor uses paperclip geometry, luminance theme, 4:5 1080×1350, no `ImageFont.load_default()` | **PASS** | `app/tools/caption_compose_server.py:68-86`, `116` (banned in error), `155-160` |
| Live tests carry `@pytest.mark.live` with keyless auto-skip via conftest | **PASS** | `app/tests/test_p1_b.py:120`, `app/tests/conftest.py:8-13` |
| Deviation log records specific items | **PASS** | `specs/deviation_log.md:19-29` |
| requirements.txt pinned; evidence artifacts present | **PASS** | `requirements.txt:1-12`, `app/tests/evidence/` |

---

## Findings

**All items have been verified and now PASS against HEAD (`2b878c3`).** 
The previous BLOCKER, MAJOR, and MINOR findings have been fully resolved:
- The publish-once guard and queue/audit logic has been correctly implemented in `sheets_server.py`.
- The sheet schema exactly matches the spec, including the `Owner-Action` column.
- The `test_p1_b.py` suite now explicitly asserts that the composited headline matches `hook_text` verbatim.
- The deviation log correctly marks rows 8-19 and includes the token-resolution stub entry.
