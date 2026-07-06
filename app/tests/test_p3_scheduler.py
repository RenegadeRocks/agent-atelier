import datetime
from app.scheduler import compose_week

def test_scheduler_base_composition():
    as_of = datetime.datetime(2026, 7, 6, 12, 0, 0) # Monday
    brand_kit = {
        "brand_short_name": "TestBrand",
        "posts_per_week_target": 3,
        "max_posts_per_week": 5,
        "standing_week": {
            "mon": {"track": "evergreen"},
            "wed": {"track": "offering:offer1"},
            "fri": {"track": "evergreen", "flag": "research_grounded"}
        }
    }
    
    result = compose_week(as_of, brand_kit, active_campaigns=[], queue_depth=0, days_since_last_owner_action=0)
    assert result["status"] == "ACTIVE"
    tasks = result["tasks"]
    assert len(tasks) == 3
    assert tasks[0]["target_date"] == "mon"
    assert tasks[1]["target_date"] == "wed"
    assert tasks[1]["offering_id"] == "offer1"
    assert tasks[2]["target_date"] == "fri"
    assert tasks[2]["flag"] == "research_grounded"

def test_scheduler_backpressure_pause():
    as_of = datetime.datetime(2026, 7, 6, 12, 0, 0)
    brand_kit = {
        "brand_short_name": "TestBrand",
        "posts_per_week_target": 3,
        "max_queue_depth": 5,
        "owner_absence_pause_days": 7,
        "standing_week": {
            "mon": {"track": "evergreen"}
        }
    }
    
    # 6 > max_queue_depth(5), 8 >= owner_absence_pause_days(7) -> Pause
    result = compose_week(as_of, brand_kit, active_campaigns=[], queue_depth=6, days_since_last_owner_action=8)
    assert result["status"] == "PAUSED"
    assert len(result["tasks"]) == 0
    assert result["audit_entry"] is not None
    assert result["audit_entry"]["action"] == "WEEK_PLAN_PAUSED"
    
def test_scheduler_campaign_overlay():
    as_of = datetime.datetime(2026, 7, 6, 12, 0, 0)
    brand_kit = {
        "brand_short_name": "TestBrand",
        "posts_per_week_target": 3,
        "max_posts_per_week": 5,
        "standing_week": {
            "mon": {"track": "evergreen"},
            "wed": {"track": "offering:offer1"}
        }
    }
    campaigns = [
        {
            "id": "camp1",
            "overlay_mode": "add",
            "slots": [
                {"day": "tue", "track": "offering:offer2"}
            ]
        }
    ]
    
    result = compose_week(as_of, brand_kit, active_campaigns=campaigns, queue_depth=0, days_since_last_owner_action=0)
    assert result["status"] == "ACTIVE"
    tasks = result["tasks"]
    assert len(tasks) == 3
    tue_task = next((t for t in tasks if t["target_date"] == "tue"), None)
    assert tue_task is not None
    assert tue_task["campaign_id"] == "camp1"
