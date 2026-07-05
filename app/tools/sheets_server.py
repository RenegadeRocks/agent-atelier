import os
import json
import gspread
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from dotenv import load_dotenv

load_dotenv()
from app.agents.config import SHEET_ID

server = FastMCP(name="sheets")
server.tool_name = "sheets"

from pathlib import Path
schema_path = Path(__file__).parent.parent.parent / "specs" / "schemas" / "mcp_tool_outputs.schema.json"
with open(schema_path) as f:
    server.declared_output_schema = json.load(f)["properties"]["tools"]["properties"]["sheets"]
@server.tool()
def sheets_handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "sheets":
        raise ValueError(f"Unknown tool: {name}")

    action = arguments.get("action")
    piece_id = arguments.get("piece_id", "unknown_piece")
    values = arguments.get("values", {})
    
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        
    print(f"[MCP sheets] Appending to {SHEET_ID} (action={action})...")
    
    gc = gspread.service_account(filename=creds_path)
    sh = gc.open_by_key(SHEET_ID)
    
    # Try to open 'Queue', fallback to first sheet
    try:
        worksheet = sh.worksheet("Queue")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.sheet1
        
    if action == "queue":
        row_data = [
            piece_id,
            values.get("status", ""),
            values.get("caption", ""),
            values.get("asset_url", ""),
            values.get("alt_text", ""),
            ""  # Owner-Action (human-writable)
        ]
        
        piece_ids = worksheet.col_values(1)
        if piece_id in piece_ids:
            row_idx = piece_ids.index(piece_id) + 1
            existing_status = worksheet.cell(row_idx, 2).value
            
            if existing_status == "Published" and values.get("status") == "Published":
                # Second publish attempt refused
                try:
                    audit_sheet = sh.worksheet("Audit")
                except gspread.exceptions.WorksheetNotFound:
                    audit_sheet = sh.add_worksheet(title="Audit", rows=1000, cols=10)
                audit_sheet.append_row([piece_id, "publish_refused", "Publish-once guard: second publish attempt refused"])
                
                response = {
                    "ok": False,
                    "error": "Publish-once guard: second publish attempt refused",
                    "row_id": piece_id
                }
                return [TextContent(type="text", text=json.dumps(response))]
            else:
                # Upsert to prevent duplicates on pipeline retry
                worksheet.update([row_data], f"A{row_idx}:F{row_idx}")
                updated_range = f"A{row_idx}:F{row_idx}"
                
        else:
            # Append new draft
            res = worksheet.append_row(row_data)
            updated_range = res.get("updates", {}).get("updatedRange", "Unknown Range")
            
        response = {
            "ok": True,
            "updated_range": updated_range,
            "row_id": piece_id,
            "values": [values]
        }
        
    elif action == "audit":
        try:
            audit_sheet = sh.worksheet("Audit")
        except gspread.exceptions.WorksheetNotFound:
            audit_sheet = sh.add_worksheet(title="Audit", rows=1000, cols=10)
            
        row_data = [
            piece_id,
            action, # internal action value
            values.get("status", ""),
            values.get("detail", "")
        ]
        res = audit_sheet.append_row(row_data)
        updated_range = res.get("updates", {}).get("updatedRange", "Unknown Range")
        response = {
            "ok": True,
            "updated_range": updated_range,
            "row_id": piece_id,
            "values": [values]
        }
    else:
        raise ValueError(f"Action '{action}' is not supported.")

    return [TextContent(type="text", text=json.dumps(response))]

if __name__ == "__main__":
    server.run()
