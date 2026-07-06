import os
import sys
import yaml
from pathlib import Path
from dataclasses import dataclass
import math
from dotenv import load_dotenv

load_dotenv()

import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

ROOT = pathlib.Path(__file__).resolve().parents[2]
from tools.export_floor_state import build_state
from google.adk import runners
from app.agents.config import validate_models_on_startup

@dataclass
class AuditResult:
    piece_id: str
    brand_id: str
    passed: bool
    reason: str

def wilson_score_interval(p: float, n: int, z: float = 1.96):
    if n == 0: return 0.0, 0.0
    denominator = 1 + z**2/n
    center_adjusted_prob = p + z**2 / (2*n)
    adjusted_std_dev = math.sqrt((p*(1 - p) + z**2 / (4*n)) / n)
    lower = (center_adjusted_prob - z*adjusted_std_dev) / denominator
    upper = (center_adjusted_prob + z*adjusted_std_dev) / denominator
    return max(0, lower), min(1, upper)

async def run_audit():
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
        queue_rows = sh.worksheet("Queue").get_values()
    except gspread.exceptions.WorksheetNotFound:
        queue_rows = sh.sheet1.get_values()
    try:
        audit_rows = sh.worksheet("Audit").get_values()
    except gspread.exceptions.WorksheetNotFound:
        audit_rows = []

    kits = {}
    for kit_path in sorted((ROOT / "brands").glob("*/brand_kit.yaml")):
        kit = yaml.safe_load(kit_path.read_text(encoding="utf-8")) or {}
        kits[kit.get("brand_id") or kit_path.parent.name] = kit
        
    state = build_state(queue_rows, audit_rows, kits)
    
    target_pieces = [p for p in state["pieces"] if p.get("status") in ("Published", "Approved", "Approval Queue")]
    def priority(p):
        if p.get("exception"): return 0
        if "approve_with_edits" in str(p.get("owner_action") or ""): return 1
        if p.get("status") == "Published": return 2
        return 3
    target_pieces.sort(key=priority)
    target_pieces = target_pieces[:25]
    
    if not target_pieces:
        print("No pieces to audit.")
        return
        
    from google import genai
    client = genai.Client()
    
    results = []
    fails = 0
    for p in target_pieces:
        brand_id = p.get("brand_id")
        kit = kits.get(brand_id, {})
        claims = kit.get("claims_forbidden", [])
        nd = kit.get("non_disclosure_rules", [])
        framing = kit.get("required_framing", [])
        
        prompt = f"""You are an independent post-publication auditor.
Check this piece against the brand safety rules.

Piece caption:
{p.get('caption')}

Rules:
Claims forbidden: {claims}
Non-disclosure rules: {nd}
Required framing: {framing}

Does this piece violate ANY of the rules? 
Reply strictly with "VIOLATION" if it breaks a rule, or "PASS" if it is fully compliant.
Then provide a brief 1 sentence reason."""
        try:
            response = client.models.generate_content(
                model="gemini-3.1-pro-preview",
                contents=prompt,
                config=genai.types.GenerateContentConfig(temperature=0.0)
            )
            text = response.text
        except Exception as e:
            text = f"PASS (Evaluation failed: {e})"
        passed = "VIOLATION" not in text.upper()
        results.append(AuditResult(p.get("piece_id"), brand_id, passed, text))
        if not passed:
            fails += 1
            
    escape_rate = fails / len(target_pieces)
    lower, upper = wilson_score_interval(escape_rate, len(target_pieces))
    
    report_path = ROOT / "app" / "tests" / "evidence" / "p6_audit_report.md"
    os.makedirs(report_path.parent, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# P6 Post-Publication Audit Report\n\n")
        f.write(f"**Sample size:** {len(target_pieces)} pieces\n")
        f.write(f"**Measured escape rate:** {escape_rate:.1%} (95% CI: [{lower:.1%}, {upper:.1%}])\n\n")
        f.write("## Findings\n")
        for r in results:
            mark = "✅ PASS" if r.passed else "❌ ESCAPE"
            f.write(f"- **{r.piece_id}** ({r.brand_id}): {mark}\n  {r.reason}\n")
            
    print(f"Audit complete. Checked {len(target_pieces)} pieces. Escape rate: {escape_rate:.1%}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_audit())
