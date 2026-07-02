import re
from dotenv import load_dotenv
from google import genai

load_dotenv()

def discover_models():
    client = genai.Client()
    models = [m.name.replace('models/', '') for m in client.models.list()]
    
    # 1. Reasoning tier: newest pro model
    pro_models = [m for m in models if m.startswith('gemini-') and '-pro' in m and 'vision' not in m and 'image' not in m and 'customtools' not in m and 'latest' not in m]
    def get_version(name):
        match = re.search(r'gemini-(\d+\.\d+|\d+)', name)
        return float(match.group(1)) if match else 0.0
    
    pro_models.sort(key=get_version, reverse=True)
    reasoning_model = pro_models[0] if pro_models else 'gemini-2.5-pro'
    
    # 2. Flash tier: 'gemini-flash-latest' if it exists, else newest flash
    if 'gemini-flash-latest' in models:
        flash_model = 'gemini-flash-latest'
    else:
        flash_models = [m for m in models if 'flash' in m and 'lite' not in m and 'image' not in m and 'preview' not in m and 'latest' not in m]
        flash_models.sort(key=get_version, reverse=True)
        flash_model = flash_models[0] if flash_models else 'gemini-2.5-flash'
        
    return reasoning_model, flash_model

REASONING_MODEL, FLASH_MODEL = discover_models()
