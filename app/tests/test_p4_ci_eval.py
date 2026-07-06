import pytest
import asyncio
from app.ci_eval_gate import evaluate_golden_set
from app.brand_kit import load_brand_kit

@pytest.mark.live
def test_ci_eval_gate_golden_set():
    brand_kit = load_brand_kit("brands/aol/brand_kit.yaml", "specs/brand_kit.schema.json")
    results = asyncio.run(evaluate_golden_set("specs/golden_set.md", brand_kit))
    
    print(f"CI Eval Gate Results: {results}")
    
    # We do not assert live scores here because P4-A is just baseline measurement
    # The actual passing threshold applies in P4-B after rubric tuning.

def test_ci_eval_gate_stubbed():
    # Prove mechanical soundness of the eval gate
    from unittest.mock import patch
    
    brand_kit = load_brand_kit("brands/aol/brand_kit.yaml", "specs/brand_kit.schema.json")
    
    with patch("app.ci_eval_gate.run_agent") as mock_run:
        async def mock_run_coro(agent, prompt, brand_kit):
            # Stub verdicts to match golden set perfectly (100% agreement, 0 false approve)
            if "observation->turn" in prompt or "claim->meaning" in prompt:
                return "APPROVED"
            return "REJECTED"
        mock_run.side_effect = mock_run_coro
        
        results = asyncio.run(evaluate_golden_set("specs/golden_set.md", brand_kit))
        
        # Perfect harness logic must yield 0 false approve, 100% negative catch, 100% agreement
        assert results["false_approve_count"] == 0
        assert results["negative_catch_rate"] == 1.0
        assert results["agreement_rate"] == 1.0
