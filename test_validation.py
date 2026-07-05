import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
from brand_kit import load_brand_kit
try:
    load_brand_kit('brands/aol/brand_kit.yaml', 'specs/brand_kit.schema.json')
    print("AOL ok")
except Exception as e:
    print("AOL Error:", type(e), e)
try:
    load_brand_kit('brands/kanva-coffee/brand_kit.yaml', 'specs/brand_kit.schema.json')
    print("Kanva ok")
except Exception as e:
    print("Kanva Error:", type(e), e)
