import datetime

def ledger_audit(piece_draft: dict, lint_result: dict, asset: dict) -> dict:
    """
    Pre-queue audit and atomic append.
    Asserts a piece has its ledger row, alt text, and a clean lint.
    
    Args:
        piece_draft: dict with keys: date, piece_id, agent, channel_format, idea, hook, shape, visual_label, language, status
        lint_result: dict from ledger_lint.
        asset: dict from visual production, must contain 'alt_text'.
        
    Returns:
        {"status": "PASS", "ledger_row": {...}, "audit_entry": {...}, "queue_item": {...}}
        or {"status": "BOUNCE", "reason": "..."}
    """
    # 1. Assert ledger-row completeness
    required_fields = ['date', 'piece_id', 'agent', 'channel_format', 'idea', 'hook', 'shape', 'visual_label', 'language', 'status']
    for field in required_fields:
        if not piece_draft.get(field):
            return {"status": "BOUNCE", "reason": f"Missing ledger field: {field}"}
            
    # 2. Assert alt text
    if not asset or not asset.get('alt_text'):
        return {"status": "BOUNCE", "reason": "Missing alt_text on asset"}
        
    # 3. Assert clean lint
    if not lint_result or lint_result.get("status") != "PASS":
        return {"status": "BOUNCE", "reason": "Lint not PASS"}
        
    # 4. Atomic append (mock output for caller to actually append)
    ledger_row = {k: piece_draft.get(k) for k in required_fields}
    ledger_row['status'] = 'Approved' # At this stage, it passed CD
    
    # 5. Write the audit entry
    audit_entry = {
        "action": "QUEUE",
        "actor_agent": "Publishing & Operations Agent",
        "target": f"{piece_draft.get('piece_id')}#QUEUE",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    # 6. Build the handoff bundle + queue
    queue_item = {
        "piece_id": piece_draft.get('piece_id'),
        "status": "Approval Queue",
        "asset_url": asset.get('url'),
        "alt_text": asset.get('alt_text'),
        "caption": piece_draft.get('caption', ''),
        "queued_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    return {
        "status": "PASS",
        "ledger_row": ledger_row,
        "audit_entry": audit_entry,
        "queue_item": queue_item
    }
