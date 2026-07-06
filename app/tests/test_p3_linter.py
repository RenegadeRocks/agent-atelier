import datetime
from app.tools.ledger_lint import ledger_lint

def test_linter_hook_in_3():
    # Setup
    ledger_rows = [
        {"status": "Approved", "hook": "myth-flip", "date": "2026-07-01"},
        {"status": "Approved", "hook": "question-that-indicts", "date": "2026-06-30"},
        {"status": "Approved", "hook": "research-reveal", "date": "2026-06-29"},
    ]
    draft = {"hook": "myth-flip", "shape": "mini-story", "visual_label": "candid joy", "idea": "new idea"}
    
    result = ledger_lint(draft, ledger_rows, research_min=1)
    assert result["status"] == "BLOCK"
    assert any(v["rule"] == "hook-in-3" for v in result["violations"])
    
def test_linter_shape_back_to_back():
    ledger_rows = [
        {"status": "Approved", "shape": "mini-story", "date": "2026-07-01"},
    ]
    draft = {"hook": "new-hook", "shape": "mini-story", "visual_label": "candid joy", "idea": "new idea"}
    
    result = ledger_lint(draft, ledger_rows, research_min=1)
    assert result["status"] == "BLOCK"
    assert any(v["rule"] == "shape-back-to-back" for v in result["violations"])

def test_linter_aphorism_1_in_5():
    ledger_rows = [
        {"status": "Approved", "shape": "aphorism", "date": "2026-07-01"},
        {"status": "Approved", "shape": "mini-story", "date": "2026-06-30"},
    ]
    draft = {"hook": "new-hook", "shape": "aphorism", "visual_label": "candid joy", "idea": "new idea"}
    
    result = ledger_lint(draft, ledger_rows, research_min=1)
    assert result["status"] == "BLOCK"
    assert any(v["rule"] == "aphorism-1-in-5" for v in result["violations"])

def test_linter_idea_rerun_30d():
    today_str = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    past_date = (datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=10)).isoformat()
    
    ledger_rows = [
        {"status": "KILLED", "idea": "same idea", "date": past_date},
    ]
    draft = {"hook": "new-hook", "shape": "mini-story", "visual_label": "candid joy", "idea": "same idea", "date": today_str}
    
    result = ledger_lint(draft, ledger_rows, research_min=1)
    assert result["status"] == "BLOCK"
    assert any(v["rule"] == "idea-rerun-30d" for v in result["violations"])

def test_linter_research_min():
    today = datetime.datetime.now(datetime.timezone.utc).date()
    today_str = today.isoformat()
    
    # 0 research posts this week, and this is the last slot
    ledger_rows = [
        {"status": "Approved", "flag": "none", "date": today_str}
    ]
    draft = {"hook": "new-hook", "shape": "mini-story", "visual_label": "candid joy", "idea": "new idea", "date": today_str, "flag": "none"}
    
    result = ledger_lint(draft, ledger_rows, research_min=1, week_slots_remaining=1)
    assert result["status"] == "PASS" # Rule removed as a piece-level hard block

def test_linter_visual_label_back_to_back():
    ledger_rows = [
        {"status": "Approved", "visual_label": "candid joy", "date": "2026-07-01"},
    ]
    draft = {"hook": "new-hook", "shape": "mini-story", "visual_label": "candid joy", "idea": "new idea"}
    
    result = ledger_lint(draft, ledger_rows, research_min=1)
    assert result["status"] == "BLOCK"
    assert any(v["rule"] == "treatment-label-repeat" for v in result["violations"])

def test_linter_pass():
    ledger_rows = [
        {"status": "Approved", "hook": "old-hook", "shape": "list-of-three", "visual_label": "texture", "idea": "old idea", "date": "2026-06-01"},
    ]
    draft = {"hook": "new-hook", "shape": "mini-story", "visual_label": "candid joy", "idea": "new idea", "date": "2026-07-01", "flag": "research_grounded"}
    
    result = ledger_lint(draft, ledger_rows, research_min=1, week_slots_remaining=1)
    assert result["status"] == "PASS"
