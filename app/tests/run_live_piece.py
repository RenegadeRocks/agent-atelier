import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from app.pipeline import run_pipeline_async
from app.brand_kit import load_brand_kit
from app.tools.instagram_publish_server import custom_publish_handler

async def main():
    print("========================================")
    print("1. RUNNING PIPELINE TO GENERATE A PIECE")
    print("========================================")
    brand_kit = load_brand_kit('brands/chuski-club/brand_kit.yaml', 'specs/brand_kit.schema.json')
    # Use a very specific prompt that will naturally pass Gate 0's specificity rule
    result = await run_pipeline_async("A group of friends laughing with stained tongues from kala khatta chuskis under a string of patio lights on a humid Delhi evening.", "brands/chuski-club/brand_kit.yaml")
    
    if result["status"] == "Escalated":
        print("PIPELINE ESCALATED:")
        print(result)
        return
        
    responses = result["responses"]
    draft_caption = ""
    import json, re
    blocks = re.findall(r'```json\s*(.*?)\s*```', responses["draft"], re.DOTALL)
    if blocks:
        draft_caption = json.loads(blocks[-1]).get("caption", "")
        
    visual_asset = responses.get("visual_asset", "")
    
    print("========================================")
    print("2. PIECE GENERATED SUCCESSFULLY")
    print("========================================")
    print(f"CAPTION: {draft_caption}")
    print(f"ASSET: {visual_asset}")
    
    print("\n========================================")
    print("3. WIRING THE PUBLISH-TIME REFEREE")
    print("========================================")
    
    publish_args = {
        "media_url": visual_asset,
        "caption": draft_caption,
        "brand_kit": brand_kit
    }
    
    # We simulate the MCP publish call which runs the semantic referee
    output = custom_publish_handler(publish_args)
    print("REFEREE/PUBLISH OUTPUT:")
    print(output[0].text)
    print("\nDONE.")

if __name__ == "__main__":
    asyncio.run(main())
