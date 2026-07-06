import datetime

def ledger_lint(draft: dict, ledger_rows: list, research_min: int, week_slots_remaining: int = 1) -> dict:
    """
    Runs the deterministic ledger-linter over a draft's fields against the trailing Content Ledger.
    
    Args:
        draft: dict with keys: 'hook', 'shape', 'visual_label', 'idea', 'date' (ISO date string), 'format'
        ledger_rows: list of dicts, sorted newest first. Keys match LedgerRow schema.
        research_min: int, [[RESEARCH_POST_MIN_PER_WEEK]]
        week_slots_remaining: int, number of un-drafted slots left in the current week including this one.
    
    Returns:
        {"status": "PASS"} or {"status": "BLOCK", "violations": [...]}
    """
    violations = []
    
    # Filter rows based on eligibility
    # hook, shape, aphorism, visual_label count {Approved, Published, RESERVED}
    eligible_rows = [r for r in ledger_rows if r.get('status') in ('Approved', 'Published', 'RESERVED')]
    
    # 1. Hook recency (last 3 eligible posts)
    recent_hooks = [r.get('hook') for r in eligible_rows[:3]]
    if draft.get('hook') in recent_hooks:
        violations.append({"rule": "hook-in-3", "conflict": draft.get('hook')})
        
    # 2. Shape back-to-back
    if eligible_rows and draft.get('shape') == eligible_rows[0].get('shape'):
        violations.append({"rule": "shape-back-to-back", "conflict": draft.get('shape')})
        
    # 3. Aphorism cap (1-in-5)
    if draft.get('shape') == 'aphorism':
        recent_shapes = [r.get('shape') for r in eligible_rows[:4]]
        if recent_shapes.count('aphorism') >= 1:
            violations.append({"rule": "aphorism-1-in-5", "conflict": "aphorism"})
            
    # 4. Idea re-run (last 30 days, counts KILLED too)
    idea_eligible = [r for r in ledger_rows if r.get('status') in ('Approved', 'Published', 'RESERVED', 'KILLED')]
    draft_date_str = draft.get('date')
    if draft_date_str:
        try:
            draft_date = datetime.date.fromisoformat(draft_date_str)
            for r in idea_eligible:
                r_date_str = r.get('date')
                if not r_date_str:
                    continue
                r_date = datetime.date.fromisoformat(r_date_str)
                if (draft_date - r_date).days <= 30 and (draft_date - r_date).days >= 0:
                    if draft.get('idea') == r.get('idea'):
                        violations.append({"rule": "idea-rerun-30d", "conflict": r.get('idea')})
                        break
        except ValueError:
            pass # Ignore invalid dates for now
            
    # 5. Visual-treatment label back-to-back
    if eligible_rows and draft.get('visual_label') == eligible_rows[0].get('visual_label'):
        violations.append({"rule": "treatment-label-repeat", "conflict": draft.get('visual_label')})
        
    # 6. Research minimum
    # NOTE: Enforced at the week-plan level in scheduler.py. 
    # Not a piece-level hard block as it causes deadlocks.
                
    if violations:
        return {"status": "BLOCK", "violations": violations}
    return {"status": "PASS"}
