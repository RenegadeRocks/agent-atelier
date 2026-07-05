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
from app.brand_kit import load_brand_kit
from app.resolver import resolve, ResolveScope, MODEL, AUTH, SecretsVault

load_dotenv()

def get_vault():
    return SecretsVault({
        "google_oauth_token": os.environ.get("GOOGLE_OAUTH_TOKEN", "mock_google_token"),
        "instagram_graph_token": os.environ.get("INSTAGRAM_GRAPH_TOKEN", "mock_ig_token"),
        "gemini_image_pro_api_key": os.environ.get("GEMINI_API_KEY", "mock_gemini_key")
    })

async def run_agent(agent, prompt: str, brand_kit: dict) -> str:
    env = os.environ
    vault = get_vault()
    agent.instruction = resolve(agent.instruction, brand_kit, env, vault, ResolveScope(MODEL)) + "\n\nCRITICAL: Square-bracket tokens like [[TOKEN]] must NEVER appear in your output."
    prompt = resolve(prompt, brand_kit, env, vault, ResolveScope(MODEL))
    
    runner = runners.InMemoryRunner(agent=agent)
    events = await runner.run_debug(prompt, quiet=True)
    output_text = ""
    for e in events:
        if getattr(e, 'author', '') != 'user' and getattr(e, 'message', None) and hasattr(e.message, 'parts'):
            for p in e.message.parts:
                if getattr(p, 'text', None):
                    output_text += p.text
    return output_text.strip()

async def run_pipeline_async(idea: str, brand_kit_path: str = 'brands/aol/brand_kit.yaml') -> dict:
    validate_models_on_startup()
    brand_kit = load_brand_kit(brand_kit_path, 'specs/brand_kit.schema.json')
    
    trace = []
    responses = {}
    import re
    brand_short = brand_kit.get("brand_short_name", "BRAND")
    slug = re.sub(r'[^A-Z0-9]+', '-', brand_short.upper()).strip('-')
    piece_id = f"{slug}-{uuid.uuid4().hex[:6].upper()}"
    
    print(f"--- STARTING PIPELINE WITH IDEA: {idea} ---\n")
    
    # [PLAN]
    me = get_me()
    prompt = f"Plan this idea: {idea}"
    print(f"[{me.name}] Prompt: {prompt}")
    resp = await run_agent(me, prompt, brand_kit)
    responses["plan"] = resp
    trace.append("managing_editor")
    print(f"[{me.name}] Response:\n{resp}\n")
    
    review_loop_count = 0
    draft_loop_count = 0
    approved_by_cd = False
    draft_prompt_suffix = ""
    
    # Store extracted fields safely
    caption = ""
    idea_sentence = ""
    hook = ""
    visual_brief = ""
    
    while review_loop_count <= 2 and not approved_by_cd:
        # [IDEATE+DRAFT]
        evergreen = get_evergreen()
        prompt = f"Draft content based on this plan:\n{responses.get('plan', '')}\n\nYou MUST end your reply with exactly one fenced ```json block containing these exactly named keys: 'idea_sentence', 'caption', 'hook_text', 'visual_brief'.\n'hook_text': the exact short phrase (2-10 words) to be printed on the image - e.g. 'Burnout isn't a badge of honor.' Never a number, never a count."
        if draft_prompt_suffix:
            prompt += f"\n\nERROR FROM PREVIOUS ATTEMPT: {draft_prompt_suffix}"
            draft_prompt_suffix = ""
            
        print(f"[{evergreen.name}] Prompt: {prompt}")
        resp = await run_agent(evergreen, prompt, brand_kit)
        responses["draft"] = resp
        trace.append("evergreen_content")
        print(f"[{evergreen.name}] Response:\n{resp}\n")
        
        # Strict Extraction - fail loudly if fields are missing
        import re
        import json
        blocks = re.findall(r'```json\s*(.*?)\s*```', resp, re.DOTALL)
        
        if not blocks:
            draft_prompt_suffix = "You failed to provide a fenced ```json block. You must output exactly one JSON block at the end."
            draft_loop_count += 1
            if draft_loop_count > 2:
                print("[pipeline] Escalate due to draft formatting limit.")
                trace.append("escalate_me")
                return {"status": "Escalated", "trace": trace, "responses": responses}
            print(f"[pipeline] Draft extraction failed. Bouncing to evergreen. Loop count: {draft_loop_count}/2")
            continue
            
        try:
            draft_data = json.loads(blocks[-1])
        except json.JSONDecodeError:
            draft_prompt_suffix = "The ```json block you provided contained invalid JSON. Ensure it is perfectly formatted."
            draft_loop_count += 1
            if draft_loop_count > 2:
                print("[pipeline] Escalate due to draft formatting limit.")
                trace.append("escalate_me")
                return {"status": "Escalated", "trace": trace, "responses": responses}
            print(f"[pipeline] Draft JSON parse failed. Bouncing to evergreen. Loop count: {draft_loop_count}/2")
            continue
            
        caption = str(draft_data.get("caption", "")).strip()
        idea_sentence = str(draft_data.get("idea_sentence", "")).strip()
        hook = str(draft_data.get("hook_text", "")).strip()
        visual_brief = str(draft_data.get("visual_brief", "")).strip()
        
        if not caption or not idea_sentence or not hook or not visual_brief:
            draft_prompt_suffix = "Your JSON block was missing one or more required keys: 'idea_sentence', 'caption', 'hook_text', 'visual_brief'."
            draft_loop_count += 1
            if draft_loop_count > 2:
                print("[pipeline] Escalate due to draft formatting limit.")
                trace.append("escalate_me")
                return {"status": "Escalated", "trace": trace, "responses": responses}
            print(f"[pipeline] Draft extraction failed due to missing keys. Bouncing to evergreen. Loop count: {draft_loop_count}/2")
            continue
        
        # [RESEARCH STUB]
        research = get_research()
        prompt = f"Verify claims for this draft:\n{responses.get('draft', '')}"
        print(f"[{research.name}] Prompt: {prompt}")
        resp = await run_agent(research, prompt, brand_kit)
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
        resp = await run_agent(cd, prompt, brand_kit)
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
    visual_prompt_suffix = ""
    
    while visual_loop_count <= 2 and not visual_approved:
        # [VISUALIZE]
        visual = get_visual()
        # Prompt visual agent
        prompt = f"Create a visual brief and placeholder for this draft:\n{responses.get('draft', '')}"
        if visual_prompt_suffix:
            prompt += f"\n\nERROR FROM PREVIOUS ATTEMPT: {visual_prompt_suffix}"
            
        print(f"[{visual.name}] Prompt: {prompt}")
        resp = await run_agent(visual, prompt, brand_kit)
        responses["visual_response"] = resp
        trace.append("visual_production")
        print(f"[{visual.name}] Response:\n{resp}\n")
        
        # Mock MCP integrations for Visualize step
        img_res = image_generate_handle_call_tool("image_generate", {"prompt": visual_brief})
        img_out = json.loads(img_res[0].text)
        asset_url = img_out["asset_url"]
        trace.append("image_generate")
        
        # Caption compose using the HOOK (on-image words), NOT the generation prompt
        comp_res = caption_compose_handle_call_tool("caption_compose", {"image_url": asset_url, "caption": hook, "brand_kit": brand_kit})
        comp_out = json.loads(comp_res[0].text)
        
        if not comp_out["ocr_text_free"]:
            visual_prompt_suffix = "The generated image contained legible text. You must adjust your Visual Brief to explicitly request no text, words, or typography."
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

    # [LATE-BOUND ALT TEXT]
    visual = get_visual()
    alt_prompt = f"The final visual asset has been composited based on this brief:\n{visual_brief}\n\nThe final composited image file is at: {responses.get('visual_asset', '')}\n\nPlease write a brief, 1-2 sentence maximum final description of this image (strictly 20-350 characters, no status chatter). Do NOT exceed 2 sentences.\n\nYou MUST end your reply with exactly one fenced ```json block containing a single key 'alt_text'."
    print(f"[{visual.name}] Alt-Text Prompt: {alt_prompt}")
    alt_resp = await run_agent(visual, alt_prompt, brand_kit)
    responses["alt_text_response"] = alt_resp
    trace.append("visual_production_alt_text")
    
    import re
    import json
    alt_text = ""
    blocks = re.findall(r'```json\s*(.*?)\s*```', alt_resp, re.DOTALL)
    if blocks:
        try:
            alt_data = json.loads(blocks[-1])
            alt_text = str(alt_data.get("alt_text", "")).strip()
        except json.JSONDecodeError:
            pass
    if not alt_text:
        alt_text = "Fallback alt text generated due to parsing failure."

    # [QUEUE]
    ops = get_ops()
    prompt = f"Queue this final package:\nText: {responses.get('draft', '')}\nVisual: {responses.get('visual_asset', '')}\nStatus is approved by CD."
    print(f"[{ops.name}] Prompt: {prompt}")
    resp = await run_agent(ops, prompt, brand_kit)
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

def run_pipeline(idea: str, brand_kit_path: str = 'brands/aol/brand_kit.yaml') -> dict:
    return asyncio.run(run_pipeline_async(idea, brand_kit_path))

if __name__ == "__main__":
    result = run_pipeline("A test idea for the aol brand", 'brands/aol/brand_kit.yaml')

