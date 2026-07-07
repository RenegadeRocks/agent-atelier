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
        "hook": "Phalsa season lasts fourteen days. Cancel your plans.",
        "brief": STYLE
        + "Three college friends mid-laugh, clinking fruit ice pops together like a "
        "toast, in front of a completely FLAT, bold hot-pink painted wall that fills "
        "the background edge to edge. Hard noon sun, crisp graphic shadows, Indian "
        "college students in casual summer clothes, deep purple and mango-yellow ice "
        "pops, poster-like flat color-block composition.",
    },
    {
        "hook": "Real jamun leaves a mark.",
        "brief": STYLE
        + "A single hand holding a deep-purple jamun ice pop with one glossy drip "
        "racing down the wrist, against a completely FLAT bold mango-yellow "
        "background filling the whole frame. Hard sunlight, crisp shadow, bold "
        "minimal poster composition, the pop as the single hero object.",
    },
    {
        "hook": "Mango o'clock is 4pm sharp.",
        "brief": STYLE
        + "Five fruit ice pops in different bright colors fanned out on crushed ice, "
        "shot from above on a completely FLAT bold mint-green background, hard sun "
        "and crisp graphic shadows, playful arrangement, poster-like minimalism.",
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

    for i, hero in enumerate(HEROES, 1):
        print(f"[heroes] generating {i}/3: {hero['hook']!r}")
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
        dest = out_dir / f"chuski-hero-{i}.jpg"
        shutil.copy(comp["asset_url"], dest)
        print(f"[heroes] wrote {dest}")

    print("[heroes] done — REVIEW each image by eye, then commit docs/heroes/.")


if __name__ == "__main__":
    main()
