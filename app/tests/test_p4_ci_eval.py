import pytest
import asyncio
from app.ci_eval_gate import evaluate_golden_set
from app.brand_kit import load_brand_kit

@pytest.mark.live
def test_ci_eval_gate_golden_set():
    brand_kit = load_brand_kit("brands/aol/brand_kit.yaml", "specs/brand_kit.schema.json")
    results = asyncio.run(evaluate_golden_set("specs/golden_set.md", brand_kit))
    
    print(f"CI Eval Gate Results: {results}")
    
    assert results["false_approve_count"] == 0, f"Failed: false_approve_count is {results['false_approve_count']}"
    assert results["negative_catch_rate"] == 1.0, f"Failed: negative_catch_rate is {results['negative_catch_rate']}"
    assert results["agreement_rate"] >= 0.87, f"Failed: agreement_rate is {results['agreement_rate']} (threshold 0.90, soft 0.87)"
