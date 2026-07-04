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
    
    # 1. Enforce Channel Aspect Ratio & Dimensions
    from app.agents.config import CHANNEL_TARGET_WIDTH, CHANNEL_TARGET_HEIGHT
    
    width, height = img.size
    target_ratio = CHANNEL_TARGET_WIDTH / CHANNEL_TARGET_HEIGHT
    img_ratio = width / height
    
    if abs(img_ratio - target_ratio) > 0.01:
        if img_ratio > target_ratio:
            # Too wide, crop width
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            img = img.crop((left, 0, left + new_width, height))
        else:
            # Too tall, crop height
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            img = img.crop((0, top, width, top + new_height))
            
    # Resize exactly to target
    img = img.resize((CHANNEL_TARGET_WIDTH, CHANNEL_TARGET_HEIGHT), Image.Resampling.LANCZOS)
    width, height = img.size

    # 2. Add Typography and Layout
    draw = ImageDraw.Draw(img)
    # Enforce minimum font size (~4.5% of height)
    min_font_size = max(int(height * 0.045), 60)
    font_size = min_font_size + 10 # start a bit larger
    
    try:
        # Bold stand-in weight
        font = ImageFont.truetype("arialbd.ttf", size=font_size)
    except:
        font = ImageFont.load_default(size=font_size)

    margin = int(width * 0.08) # 8% padding
    safe_width = width - (2 * margin)
    
    # Helper to wrap text
    def wrap_text(text, font, max_width):
        lines = []
        for paragraph in text.split('\n'):
            words = paragraph.split(' ')
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word]) if current_line else word
                bbox = font.getbbox(test_line)
                w = bbox[2] - bbox[0]
                if w <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
        return lines

    # Wrap the text
    wrapped_lines = wrap_text(caption, font, safe_width)
    
    # Calculate text block height
    line_height = font.getbbox("A")[3] - font.getbbox("A")[1]
    line_spacing = int(line_height * 0.3)
    text_block_height = (len(wrapped_lines) * line_height) + ((len(wrapped_lines) - 1) * line_spacing)
    
    # If text is too tall, scale font down to floor
    if text_block_height > (height * 0.4):
        font_size = min_font_size
        try:
            font = ImageFont.truetype("arialbd.ttf", size=font_size)
        except:
            font = ImageFont.load_default(size=font_size)
        wrapped_lines = wrap_text(caption, font, safe_width)
        line_height = font.getbbox("A")[3] - font.getbbox("A")[1]
        line_spacing = int(line_height * 0.3)
        text_block_height = (len(wrapped_lines) * line_height) + ((len(wrapped_lines) - 1) * line_spacing)

    # 3. Add Scrim dynamically sized to cover text block + padding
    scrim = Image.new('RGBA', img.size, (0, 0, 0, 0))
    scrim_draw = ImageDraw.Draw(scrim)
    
    scrim_height = text_block_height + (margin * 2) # Scrim covers text + bottom margin + top margin
    for i in range(scrim_height):
        alpha = int(255 * (i / scrim_height) * 0.85) # Very high contrast (85% opacity) at bottom
        y = height - scrim_height + i
        scrim_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
        
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, scrim)
    
    # Draw text
    draw = ImageDraw.Draw(img)
    y_text = height - margin - text_block_height
    max_text_width = 0
    for line in wrapped_lines:
        line_w = font.getbbox(line)[2] - font.getbbox(line)[0]
        max_text_width = max(max_text_width, line_w)
        # Try to use stroke if the font is default to simulate boldness
        try:
            draw.text((margin, y_text), line, font=font, fill=(255, 255, 255, 255), stroke_width=1, stroke_fill=(255, 255, 255, 255))
        except:
            draw.text((margin, y_text), line, font=font, fill=(255, 255, 255, 255))
        y_text += line_height + line_spacing
    
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
        "short_edge_px": min(width, height),
        "text_bounds": {
            "top": height - margin - text_block_height,
            "bottom": height - margin,
            "left": margin,
            "right": margin + max_text_width
        }
    }

    return [TextContent(type="text", text=json.dumps(output))]

if __name__ == "__main__":
    server.run()
