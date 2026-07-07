"""Run ONE live pipeline piece for any brand: the owner's per-brand demo runner.

Usage (from repo root, needs .env + service-account json):
    python tools/run_one_piece.py brands/chuski-club/brand_kit.yaml "directive text"

Each run costs ~10-15 live model calls and, on success, writes one row to the
Queue sheet and uploads the composited image. An 'Escalated' result is the CD
taste gate working — rerun once or accept it.
"""
import asyncio
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from app.pipeline import run_pipeline_async  # noqa: E402


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    kit_path, directive = sys.argv[1], sys.argv[2]
    result = asyncio.run(run_pipeline_async(directive, kit_path))
    print("=" * 46)
    print(f"STATUS: {result.get('status')}")
    if result.get("status") == "Escalated":
        print("The CD escalated this piece (taste gate). Rerun once or accept.")
    else:
        print("Piece queued — check the Queue sheet and the image link in its row.")
    print("=" * 46)


if __name__ == "__main__":
    main()
