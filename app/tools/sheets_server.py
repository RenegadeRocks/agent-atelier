import os
import json
import gspread
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from dotenv import load_dotenv

load_dotenv()
from app.agents.config import SHEET_ID

server = FastMCP(name="sheets")

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
        
    if action == "queue" or action == "audit":
        row_data = [
            piece_id,
            action,
            values.get("status", ""),
            values.get("caption", ""),
            values.get("asset_url", ""),
            values.get("alt_text", "")
        ]
        
        # Append the row
        res = worksheet.append_row(row_data)
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
