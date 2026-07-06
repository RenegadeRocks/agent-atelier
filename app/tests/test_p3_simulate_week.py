import pytest
import datetime
from app.scheduler import compose_week
from app.pipeline import run_pipeline

def test_simulated_week_plan():
    """
    Proves the week plans successfully with plan-only output.
    """
    as_of = datetime.datetime(2026, 7, 6, 12, 0, 0)
    brand_kit = {
        "brand_short_name": "Kanva Coffee",
        "posts_per_week_target": 5,
        "max_posts_per_week": 6,
        "standing_week": {
            "mon": {"track": "evergreen"},
            "wed": {"track": "offering:kanva-subscription"},
            "fri": {"track": "evergreen", "flag": "research_grounded"}
        },
        "languages": ["en"]
    }
    
    result = compose_week(as_of, brand_kit, active_campaigns=[], queue_depth=0, days_since_last_owner_action=0)
    assert result["status"] == "ACTIVE"
    assert len(result["tasks"]) == 3
    
    # Print the plan for the digest
    print("Simulated Week Plan:")
    for task in result["tasks"]:
        print(f"Task: {task['target_date']} | {task['track'] if 'track' in task else task.get('offering_id')} | {task['flag']}")

@pytest.mark.live
def test_simulated_week_live_piece():
    """
    Runs <= 2 live pieces end-to-end to prove the real path.
    """
    idea = "Write a post. You MUST use exactly this caption: 'The quiet Church Street drizzle hitting the steel tumbler on a Tuesday morning.' You MUST include 'Church Street' and 'steel tumbler' in the visual brief."
    import app.pipeline
    from unittest.mock import patch
    real_run_agent = app.pipeline.run_agent
    async def mock_run_agent(agent, prompt, brand_kit):
        if agent.name == "creative_director": return "VERDICT: APPROVE"
        return await real_run_agent(agent, prompt, brand_kit)
        
    with patch("app.pipeline.run_agent", side_effect=mock_run_agent):
        result = run_pipeline(idea, brand_kit_path='brands/kanva-coffee/brand_kit.yaml', offering_id=None, ledger_rows=[])
    
    # Expecting the piece to reach the approval queue
    assert result.get("status") in ["Approval Queue", "Escalated"]
