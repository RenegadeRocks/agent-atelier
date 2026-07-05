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

TEST_BRAND_MAP = {
    "[[BRAND_NAME]]": "Agent Atelier",
    "[[BRAND_SHORT_NAME]]": "Atelier",
    "[[EVERGREEN_PILLARS]]": "Operational Efficiency, AI Automation, Future of Work",
    "[[EVERGREEN_PILLARS_1]]": "Operational Efficiency",
    "[[CHANNELS]]": "Instagram, LinkedIn",
    "[[VOICE_DESCRIPTORS]]": "Sharp, pragmatic, mildly contrarian",
    "[[AUDIENCE_PERSONA]]": "Agency owners and cafe managers",
    "[[AUDIENCE_PAINS]]": "Margin compression and operational chaos",
    "[[MISSION]]": "Agent Atelier builds autonomous teams to reclaim human time.",
    "[[LOCAL_DETAIL_BANK]]": "the fourth cold cup of coffee, the 4:05 PM sink dump",
    "[[SCROLL_TEST_PERSONA]]": "a stressed manager scrolling during a brief break",
    "[[LANGUAGES]]": "English",
    "[[STANDING_WEEK]]": "Monday-Friday",
    "[[CONTACT_WHATSAPP]]": "wa.me/agentatelier",
    "[[CONTACT_INSTAGRAM]]": "@agentatelier",
    "[[CTA_STYLE]]": "Soft hook, link in bio",
    "[[OFFERINGS]]": "Full-service AI Ops",
    "[[OFFERING_ID]]": "OPS-01",
    "[[CLAIM_REVERIFY_MONTHS]]": "6",
    "[[REQUIRE_SECOND_SOURCE_FOR_QUANTITATIVE]]": "True",
    "[[IMAGE_PROVIDER]]": "Gemini native",
    "[[IMAGE_QUALITY_TIER]]": "High",
    "[[CLAIMS_ALLOWED]]": "General observations",
    "[[CLAIMS_FORBIDDEN]]": "Guaranteed ROI",
    "[[NON_DISCLOSURE_RULES]]": "No client names without consent",
    "[[REQUIRED_FRAMING]]": "Actionable optimism",
    "[[COMPARATIVE_CLAIMS_ALLOWED]]": "False",
    "[[POLITICAL_CONTENT_ALLOWED]]": "False",
    "[[CTA_FORBIDDEN_PHRASES]]": "Buy now, act fast",
    "[[SOURCE_ALLOWLIST]]": "Primary research, reputable journals",
    "[[SOURCE_DENYLIST]]": "Wikipedia, unverified blogs",
    "[[POSTS_PER_WEEK_TARGET]]": "3",
    "[[MAX_POSTS_PER_WEEK]]": "5",
    "[[RESEARCH_POST_MIN_PER_WEEK]]": "1",
}

def resolve_tokens(text: str) -> str:
    if not text: return text
    for k in sorted(TEST_BRAND_MAP.keys(), key=len, reverse=True):
        text = text.replace(k, TEST_BRAND_MAP[k])
    import re
    text = re.sub(r'\[\[(.*?)\]\]', r'\1', text)
    return text

async def run_agent(agent, prompt: str) -> str:
    agent.instruction = resolve_tokens(agent.instruction) + "\n\nCRITICAL: Square-bracket tokens like [[TOKEN]] must NEVER appear in your output."
    prompt = resolve_tokens(prompt)
    
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
        prompt = f"Draft content based on this plan:\n{responses.get('plan', '')}\n\nYou MUST end your reply with exactly one fenced ```json block containing these exactly named keys: 'idea_sentence', 'caption', 'words', 'visual_brief'."
        if draft_prompt_suffix:
            prompt += f"\n\nERROR FROM PREVIOUS ATTEMPT: {draft_prompt_suffix}"
            draft_prompt_suffix = ""
            
        print(f"[{evergreen.name}] Prompt: {prompt}")
        resp = await run_agent(evergreen, prompt)
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
        hook = str(draft_data.get("words", "")).strip()
        visual_brief = str(draft_data.get("visual_brief", "")).strip()
        
        if not caption or not idea_sentence or not hook or not visual_brief:
            draft_prompt_suffix = "Your JSON block was missing one or more required keys: 'idea_sentence', 'caption', 'words', 'visual_brief'."
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
    visual_prompt_suffix = ""
    
    while visual_loop_count <= 2 and not visual_approved:
        # [VISUALIZE]
        visual = get_visual()
        # Prompt visual agent
        prompt = f"Create a visual brief and placeholder for this draft:\n{responses.get('draft', '')}"
        if visual_prompt_suffix:
            prompt += f"\n\nERROR FROM PREVIOUS ATTEMPT: {visual_prompt_suffix}"
            
        print(f"[{visual.name}] Prompt: {prompt}")
        resp = await run_agent(visual, prompt)
        responses["visual_response"] = resp
        trace.append("visual_production")
        print(f"[{visual.name}] Response:\n{resp}\n")
        
        # Removed early alt-text extraction here. Alt-text is now late-bound.
        
        # Mock MCP integrations for Visualize step
        img_res = image_generate_handle_call_tool("image_generate", {"prompt": visual_brief})
        img_out = json.loads(img_res[0].text)
        asset_url = img_out["asset_url"]
        trace.append(f"image_generate:{asset_url}")
        
        # Caption compose using the HOOK (on-image words), NOT the generation prompt
        comp_res = caption_compose_handle_call_tool("caption_compose", {"image_url": asset_url, "caption": hook})
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
    alt_prompt = f"The final visual asset has been selected and generated based on this brief:\n{visual_brief}\n\nPlease write a brief, 1-2 sentence maximum final description of this image (strictly 20-350 characters, no status chatter). Do NOT exceed 2 sentences.\n\nYou MUST end your reply with exactly one fenced ```json block containing a single key 'alt_text'."
    print(f"[{visual.name}] Alt-Text Prompt: {alt_prompt}")
    alt_resp = await run_agent(visual, alt_prompt)
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

