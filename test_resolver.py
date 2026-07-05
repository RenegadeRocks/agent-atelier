import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
from resolver import resolve, ResolveScope, MODEL, AUTH, SecretsVault, REGISTRY

template = "Mission: [[MISSION]] \n Secret: [[SECRET:IMAGE_PROVIDER_KEY]]"
try:
    resolve(template, {}, {}, SecretsVault({}), ResolveScope(MODEL))
    print("FAILED TO BLOCK ON SECRET")
except Exception as e:
    print("Blocked successfully on secret:", e)

from brand_kit import load_brand_kit
aol_kit = load_brand_kit('brands/aol/brand_kit.yaml', 'specs/brand_kit.schema.json')

test_template = "Name: [[BRAND_NAME]] \nMission: [[MISSION]]\nVoice: [[VOICE_DESCRIPTORS]]"
res = resolve(test_template, aol_kit, {}, SecretsVault({}), ResolveScope(MODEL))
print("Resolved:", res)
