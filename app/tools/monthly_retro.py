import os
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

ROOT = pathlib.Path(__file__).resolve().parents[2]
# Load the floor-state projection by explicit file path: the top-level name
# "tools" is shadowed by app/tools when app/ is on sys.path (pytest), so a
# package import is ambiguous by construction.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "floor_state_projection", ROOT / "tools" / "export_floor_state.py"
)
_floor_state = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_floor_state)
build_state = _floor_state.build_state
from google.adk import runners
from app.agents.config import validate_models_on_startup

async def run_retro():
    import gspread
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    sheet_id = os.environ.get("SHEET_ID")
    if not sheet_id:
        from app.agents.config import SHEET_ID as sheet_id
    if not creds or not sheet_id:
        print("Missing credentials or SHEET_ID")
        return
        
    gc = gspread.service_account(filename=creds)
    sh = gc.open_by_key(sheet_id)
    try:
        audit_rows = sh.worksheet("Audit").get_values()
    except gspread.exceptions.WorksheetNotFound:
        print("No Audit sheet found")
        return

    events = []
    # Find corrections
    for idx, row in enumerate(audit_rows):
        if not row or not any(str(c).strip() for c in row): continue
        if "piece" in str(row[0]).lower(): continue
        row = list(row) + [""] * (7 - len(row))
        verb = row[1].lower()
        detail = row[3]
        if "owner_" in verb or "correction" in verb:
            events.append(f"- Verb: {verb}, Detail: {detail}")

    events = events[-50:] # last 50 edits
    if not events:
        print("No corrections to mine.")
        return
        
    from google import genai
    client = genai.Client()
    
    prompt = f"""You are the Managing Editor preparing the monthly CD retro.
Please review the recent owner corrections/edits and suggest qualitative triage:
- What are the recurring failure modes?
- What engine or canon amendments (e.g. brand voice, safety rules) are needed?

Recent corrections:
{chr(10).join(events)}

Provide a concise, markdown-formatted retro report."""
    
    try:
        response = client.models.generate_content(
            model="gemini-3.1-pro-preview",
            contents=prompt,
            config=genai.types.GenerateContentConfig(temperature=0.4)
        )
        text = response.text
    except Exception as e:
        text = f"LLM error: {e}"
    
    report_path = ROOT / "app" / "tests" / "evidence" / "p6_monthly_retro.md"
    os.makedirs(report_path.parent, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# P6 Monthly Retro\n\n")
        f.write(text)
        
    print("Monthly retro completed.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_retro())
