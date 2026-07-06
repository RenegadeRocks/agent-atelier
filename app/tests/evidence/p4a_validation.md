# P4-A Validation Report

## Verdict Table

| Component / Requirement | Status | Evidence / File References |
| --- | --- | --- |
| **`policy_server.py` default-deny & fail-closed** | **PASS** | `app/policy_server.py`: `check_structural_gate()` correctly enforces role×tool×environment default-deny. `content_gauntlet()` fails-closed on empty/unconfirmed safety fields and verbatim names exact rules on BLOCK. |
| **Fixture tests per kit-driven scan** | **PASS** | `app/tests/test_p4_policy_server.py`: Contains tests for `claims_forbidden` hit, non-disclosure leak, `cta_forbidden` phrase, comparative claim, and lexicon-triggered quantitative claim (thin bank block). |
| **Zero LLM calls in runtime gates** | **PASS** | `app/policy_server.py`, `app/circuit_breaker.py`, `app/pipeline.py`: No LLM invocations (`run_agent` or otherwise) inside `content_gauntlet` or `check_and_accumulate`. |
| **`circuit_breaker.py` limits** | **PASS** | `app/circuit_breaker.py`: `CircuitBreakerTrip` thrown correctly on token accumulator and iteration caps. Tests in `app/tests/test_p4_circuit_breaker.py` pass. |
| **Sheets Audit worksheet (7-column shape)** | **PASS** | `app/tools/ledger_audit.py`, `app/tools/sheets_server.py`: Audit appended to the EXISTING Sheets Audit worksheet in 7-column shape (`piece_id, verb, status, detail, actor, ts, operator_id`). |
| **Pipeline wiring & `re_gate_human_edit`** | **PASS** | `app/pipeline.py`: Gauntlet runs pre-queue. `app/policy_server.py` exports `re_gate_human_edit` as a callable socket for P5-A. |
| **`ci_eval_gate.py` mechanical test & baseline** | **PASS** | `app/ci_eval_gate.py`: Proven via `test_p4_ci_eval.py::test_ci_eval_gate_stubbed` (100% agreement, 0 false approve). Live baseline scores (4 false approves / 0.00 catch / 33.3%) are recorded in `specs/deviation_log.md`. |
| **`test_p2_a` assertion update (1→2 calls)** | **PASS** | `app/tests/test_p2_a.py:173-174`: Justified in place. Pipeline accurately runs one queue entry + one audit append, maintaining publish-once integrity. |
| **Two new protocol rules in `build-protocol.md`** | **PASS** | `.agents/rules/build-protocol.md`: Contains rules requiring "raw gh output pasted in reports" and "clean tree after completion commits". |
| **Deviation log entries** | **PASS** | `specs/deviation_log.md`: Carries the P4-A Deterministic Gauntlet and P4-A CI Eval Gate Baseline entries for 2026-07-06. |
| **Full deterministic suite green at HEAD** | **FAIL** | `pytest app/tests -m "not live"`: 1 failure. `app/tests/test_p5_b.py::test_demo_state_valid` fails with `UnicodeDecodeError` on Windows due to missing `encoding="utf-8"` in `read_text()`. |

## Ranked Findings

1. **[MAJOR] Deterministic Suite Failure on Windows:** `app/tests/test_p5_b.py::test_demo_state_valid` throws a `UnicodeDecodeError: 'charmap' codec can't decode byte 0x8d in position 645`. The file `UI_DIR / "data" / "demo-state.json"` is being read without specifying `encoding="utf-8"`, causing a failure on Windows systems where the default `cp1252` encoding is used. As a read-only auditor, I am reporting this without fixing it.
2. **[CLEAN] Policy Server & Circuit Breaker Robustness:** The `policy_server.py` correctly adheres to zero-LLM boundaries and stringent fail-closed blocks. The circuit breaker is fully deterministic and tests prove proper token/iteration short-circuiting.
3. **[CLEAN] Audit Integrity:** The append-only audit trail retains its 7-column integrity and uses the existing Sheets worksheet, satisfying the pipeline wiring requirements cleanly.
4. **[CLEAN] Specification Conformance:** The `deviation_log.md` accurately tracks the changes made, and `build-protocol.md` includes the strict new validation guidelines for completion commits.
