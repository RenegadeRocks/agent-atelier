import os
from app.approval_poller import get_google_sheets_client, run_poller_tick
from app.agents.config import SHEET_ID
import uuid

def run_demo():
    gc = get_google_sheets_client()
    sh = gc.open_by_key(SHEET_ID)
    try:
        ws = sh.worksheet("Queue")
    except Exception:
        ws = sh.sheet1
        
    piece_id = f"DEMO-P5-A-{uuid.uuid4().hex[:6].upper()}"
    row_data = [piece_id, "Approval Queue", "This is a demo caption for P5-A.", "http://example.com/demo.jpg", "Demo Alt", "Approve"]
    
    print("Appending demo row (Owner Action = Approve)...")
    ws.append_row(row_data)
    
    print("Running poller tick 1...")
    run_poller_tick()
    
    cell = ws.find(piece_id)
    row = ws.row_values(cell.row)
    status = row[1]
    print(f"Status after tick 1: {status}")
    
    print("Setting Owner Action to 'Mark posted'...")
    ws.update_cell(cell.row, 6, "Mark posted")
    
    print("Running poller tick 2...")
    run_poller_tick()
    
    row = ws.row_values(cell.row)
    status = row[1]
    print(f"Status after tick 2: {status}")
    print("Demo pass complete. Post Kit created in brands/aol/handoff.")
    
if __name__ == "__main__":
    run_demo()
