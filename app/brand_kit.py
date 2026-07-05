import yaml
import json
import os
import jsonschema

def load_brand_kit(brand_kit_path: str, schema_path: str) -> dict:
    if not os.path.exists(brand_kit_path):
        raise FileNotFoundError(f"Brand kit not found at {brand_kit_path}")
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema not found at {schema_path}")
        
    with open(brand_kit_path, 'r', encoding='utf-8') as f:
        kit = yaml.safe_load(f)
        
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
        
    jsonschema.validate(instance=kit, schema=schema)
    return kit
