import datetime

from app.policy_server import re_gate_human_edit
from app.tools.ledger_lint import ledger_lint

def process_approval_action(
    piece_id: str,
    status: str,
    owner_action: str,
    caption: str,
    brand_kit: dict,
    claim_bank: list,
    ledger_rows: list
) -> dict:
    """
    Processes the Owner Action for a given piece and returns the transition result.
    The orchestrator NEVER overwrites the Owner Action; it only consumes it.
    """
    # Clean up owner_action to match expected terms
    action = str(owner_action).strip().lower()
    
    # State transition validation based on current status
    if status == "Published" or status == "Archived":
        return {"ok": False, "error": f"Piece is already {status}", "new_status": status}

    if status == "Approval Queue":
        if action == "approve":
            # Rider: Re-gate on EVERY Approve
            # 1. Deterministic ledger-lint
            import datetime
            draft_dict = {
                "hook": caption[:50],  # approximate hook
                "shape": "mini-story",
                "visual_label": "real human moment",
                "idea": caption,
                "date": datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
                "format": "single",
                "flag": ""
            }
            lint_res = ledger_lint(draft_dict, ledger_rows, brand_kit.get('research_post_min_per_week', 1))
            if lint_res.get("status") == "BLOCK":
                return {
                    "ok": False, 
                    "error": f"refused_regate: {lint_res.get('violations')}", 
                    "new_status": "Approval Queue"
                }
            
            # 2. Claim grounding and safety fields via Policy Server
            policy_res = re_gate_human_edit(piece_id, caption, brand_kit, claim_bank)
            if policy_res.get("status") == "BLOCK":
                return {
                    "ok": False,
                    "error": f"refused_regate: {policy_res.get('reason')}",
                    "new_status": "Approval Queue"
                }
            
            return {"ok": True, "new_status": "Approved"}
            
        elif action == "reject":
            return {"ok": True, "new_status": "Archived", "detail": "Killed idea"}
            
        elif action == "request changes":
            return {"ok": True, "new_status": "CD Review", "detail": "Owner requested changes"}
            
        elif action == "":
            return {"ok": True, "new_status": status, "detail": "No action"}
            
        else:
            return {"ok": False, "error": f"Unknown action: {owner_action}", "new_status": status}
            
    elif status == "Approved":
        if action == "mark posted":
            return {"ok": True, "new_status": "Published"}
        elif action == "request changes":
            return {"ok": True, "new_status": "CD Review"}
        elif action == "approve":
            # Stale action, already Approved
            return {"ok": True, "new_status": status, "detail": "Stale action, already Approved"}
        elif action == "":
            return {"ok": True, "new_status": status, "detail": "No action"}
        else:
            return {"ok": False, "error": f"Action '{owner_action}' not allowed from Approved status", "new_status": status}
            
    return {"ok": True, "new_status": status}
