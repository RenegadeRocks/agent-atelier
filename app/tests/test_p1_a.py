import pytest
from app.pipeline import run_pipeline

@pytest.mark.live
def test_p1_a_pipeline_flow():
    """
    Scenario: P1-A pipeline flows through all 6 core agents in order
      Given the 6 core agents (ME, Evergreen, Research, CD, Visual, Ops)
      When a test idea is provided for a hard-coded test brand
      Then the idea should flow through PLAN -> DRAFT -> LINT -> REVIEW -> VISUALIZE -> QUEUE
      And the final status should be in Approval Queue
    """
    test_idea = "A test idea for the hard-coded brand"
    
    result = run_pipeline(test_idea)
    
    assert result is not None
    assert result.get("status") == "Approval Queue"
    
    # We will expand this as we build the ADK agents to verify their outputs.
    assert "managing_editor" in result.get("trace", [])
    assert "evergreen_content" in result.get("trace", [])
    assert "research_verification" in result.get("trace", [])
    assert "ledger_lint_stub" in result.get("trace", [])
    assert "creative_director" in result.get("trace", [])
    assert "visual_production" in result.get("trace", [])
    assert "publishing_operations" in result.get("trace", [])
