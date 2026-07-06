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
    
    # Enforce fail-closed validation on safety fields
    for safety_field in ["claims_forbidden", "non_disclosure_rules", "required_framing"]:
        confirmed_key = f"{safety_field}_confirmed"
        if kit.get(confirmed_key) is True:
            field_val = kit.get(safety_field)
            if not field_val:  # Empty list, None, or empty string
                raise ValueError(f"Confirmed-empty is only legal with an explicit owner sign-off marker. Field '{safety_field}' is empty but '{confirmed_key}' is True.")

    def check_placeholders(obj):
        import re
        if isinstance(obj, dict):
            for k, v in obj.items():
                check_placeholders(v)
        elif isinstance(obj, list):
            for item in obj:
                check_placeholders(item)
        elif isinstance(obj, str):
            if re.search(r'<[^>]+>', obj):
                raise ValueError(f"Placeholder string found in kit: {obj}")
                
    check_placeholders(kit)

    return kit
