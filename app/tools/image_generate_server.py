import os
import uuid
import json
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
from app.agents.config import IMAGE_MODEL_ID

server = FastMCP(name="image_generate")

@server.tool()
def image_generate_handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "image_generate":
        raise ValueError(f"Unknown tool: {name}")

    prompt = arguments.get("prompt")
    if not prompt:
        raise ValueError("Missing 'prompt' argument.")
        
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    
    print(f"[MCP image_generate] Real generating image with model {IMAGE_MODEL_ID}...")
    
    # We call the real API
    # Since gemini-3-pro-image or imagen-3 is used, we use client.models.generate_images
    result = client.models.generate_images(
        model=IMAGE_MODEL_ID,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            output_mime_type="image/jpeg",
            aspect_ratio="1:1"
        )
    )
    
    if not result.generated_images:
        raise RuntimeError("Image generation failed to produce an image.")
        
    generated_image = result.generated_images[0]
    
    # Save the bytes to a local file for the real 'asset_url' since we don't have a real cloud bucket for it here
    pred_id = str(uuid.uuid4())[:8]
    output_filename = f"gen_{pred_id}.jpg"
    
    evidence_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", "evidence")
    os.makedirs(evidence_dir, exist_ok=True)
    file_path = os.path.join(evidence_dir, output_filename)
    
    with open(file_path, "wb") as f:
        f.write(generated_image.image.image_bytes)
        
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
