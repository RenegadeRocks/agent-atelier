import os
import gspread
from dotenv import load_dotenv

load_dotenv("app/agents/.env")
load_dotenv(".env")

from app.agents.config import SHEET_ID

creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
gc = gspread.service_account(filename=creds_path)
sh = gc.open_by_key(SHEET_ID)

try:
    worksheet = sh.worksheet("Queue")
except gspread.exceptions.WorksheetNotFound:
    worksheet = sh.sheet1

# Update header row
worksheet.update([['piece_id', 'status', 'caption', 'asset URL', 'alt text', 'Owner-Action']], 'A1')

print("Header updated. Rows count:", worksheet.row_count)
# print rows 1 to 25 to see
vals = worksheet.get_values('A1:F25')
for i, r in enumerate(vals):
    print(f"Row {i+1}: {r}")
