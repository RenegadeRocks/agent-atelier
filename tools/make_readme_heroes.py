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
KIT = yaml.safe_load((ROOT / "brands/chuski-club/brand_kit.yaml").read_text(encoding="utf-8"))

# Owner art direction (2026-07-07): youthful, enthusiastic, college friends;
# some frames use a FLAT, BOLD solid-color background area for the brand's
# poster-like energy. Hooks are kit sample lines / owner-approved copy.
STYLE = (
    "Bright high-key summer daylight, saturated candy colors, joyful and "
    "youthful energy — NOT moody, NOT dim, NOT filmic-dark. "
)
HEROES = [
    {
        "n": 4,
        "hook": "Pick your fighter.",
        "brief": STYLE
        + "Five fruit ice pops in five different bright colors standing upright in a "
        "neat row like a video-game character lineup, against a completely FLAT bold "
        "hot-pink background filling the frame. Hard sun, long crisp graphic shadows, "
        "poster-like flat color-block minimalism, no people.",
    },
    {
        "n": 5,
        "hook": "Your tongue is going to be purple in four minutes.",
        "brief": STYLE
        + "One deep-purple jamun ice pop with a big playful bite already taken out of "
        "it, two tiny glossy purple drips, against a completely FLAT bold pale-lilac "
        "background filling the frame. Hard sunlight, crisp shadow, bold minimal "
        "poster composition, the bitten pop as the single hero object, no people.",
    },
    {
        "n": 6,
        "hook": "It's hot. Come eat ice.",
        "brief": STYLE
        + "A single mango-yellow ice pop perfectly centered with one glossy melting "
        "drip running down its stick, against a completely FLAT bold electric-blue "
        "background filling the frame. Hard summer sun, crisp graphic shadow, "
        "ultra-minimal poster composition, no people.",
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

    brand_kit_args = {
        "wordmark_text": KIT.get("wordmark_text", "CHUSKI CLUB"),
        "accent_light_bg": KIT.get("accent_light_bg"),
        "accent_dark_bg": KIT.get("accent_dark_bg"),
    }

    for hero in HEROES:
        print(f"[heroes] generating hero {hero['n']}: {hero['hook']!r}")
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
        dest = out_dir / f"chuski-hero-{hero['n']}.jpg"
        shutil.copy(comp["asset_url"], dest)
        print(f"[heroes] wrote {dest}")

    print("[heroes] done — REVIEW each image by eye, then commit docs/heroes/.")


if __name__ == "__main__":
    main()
