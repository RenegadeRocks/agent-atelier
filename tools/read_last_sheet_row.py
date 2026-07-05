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

vals = worksheet.get_values()
last_row = vals[-1]
print("Last Row:")
for v in last_row:
    print(v)
