import warnings
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Pinned models (do not auto-switch per PRD §14.3 and §18.2)
# RE-CHECK: if a stable gemini-3.1-pro (non-preview) is released before the demo recording, update this pin.
REASONING_MODEL = "gemini-3.1-pro-preview"
FLASH_MODEL = "gemini-flash-latest"

def validate_models_on_startup():
    try:
        client = genai.Client()
        available_models = [m.name.replace('models/', '') for m in client.models.list()]
    except Exception as e:
        warnings.warn(f"Could not fetch models to validate: {e}")
        return

    # 1. Check if pinned models exist
    if REASONING_MODEL not in available_models:
        warnings.warn(f"WARNING: Pinned reasoning model '{REASONING_MODEL}' no longer exists in available models.")
    if FLASH_MODEL not in available_models:
        warnings.warn(f"WARNING: Pinned flash model '{FLASH_MODEL}' no longer exists in available models.")
        
    # 2. Check if a newer stable pro exists
    pro_models = [m for m in available_models if m.startswith('gemini-') and '-pro' in m and 'vision' not in m and 'image' not in m and 'customtools' not in m and 'latest' not in m]
    stable_pros = [m for m in pro_models if 'preview' not in m]
    
    def get_version(name):
        match = re.search(r'gemini-(\d+\.\d+|\d+)', name)
        return float(match.group(1)) if match else 0.0
        
    if stable_pros:
        stable_pros.sort(key=get_version, reverse=True)
        newest_stable = stable_pros[0]
        if get_version(newest_stable) >= 3.1:
            warnings.warn(f"NOTICE: A newer stable pro model '{newest_stable}' is available. Consider updating REASONING_MODEL.")
