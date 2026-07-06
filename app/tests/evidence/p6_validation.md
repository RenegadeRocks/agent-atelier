# P6 Validation Report

## Verdict Table

| Requirement | Status | Evidence / Notes |
|---|---|---|
| 1. Multi-brand proof | PASS | `app/tests/test_p6.py` tests `aol`, `kanva-coffee`, and `chuski-club` on the same pipeline with stubs. `grep` across `app/` confirms zero brand-specific conditionals. |
| 2. Audit independence | PASS | `app/tools/post_publish_audit.py` instantiates a fresh `genai.Client()`. Target pieces are sorted by `exception` and `approve_with_edits` first, capped at `[:25]`. |
| 3. The reports are REAL | PARTIAL FAIL | `app/tests/evidence/p6_audit_report.md` now contains actual sampled pieces (18 total) and real escape rate CIs (5.6%). However, `p6_monthly_retro.md` still contains the mocked test string "Found 1 pattern." instead of real mined corrections. |
| 4. Calibration | PASS | `app/tools/weekly_digest.py` computes agreement rate as `((cd_verdicts - owner_overrides) / cd_verdicts) * 100`. |
| 5. Step-0 (`conftest.py`) | PASS | The `mock_semantic_review_judge` fixture wraps the import of `app.pipeline` in a `try/except ImportError` block, allowing it to run standalone. |
| 6. Import architecture | PASS | Fixed. Tools load floor-state via `importlib.util.spec_from_file_location`, with a clear comment explaining that `app/tools` shadows top-level `tools`. |
| 7. Evidence integrity | PASS | `specs/deviation_log.md` correctly logs the "Fabrication of CI Run Verification [P6]" incident with the corrective rule. |
| 8. Deterministic suite | PASS | Full suite run is green (78 passed) after the import architecture fix. |

## Ranked Findings

1. **MAJOR: Monthly retro artifact contains mock output (FAIL 3).** While the audit report was fixed, the committed `app/tests/evidence/p6_monthly_retro.md` still contains the placeholder text ("Found 1 pattern.") generated during older test runs. The real retro tool must be run to generate concrete canon-amendment suggestions.
