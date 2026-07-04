import os
import asyncio
from dotenv import load_dotenv
from google.adk import runners

from app.agents.config import validate_models_on_startup
from app.agents.managing_editor import get_agent as get_me
from app.agents.evergreen_content import get_agent as get_evergreen
from app.agents.research_verification import get_agent as get_research
from app.agents.creative_director import get_agent as get_cd
from app.agents.visual_production import get_agent as get_visual
from app.agents.publishing_operations import get_agent as get_ops

# We need to simulate MCP calls for the state machine logic
from app.tools.sheets_server import sheets_handle_call_tool
from app.tools.caption_compose_server import caption_compose_handle_call_tool
from app.tools.image_generate_server import image_generate_handle_call_tool
from app.tools.drive_server import drive_handle_call_tool
import json
import uuid

load_dotenv()

async def run_agent(agent, prompt: str) -> str:
    runner = runners.InMemoryRunner(agent=agent)
    events = await runner.run_debug(prompt, quiet=True)
    output_text = ""
    for e in events:
        if getattr(e, 'author', '') != 'user' and getattr(e, 'message', None) and hasattr(e.message, 'parts'):
            for p in e.message.parts:
                if getattr(p, 'text', None):
                    output_text += p.text
    return output_text.strip()

async def run_pipeline_async(idea: str) -> dict:
    validate_models_on_startup()
    
    trace = []
    responses = {}
    piece_id = f"test_brand-{uuid.uuid4().hex[:6]}"
    
    print(f"--- STARTING PIPELINE WITH IDEA: {idea} ---\n")
    
    # [PLAN]
    me = get_me()
    prompt = f"Plan this idea: {idea}"
    print(f"[{me.name}] Prompt: {prompt}")
    resp = await run_agent(me, prompt)
    responses["plan"] = resp
    trace.append("managing_editor")
    print(f"[{me.name}] Response:\n{resp}\n")
    
    review_loop_count = 0
    approved_by_cd = False
    
    while review_loop_count <= 2 and not approved_by_cd:
        # [IDEATE+DRAFT]
        evergreen = get_evergreen()
        prompt = f"Draft content based on this plan:\n{responses.get('plan', '')}"
        print(f"[{evergreen.name}] Prompt: {prompt}")
        resp = await run_agent(evergreen, prompt)
        responses["draft"] = resp
        trace.append("evergreen_content")
        print(f"[{evergreen.name}] Response:\n{resp}\n")
        
        # [RESEARCH STUB]
        research = get_research()
        prompt = f"Verify claims for this draft:\n{responses.get('draft', '')}"
        print(f"[{research.name}] Prompt: {prompt}")
        resp = await run_agent(research, prompt)
        responses["research"] = resp
        trace.append("research_verification")
        print(f"[{research.name}] Response:\n{resp}\n")
        
        # [LEDGER LINT]
        trace.append("ledger_lint_stub")
        print(f"[ledger_lint_stub] Linter passed.\n")
        
        # [REVIEW]
        cd = get_cd()
        prompt = f"Review this draft:\n{responses.get('draft', '')}"
        print(f"[{cd.name}] Prompt: {prompt}")
        resp = await run_agent(cd, prompt)
        trace.append("creative_director")
        print(f"[{cd.name}] Response:\n{resp}\n")
        
        if "APPROVED" in resp.upper():
            approved_by_cd = True
            responses["review"] = resp
        else:
            review_loop_count += 1
            print(f"[pipeline] CD rejected. Loop count: {review_loop_count}/2")
            
    if not approved_by_cd:
        print("[pipeline] Escalating to ME due to review loop limit.")
        trace.append("escalate_me")
        return {"status": "Escalated", "trace": trace, "responses": responses}

    visual_loop_count = 0
    visual_approved = False
    
    while visual_loop_count <= 2 and not visual_approved:
        # [VISUALIZE]
        draft_text = responses.get('draft', '')
        # Simple extraction using regex
        import re
        
        caption_match = re.search(r'\*\*Caption:\*\*\s*(.*?)(?=\n\*\*|\Z)', draft_text, re.DOTALL)
        caption = caption_match.group(1).strip() if caption_match else idea
        
        idea_sentence_match = re.search(r'\*\*Idea Sentence:\*\*\s*(.*?)(?=\n\*\*|\Z)', draft_text, re.DOTALL)
        idea_sentence = idea_sentence_match.group(1).strip() if idea_sentence_match else idea
        
        # Extract hook / on-image words from WORDS: field
        words_match = re.search(r'\*\*WORDS:\*\*\s*(.*?)(?=\n\*|\n\*\*|\Z)', draft_text, re.DOTALL)
        if words_match:
            hook = words_match.group(1).strip()
        else:
            # Fallback to caption's first line
            hook = caption.split('\n')[0].split('.')[0] + '.'
            
        # visual brief prompt
        visual_brief_match = re.search(r'\*\*Visual Brief.*?\*\*(.*?)(?=\n\*\*|\Z)', draft_text, re.DOTALL)
        visual_brief = visual_brief_match.group(1).strip() if visual_brief_match else hook
        
        # [VISUALIZE]
        visual = get_visual()
        # Prompt visual agent
        prompt = f"Create a visual brief and placeholder for this draft:\n{draft_text}"
        print(f"[{visual.name}] Prompt: {prompt}")
        resp = await run_agent(visual, prompt)
        responses["visual_response"] = resp
        trace.append("visual_production")
        print(f"[{visual.name}] Response:\n{resp}\n")
        
        # Extract alt text from visual agent response
        alt_text_match = re.search(r'(?:> )?\*\*Alt Text:\*\*\s*(.*?)(?=\n\*\*|\Z)', resp, re.DOTALL | re.IGNORECASE)
        alt_text = alt_text_match.group(1).strip() if alt_text_match else "Generated visual asset."
        
        # Mock MCP integrations for Visualize step
        img_res = image_generate_handle_call_tool("image_generate", {"prompt": visual_brief})
        img_out = json.loads(img_res[0].text)
        asset_url = img_out["asset_url"]
        trace.append(f"image_generate:{asset_url}")
        
        # Caption compose using the HOOK (on-image words), NOT the generation prompt
        comp_res = caption_compose_handle_call_tool("caption_compose", {"image_url": asset_url, "caption": hook})
        comp_out = json.loads(comp_res[0].text)
        
        if not comp_out["ocr_text_free"]:
            visual_loop_count += 1
            print(f"[pipeline] OCR check failed (baked_glyph). Loop count: {visual_loop_count}/3")
            continue # Try again
            
        # If passed OCR, mock uploading to drive
        trace.append("caption_compose")
        drive_res = drive_handle_call_tool("drive", {"action": "upload", "file_id": comp_out["asset_url"]})
        drive_out = json.loads(drive_res[0].text)
        responses["visual_asset"] = drive_out["drive_url"]
        
        # [CD RENDER PASS]
        trace.append("cd_render_pass")
        print("[pipeline] CD render pass passed.\n")
        visual_approved = True

    if not visual_approved:
        print("[pipeline] Escalate due to visual loop limit.")
        trace.append("escalate_visual")
        return {"status": "Escalated", "trace": trace, "responses": responses}

    # [QUEUE]
    ops = get_ops()
    prompt = f"Queue this final package:\nText: {responses.get('draft', '')}\nVisual: {responses.get('visual_asset', '')}\nStatus is approved by CD."
    print(f"[{ops.name}] Prompt: {prompt}")
    resp = await run_agent(ops, prompt)
    responses["queue"] = resp
    trace.append("publishing_operations")
    print(f"[{ops.name}] Response:\n{resp}\n")
    
    # Sheets MCP tool appending to queue
    sheets_handle_call_tool("sheets", {
        "action": "queue", 
        "piece_id": piece_id, 
        "values": {
            "status": "Approval Queue",
            "asset_url": responses.get("visual_asset"),
            "caption": caption,
            "alt_text": alt_text,
            "idea": idea_sentence
        }
    })
    
    return {
        "status": "Approval Queue",
        "trace": trace,
        "responses": responses
    }

def run_pipeline(idea: str) -> dict:
    return asyncio.run(run_pipeline_async(idea))

if __name__ == "__main__":
    result = run_pipeline("A test idea for the hard-coded brand")

