import os
import uuid
import json
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
from app.agents.config import IMAGE_MODEL_ID, CHANNEL_ASPECT_RATIO

server = FastMCP(name="image_generate")
server.tool_name = "image_generate"

from pathlib import Path
schema_path = Path(__file__).parent.parent.parent / "specs" / "schemas" / "mcp_tool_outputs.schema.json"
with open(schema_path) as f:
    server.declared_output_schema = json.load(f)["properties"]["tools"]["properties"]["image_generate"]
@server.tool()
def image_generate_handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "image_generate":
        raise ValueError(f"Unknown tool: {name}")

    prompt = arguments.get("prompt")
    if not prompt:
        raise ValueError("Missing 'prompt' argument.")
        
    # Inject constraints to enforce text-free E2E generation, channel aspect ratio, composition boundaries, and visual polish
    prompt = f"{prompt}\n\n[SYSTEM CONSTRAINT]: Generate at {CHANNEL_ASPECT_RATIO} aspect ratio. Compose with the subject in the upper and central area of the frame; keep the lower ~40% of the frame clean, simple background with no important elements — space is reserved there for typography. STYLE ENFORCEMENT: premium advertising-campaign photography, cinematic controlled lighting, shallow depth of field, filmic color grade, elevated, magazine-quality. --no text, words, letters, signatures, watermarks, raw, candid, documentary, CCTV-style, gritty. Blank screens/blank signs are fine; no readable glyphs anywhere."
    
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    
    print(f"[MCP image_generate] Real generating image with model {IMAGE_MODEL_ID}...")
    
    pred_id = str(uuid.uuid4())[:8]
    evidence_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", "evidence")
    os.makedirs(evidence_dir, exist_ok=True)
    file_path = os.path.join(evidence_dir, f"gen_{pred_id}.jpg")
    
    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL_ID,
            contents=prompt,
        )
        
        has_image = False
        img_bytes = None
        if hasattr(response, 'candidates') and response.candidates:
            for p in response.candidates[0].content.parts:
                if hasattr(p, 'inline_data') and p.inline_data:
                    img_bytes = p.inline_data.data
                    has_image = True
                    break
                    
        if not has_image or not img_bytes:
            raise ValueError("No image returned from Gemini.")
            
        with open(file_path, "wb") as f:
            f.write(img_bytes)
            
    except Exception as e:
        print(f"[MCP image_generate] API call failed: {e}")
        raise ValueError(f"Image generation API failure: {e}")
        
    # Standard schema output
    output = {
        "asset_url": file_path, # Return local path as URL so caption_compose can read it
        "prediction_id": f"pred_{pred_id}",
        "provider": "google-genai",
        "tier": "high",
        "width": 1024,
        "height": 1024
    }

    return [TextContent(type="text", text=json.dumps(output))]

if __name__ == "__main__":
    server.run()
