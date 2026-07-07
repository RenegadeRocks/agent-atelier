"""Generate owner-directed README hero images for Chuski Club.

These are curated marketing assets, not pipeline pieces: the briefs and hooks
below are OWNER-AUTHORED, so the human eye replaces the OCR machine-gate —
review every output before committing anything.

Needs only GOOGLE_API_KEY in .env (image-model quota; no text-model calls).
Run from the repo root:   python tools/make_readme_heroes.py
Outputs:                  docs/heroes/chuski-hero-<n>.jpg
"""
import json
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import yaml  # noqa: E402
from app.tools import caption_compose_server as ccs  # noqa: E402
from app.tools.image_generate_server import image_generate_handle_call_tool  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load_kit(rel):
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))

# Owner art direction (2026-07-07): youthful, enthusiastic, college friends;
# some frames use a FLAT, BOLD solid-color background area for the brand's
# poster-like energy. Hooks are kit sample lines / owner-approved copy.
STYLE = (
    "Bright high-key summer daylight, saturated candy colors, joyful and "
    "youthful energy — NOT moody, NOT dim, NOT filmic-dark. "
)
HEROES = [
    {
        "out": "chuski-hero-7.jpg",
        "kit": "brands/chuski-club/brand_kit.yaml",
        "hook": "Sharing is optional.",
        "brief": (
            "Bright high-key summer daylight, saturated candy colors, joyful and "
            "youthful energy — NOT moody, NOT dim. Three Indian college friends "
            "squeezed together laughing on one parked scooter against a completely "
            "FLAT bold mango-yellow wall, each holding a different bright fruit ice "
            "pop, one friend playfully guarding hers away from the others. Hard sun, "
            "crisp shadows, candid mid-laugh energy, casual summer clothes, "
            "poster-like flat color-block composition."
        ),
    },
    {
        "out": "kanva-hero-1.jpg",
        "kit": "brands/kanva-coffee/brand_kit.yaml",
        "hook": "Slow is the whole point.",
        "brief": (
            "Premium, royal, unhurried craft: a gleaming copper pour-over kettle "
            "pouring one thin steady stream into a glass brewer, dramatic soft steam "
            "rising, on dark polished walnut with a folded linen cloth, one warm "
            "shaft of morning light from the side, deep controlled shadows, copper "
            "and amber glow, tactile textures, magazine-quality still life."
        ),
    },
]

# Owner-reviewed assets: the human eye is the gate here (see module docstring).
ccs.ocr_checker = lambda image_path: True


def main() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    out_dir = ROOT / "docs" / "heroes"
    out_dir.mkdir(parents=True, exist_ok=True)

    for hero in HEROES:
        kit = load_kit(hero["kit"])
        brand_kit_args = {
            "wordmark_text": kit.get("wordmark_text", ""),
            "accent_light_bg": kit.get("accent_light_bg"),
            "accent_dark_bg": kit.get("accent_dark_bg"),
        }
        print(f"[heroes] generating {hero['out']}: {hero['hook']!r}")
        gen = json.loads(
            image_generate_handle_call_tool("image_generate", {"prompt": hero["brief"]})[0].text
        )
        comp = json.loads(
            ccs.caption_compose_handle_call_tool(
                "caption_compose",
                {
                    "image_url": gen["asset_url"],
                    "caption": hero["hook"],
                    "brand_kit": brand_kit_args,
                },
            )[0].text
        )
        dest = out_dir / hero["out"]
        shutil.copy(comp["asset_url"], dest)
        print(f"[heroes] wrote {dest}")

    print("[heroes] done — REVIEW each image by eye, then commit docs/heroes/.")


if __name__ == "__main__":
    main()
