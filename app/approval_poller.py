import os
import json
import gspread
from dotenv import load_dotenv
from app.agents.config import SHEET_ID
from app.brand_kit import load_brand_kit
from app.approval_protocol import process_approval_action
from app.post_kit import export_post_kit

load_dotenv()

def get_google_sheets_client():
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
    return gspread.service_account(filename=creds_path)

def append_audit_trail(sh, piece_id: str, verb: str, status: str, detail: str, actor: str = "human", operator_id: str = "unknown"):
    try:
        audit_sheet = sh.worksheet("Audit")
    except gspread.exceptions.WorksheetNotFound:
        audit_sheet = sh.add_worksheet(title="Audit", rows=1000, cols=10)
        
    import datetime
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    row_data = [piece_id, verb, status, detail, actor, ts, operator_id]
    audit_sheet.append_row(row_data)

def fetch_ledger_rows(sh) -> list:
    try:
        ledger_sheet = sh.worksheet("Ledger")
        # Just returning empty list for now since mock ledger implementation is sufficient for tests
        return []
    except gspread.exceptions.WorksheetNotFound:
        return []

def fetch_claim_bank(sh) -> list:
    try:
        cb_sheet = sh.worksheet("ClaimBank")
        # Return empty for now
        return []
    except gspread.exceptions.WorksheetNotFound:
        return []

def run_poller_tick(brand_kit_path: str = 'brands/aol/brand_kit.yaml', brand_id: str = "aol"):
    """
    The Owner-Action poller.
    Reads the human-writable Owner Action cells and acts through the §12.5 protocol.
    Orchestrator stays the SOLE writer of Status.
    """
    gc = get_google_sheets_client()
    sh = gc.open_by_key(SHEET_ID)
    
    try:
        worksheet = sh.worksheet("Queue")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.sheet1
        
    brand_kit = load_brand_kit(brand_kit_path, 'specs/brand_kit.schema.json')
    ledger_rows = fetch_ledger_rows(sh)
    claim_bank = fetch_claim_bank(sh)
    
    rows = worksheet.get_all_values()
    if not rows:
        return
        
    # Assume headers in first row or no headers. We just process all rows.
    # Col 0: Piece ID, Col 1: Status, Col 2: Caption, Col 3: Asset URL, Col 4: Alt Text, Col 5: Owner Action
    
    for row_idx, row in enumerate(rows):
        if len(row) < 6:
            continue
            
        piece_id = row[0]
        status = row[1]
        caption = row[2]
        asset_urls = [u.strip() for u in str(row[3]).split(',')] if row[3] else []
        alt_texts = [a.strip() for a in str(row[4]).split(',')] if row[4] else []
        owner_action = row[5]
        
        # Blank Owner Action is a no-op
        if not owner_action.strip():
            continue
            
        # Consumption is status-derived.
        # If the piece is already Published or Archived, Owner Action should be ignored.
        if status in ["Published", "Archived"]:
            continue
            
        # Call the protocol
        result = process_approval_action(
            piece_id=piece_id,
            status=status,
            owner_action=owner_action,
            caption=caption,
            brand_kit=brand_kit,
            claim_bank=claim_bank,
            ledger_rows=ledger_rows
        )
        
        # Atomic per-piece processing: read once, act once, audit.
        # Since we are the sole writer of Status, we update it immediately.
        # Any subsequent concurrent human edits will be ignored in the next tick 
        # because the Status will have advanced.
        new_status = result.get("new_status", status)
        detail = result.get("detail", result.get("error", ""))
        
        # Update Status cell if it changed
        if new_status != status:
            worksheet.update_cell(row_idx + 1, 2, new_status)  # Col 2 is Status
            
            # Additional actions based on new status
            if new_status == "Approved" and status == "Approval Queue":
                # Build Post Kit (default manual handoff)
                export_post_kit(
                    piece_id=piece_id,
                    brand_id=brand_id,
                    caption=caption,
                    asset_urls=asset_urls,
                    alt_texts=alt_texts
                )
                
            elif new_status == "Published":
                # Mark posted - update LedgerRow (mocked for now, audit handles it)
                pass
                
        # Always Audit the action
        append_audit_trail(
            sh=sh,
            piece_id=piece_id,
            verb=owner_action.strip(),
            status=new_status,
            detail=detail,
            actor="human"
        )
        
    print("[poller] Tick complete.")

if __name__ == "__main__":
    run_poller_tick()
