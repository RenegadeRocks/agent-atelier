# P2-A Validation Report

| Item | Status | Evidence |
|---|---|---|
| 1. Resolver correctness (`app/resolver.py`) | PASS | `app/resolver.py:240` checks Brand Kit → Env → Default. L202-L221 routes `[[SECRET:*]]` exclusively to `AUTH` and blocks in `MODEL`. L253 catches recursion. L248 fails closed on missing required. |
| 2. Fail-closed loader (`app/brand_kit.py`) | PASS | `app/brand_kit.py:18` enforces JSON schema. L20-L27 raises `ValueError` if a safety field is empty despite `*_confirmed: true`. |
| 3. Kit faithfulness — Kanva | PASS | `brands/kanva-coffee/brand_kit.yaml` L29-L44 faithfully matches `demo/brand-packs/kanva-coffee/intake-answers.md` safety fields verbatim. Wordmark is "KANVA COFFEE WORKS" (L75). |
| 4. Kit faithfulness — AOL | PASS | `brands/aol/brand_kit.yaml` L56-59 correctly restores `non_disclosure_rules`. Wordmark is "ART OF LIVING LUDHIANA". `git log -p` confirms no unexplained blanking at HEAD. |
| 5. `TEST_BRAND_MAP` eradicated | PASS | Eradicated from `app/pipeline.py`. No occurrences found outside `deviation_log.md`. `specs/agents/` instructions still properly carry `[[TOKENS]]`. |
| 6. Compositor brand layer | PASS | `app/tests/test_p2_a.py:79-121` (`test_compositor_uses_brand_kit`) reads `wordmark_text` and `accent_light_bg` directly FROM the loaded kit rather than hardcoding. |
| 7. `piece_id` per §17 | PASS | `app/pipeline.py:56-58` mints `<slug>-<uuid>` once before the pipeline loop. Stable across retries. |
| 8. Single queue write per run | PASS | `app/pipeline.py:199-204` continues the loop without queuing on OCR fail. `test_p2_a.py:128-182` (`test_pipeline_ocr_retry_logic`) asserts 1 drive upload and 1 stable queue write. |
| 9. Live-test hygiene | PASS | `test_p1_a.py`, `test_p1_b.py`, `test_p2_a.py` all correctly apply `@pytest.mark.live` to E2E runs. HEAD commit `d1341f93a9436beb3a7669d10347d79db7e5a2b5`. |
| 10. Deviation log | **FAIL** | `specs/deviation_log.md:157-161` mentions rows 32–35, `desired_feeling`, and golden-set REJECT #1, but is completely missing the Kanva kit-derivation defect. |

## Findings

- **BLOCKER**: Item 10 — `specs/deviation_log.md` is missing the required conscious-deviation entry for the Kanva kit-derivation defect. All conscious deviations must be logged per PRD §18.4.4.
