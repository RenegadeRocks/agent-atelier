import asyncio
import sys

# Ensure stdout supports utf-8 encoding for special characters (like ₹)
sys.stdout.reconfigure(encoding='utf-8')

from app.ci_eval_gate import evaluate_golden_set
from app.brand_kit import load_brand_kit

async def main():
    brand_kit = load_brand_kit('brands/kanva-coffee/brand_kit.yaml', 'specs/brand_kit.schema.json')
    results = await evaluate_golden_set('specs/golden_set.md', brand_kit)
    print("--- CI EVAL GATE RESULTS ---")
    print(f"Total entries: {results['total']}")
    print(f"False Approves: {results['false_approve_count']} (Target: 0)")
    print(f"Negative Catch Rate: {results['negative_catch_rate']:.2f} (Target: 1.00)")
    print(f"Agreement Rate: {results['agreement_rate']:.2f} (Target: >=0.90)")
    print("----------------------------")
    
    if results['false_approve_count'] > 0 or results['negative_catch_rate'] < 1.00 or results['agreement_rate'] < 0.90:
        print("CI GATE FAILED.")
        sys.exit(1)
    else:
        print("CI GATE PASSED.")

if __name__ == "__main__":
    asyncio.run(main())
