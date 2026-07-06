import re
import yaml
from pathlib import Path
from app.agents.creative_director import get_agent as get_cd
from app.agents.config import validate_models_on_startup
from google.adk import runners

def load_golden_set(filepath: str) -> list[dict]:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)
    entries = []
    for block in blocks:
        try:
            entry = yaml.safe_load(block)
            if entry and "id" in entry and "kind" in entry:
                entries.append(entry)
        except Exception:
            pass
    return entries

async def evaluate_golden_set(filepath: str, brand_kit: dict):
    validate_models_on_startup()
    entries = load_golden_set(filepath)
    cd_agent = get_cd()
    
    results = {
        "total": len(entries),
        "false_approve_count": 0,
        "negative_catch_rate": 0.0,
        "agreement_rate": 0.0
    }
    
    if not entries:
        return results
        
    agreements = 0
    negatives = 0
    caught_negatives = 0
    
    for entry in entries:
        kind = entry.get("kind")
        owner_expected = entry.get("owner_label", {}).get("expected_cd", "reject").upper()
        owner_decision = entry.get("owner_label", {}).get("decision", "reject").upper()
        
        artifact = entry.get("artifact", {})
        prompt = f"Evaluate this artifact:\n{yaml.dump(artifact)}"
        
        runner = runners.InMemoryRunner(agent=cd_agent)
        events = await runner.run_debug(prompt, quiet=True)
        
        output_text = ""
        for e in events:
            if getattr(e, 'author', '') != 'user' and getattr(e, 'message', None) and hasattr(e.message, 'parts'):
                for p in e.message.parts:
                    if getattr(p, 'text', None):
                        output_text += p.text
                        
        output_upper = output_text.upper()
        
        # Parse CD verdict
        if "APPROVED" in output_upper:
            cd_verdict = "APPROVE"
        elif "REVISE" in output_upper:
            cd_verdict = "REVISE"
        else:
            cd_verdict = "REJECT"
            
        if kind == "negative":
            negatives += 1
            if cd_verdict != "APPROVE":
                caught_negatives += 1
                
        if cd_verdict == "APPROVE" and owner_decision == "REJECT":
            results["false_approve_count"] += 1
            
        if cd_verdict == owner_expected:
            agreements += 1
            
    results["agreement_rate"] = agreements / len(entries)
    if negatives > 0:
        results["negative_catch_rate"] = caught_negatives / negatives
    else:
        results["negative_catch_rate"] = 1.0
        
    return results
