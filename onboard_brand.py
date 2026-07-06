import os
import asyncio
import sys
import argparse
from dotenv import load_dotenv

from google.adk import runners
from app.agents.config import validate_models_on_startup
from app.agents.brand_strategist import get_agent
from app.brand_kit import load_brand_kit
from app.resolver import ResolveScope, MODEL, AUTH, SecretsVault, resolve

load_dotenv()

def get_vault():
    return SecretsVault({
        "google_oauth_token": os.environ.get("GOOGLE_OAUTH_TOKEN", "mock_google_token"),
        "instagram_graph_token": os.environ.get("INSTAGRAM_GRAPH_TOKEN", "mock_ig_token"),
        "gemini_image_pro_api_key": os.environ.get("GEMINI_API_KEY", "mock_gemini_key")
    })

async def main():
    parser = argparse.ArgumentParser(description="Brand Onboarding CLI")
    parser.add_argument("source_dir", nargs='?', default=None, help="Directory containing source materials (e.g. demo/brand-packs/kanva-coffee/)")
    args = parser.parse_args()

    validate_models_on_startup()
    
def preload_ingested_context(source_dir: str) -> str:
    ingested_context = ""
    if source_dir and os.path.isdir(source_dir):
        sources_path = os.path.join(source_dir, "sources")
        if os.path.isdir(sources_path):
            print(f"\n[System] Found source directory: {sources_path}. Ingesting local files...")
            from app.tools.source_ingest import ingest_source
            
            # Look for markdown or text files
            for f in os.listdir(sources_path):
                if f.endswith(".md") or f.endswith(".txt"):
                    file_path = os.path.join(sources_path, f)
                    res = ingest_source(file_path)
                    if res["status"] == "success":
                        ingested_context += f"\n--- INGESTED SOURCE: {f} ---\n{res['text']}\n"
            
            if ingested_context:
                print("[System] Ingestion successful. Passing to Strategist...\n")
    return ingested_context

def process_kit_output(output_text: str, base_dir: str = "."):
    import re
    import yaml
    import traceback
    
    blocks = re.findall(r'```(?:yaml)?\s*(.*?)\s*```', output_text, re.DOTALL | re.IGNORECASE)
    for block in blocks:
        if 'brand_kit_version' in block:
            print("\n[System] Detected Brand Kit YAML output. Attempting to save and validate...")
            try:
                kit_data = yaml.safe_load(block)
                if not isinstance(kit_data, dict):
                    continue
                
                # Derive slug
                brand_name = kit_data.get('brand_short_name') or kit_data.get('brand_name') or 'unknown-brand'
                slug = re.sub(r'[^a-z0-9]+', '-', brand_name.lower()).strip('-')
                
                # Ensure directory exists
                brand_dir = os.path.join(base_dir, "brands", slug)
                os.makedirs(brand_dir, exist_ok=True)
                
                kit_path = os.path.join(brand_dir, "brand_kit.yaml")
                with open(kit_path, 'w', encoding='utf-8') as f:
                    f.write(block.strip())
                
                print(f"[System] Kit written to: {kit_path}")
                
                # Validate
                from app.brand_kit import load_brand_kit
                schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "specs", "brand_kit.schema.json")
                try:
                    load_brand_kit(kit_path, schema_path)
                    print("\n[System] VALIDATION: PASS")
                    print(f"[System] The Brand Kit at {kit_path} is now ACTIVE.")
                except Exception as e:
                    draft_path = os.path.join(brand_dir, "brand_kit.draft.yaml")
                    os.rename(kit_path, draft_path)
                    print("\n[System] VALIDATION: FAIL")
                    print(f"[System] Reason: {str(e)}")
                    print(f"[System] The kit has been renamed to {draft_path} and is NOT active.")
            except Exception as e:
                print(f"[System] Failed to parse or save YAML: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Brand Onboarding CLI")
    parser.add_argument("source_dir", nargs='?', default=None, help="Directory containing source materials (e.g. demo/brand-packs/kanva-coffee/)")
    args = parser.parse_args()

    validate_models_on_startup()
    
    ingested_context = preload_ingested_context(args.source_dir)

    agent = get_agent()
    # The Strategist runs PRE-kit, so we do NOT fail-closed resolve its instructions.
    # The [[TOKENS]] remain literal text so the LLM knows which fields to elicit.
    
    runner = runners.InMemoryRunner(agent=agent)
    
    print("=========================================================")
    print("       Agent Atelier — Brand Onboarding Strategist       ")
    print("=========================================================")
    print("Type 'exit' or 'quit' to end the session.")
    print("The Strategist will guide you through the intake interview.")
    print("=========================================================\n")

    # Initial prompt to start the interview
    initial_prompt = "Hello! I am ready to start the guided brand interview. "
    if ingested_context:
        initial_prompt += f"I have ingested the following source materials. Please use them to draft answers when appropriate:\n{ingested_context}"
    else:
        initial_prompt += "We are starting from scratch."

    # First turn
    events = await runner.run_debug(initial_prompt, quiet=True)
    for e in events:
        if getattr(e, 'author', '') != 'user' and getattr(e, 'message', None) and hasattr(e.message, 'parts'):
            for p in e.message.parts:
                if getattr(p, 'text', None):
                    print(f"Strategist: {p.text.strip()}")

    # Interactive Loop
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.strip().lower() in ['exit', 'quit']:
                print("Exiting onboarding session...")
                break
            
            if not user_input.strip():
                continue
                
            print("\nThinking...")
            events = await runner.run_debug(user_input, quiet=True)
            output_text = ""
            for e in events:
                if getattr(e, 'author', '') != 'user' and getattr(e, 'message', None) and hasattr(e.message, 'parts'):
                    for p in e.message.parts:
                        if getattr(p, 'text', None):
                            output_text += p.text
            print(f"Strategist: {output_text.strip()}")
            process_kit_output(output_text)
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting onboarding session...")
            break

if __name__ == "__main__":
    asyncio.run(main())
