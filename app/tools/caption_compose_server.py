import os
import json
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
from app.agents.config import REASONING_MODEL

server = FastMCP(name="caption_compose")

@server.tool()
def caption_compose_handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "caption_compose":
        raise ValueError(f"Unknown tool: {name}")

    image_path = arguments.get("image_url")
    caption = arguments.get("caption")

    if not image_path or not caption:
        raise ValueError("Missing required arguments")
        
    print(f"[MCP caption_compose] Processing {image_path}...")

    # OCR Check via Gemini Vision
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    print("[MCP caption_compose] Running OCR text-free check via Gemini Vision...")
    response = client.models.generate_content(
        model=REASONING_MODEL,
        contents=[
            "Extract any text you see in this image. Do not describe the image. If there are words, output them exactly. If the image is completely free of letters, words, and text, output exactly the string 'NO_TEXT'.",
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
        ]
    )
    
    ocr_result = response.text.strip()
    # Since LLMs can be wordy, check if it strictly said NO_TEXT or if it's empty
    ocr_text_free = ("NO_TEXT" in ocr_result) or (len(ocr_result) == 0)
    
    if not ocr_text_free:
        print(f"[MCP caption_compose] OCR Flagged Text: {ocr_result}")

    # Load image with Pillow
    img = Image.open(image_path)
    
    # 1. Enforce >=1080px short edge
    width, height = img.size
    short_edge = min(width, height)
    if short_edge < 1080:
        scale = 1080 / short_edge
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        width, height = img.size

    # 2. Add Scrim (linear gradient at the bottom)
    # Create an RGBA image for drawing the gradient
    scrim = Image.new('RGBA', img.size, (0, 0, 0, 0))
    scrim_draw = ImageDraw.Draw(scrim)
    # Apply a gradient over the bottom 25% of the image
    scrim_height = int(height * 0.25)
    for i in range(scrim_height):
        alpha = int(255 * (i / scrim_height) * 0.8) # max 80% opacity
        y = height - scrim_height + i
        scrim_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
        
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, scrim)
    
    # 3. Add Typography
    draw = ImageDraw.Draw(img)
    try:
        # We don't have brand fonts, using default as an open-source stand-in (logged as deviation)
        font = ImageFont.load_default(size=40)
    except:
        font = ImageFont.load_default()

    # Simple text wrap would go here, but for now we draw the caption at the bottom
    margin = 40
    # Use textbbox to get size
    bbox = draw.textbbox((0, 0), caption, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = margin
    y = height - text_h - margin
    draw.text((x, y), caption, font=font, fill=(255, 255, 255, 255))
    
    img = img.convert('RGB')
    
    out_path = image_path.replace("gen_", "composited_")
    if out_path == image_path:
        out_path = image_path + "_composited.jpg"
        
    img.save(out_path, "JPEG", quality=90)

    output = {
        "asset_url": out_path,
        "ocr_text_free": ocr_text_free,
        "scrim_applied": True,
        "width": width,
        "height": height,
        "short_edge_px": min(width, height)
    }

    return [TextContent(type="text", text=json.dumps(output))]

if __name__ == "__main__":
    server.run()
