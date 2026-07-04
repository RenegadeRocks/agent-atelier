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

    from app.agents import config
    from app.agents.config import ACCENT_COLOR, WORDMARK_TEXT
    
    # 2. Add Typography and Layout (Paperclip Compositor Integration)
    margin = int(width * 0.075)
    max_w = width - 2 * margin
    size = int(width * 0.072)

    def load_font(font_type, font_size):
        paths = {
            "headline": [
                getattr(config, "HEADLINE_FONT_PATH", None),
                "C:\\Windows\\Fonts\\georgiab.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
            ],
            "sans": [
                getattr(config, "SANS_FONT_PATH", None),
                "C:\\Windows\\Fonts\\arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            ]
        }
        for path in paths[font_type]:
            if path and os.path.exists(path):
                try:
                    return ImageFont.truetype(path, font_size)
                except Exception as e:
                    print(f"Font load error ({path}): {e}")
                    
        raise RuntimeError(f"BANNED: Failed to resolve {font_type} font across all fallbacks. ImageFont.load_default() is prohibited.")

    def wrap(draw, text, font, max_w):
        words, lines, cur = text.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=font) <= max_w: cur = t
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        return lines

    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    font = load_font("headline", size)
    
    # Normalize the caption to replace actual newlines with spaces for natural wrapping
    normalized_caption = " ".join(caption.split())
    lines = wrap(d, normalized_caption, font, max_w)
    
    # Auto-shrink headline if too many lines
    while len(lines) > 3 and size > 30:
        size -= 4
        font = load_font("headline", size)
        lines = wrap(d, normalized_caption, font, max_w)

    asc, desc = font.getmetrics()
    lh = int((asc + desc) * 1.06)
    block_h = lh * len(lines)

    # Wordmark padding
    wm_h = int(width * 0.05) if WORDMARK_TEXT else 0
    bottom_pad = int(height * 0.055) + wm_h
    top_of_text = height - bottom_pad - block_h
    accent_gap = int(width * 0.022)
    kick_h = 0
    scrim_top = max(0, top_of_text - kick_h - accent_gap - int(height * 0.10))

    # Auto-detect Theme (Light vs Dark) based on lower band luminance
    box = (0, int(height * 0.6), width, height)
    region = img.crop(box).convert("L")
    mean_luminance = sum(region.getdata()) / (region.width * region.height)
    is_light = mean_luminance > 140
    theme = "light" if is_light else "dark"

    # Theme Variables
    cap_alpha = 242 if is_light else 224
    scrim_col = (250, 246, 239, 255) if is_light else (8, 7, 11, 255)
    shadow = None if is_light else (0, 0, 0, 150)
    text_col = (38, 30, 22, 255) if is_light else (255, 252, 247, 255)
    accent_col = "#B8800E" if is_light else ACCENT_COLOR

    # 3. Add Feathered Scrim (Replaces rudimentary gradient)
    grad = Image.new("L", (1, height), 0)
    feather = max(1, int(height * 0.10))
    full_at = scrim_top + feather
    
    for yy in range(height):
        if yy < scrim_top: v = 0
        elif yy < full_at: v = int(((yy - scrim_top) / feather) * cap_alpha)
        else: v = cap_alpha
        grad.putpixel((0, yy), v)
        
    grad = grad.resize((width, height))
    sc = Image.new("RGBA", (width, height), scrim_col)
    sc.putalpha(grad)
    layer = Image.alpha_composite(layer, sc)
    d = ImageDraw.Draw(layer)

    x_left = margin
    
    # Accent rule
    ry = top_of_text - accent_gap
    rule_w = int(width * 0.085)
    rule_h = max(3, int(width * 0.006))
    d.rectangle([x_left, ry, x_left + rule_w, ry + rule_h], fill=accent_col)

    # Headline
    y_text = top_of_text
    
    max_text_width = 0
    for ln in lines:
        line_w = d.textlength(ln, font=font)
        max_text_width = max(max_text_width, line_w)
        if shadow:
            d.text((x_left + 2, y_text + 3), ln, font=font, fill=shadow)
        d.text((x_left, y_text), ln, font=font, fill=text_col)
        y_text += lh
        
    # Wordmark pinned to bottom
    if WORDMARK_TEXT:
        def spaced(s, n=1):
            return (" " * n).join(list(s.upper()))
            
        wf_size = int(width * 0.0225)
        wf = load_font("sans", wf_size)
        ws = spaced(WORDMARK_TEXT, 1)
        wy = height - int(height * 0.045)
        d.text((x_left, wy), ws, font=wf, fill=accent_col)

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    
    out_path = image_path.replace("gen_", "composited_")
    if out_path == image_path:
        out_path = image_path + "_composited.jpg"
        
    img.save(out_path, "JPEG", quality=90)

    output = {
        "asset_url": out_path,
        "ocr_text_free": ocr_text_free,
        "scrim_applied": True,
        "theme": theme,
        "width": width,
        "height": height,
        "short_edge_px": min(width, height),
        "text_bounds": {
            "top": top_of_text,
            "bottom": height - bottom_pad,
            "left": margin,
            "right": margin + max_text_width
        }
    }

    return [TextContent(type="text", text=json.dumps(output))]

if __name__ == "__main__":
    server.run()
