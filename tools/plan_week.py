"""Print this week's cadence for every active brand — the scheduler on screen.

Calls the real compose_week() (app/scheduler.py) for each brands/*/brand_kit.yaml.

Usage: .venv/bin/python tools/plan_week.py [--as-of 2026-07-08T09:00:00]
"""
import argparse
import datetime
import glob
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from app.scheduler import compose_week  # noqa: E402
from app.brand_kit import load_brand_kit  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=None)
    args = ap.parse_args()
    as_of = (datetime.datetime.fromisoformat(args.as_of)
             if args.as_of else datetime.datetime.now())

    kits = sorted(glob.glob("brands/*/brand_kit.yaml"))
    print(f"WEEK PLAN — composed {as_of:%A %Y-%m-%d} · {len(kits)} active brands\n")
    for kit_path in kits:
        try:
            kit = load_brand_kit(kit_path, "specs/brand_kit.schema.json")
        except Exception as e:
            print(f"  {kit_path}: kit not active ({type(e).__name__}) — skipped\n")
            continue
        plan = compose_week(as_of, kit, active_campaigns=[], queue_depth=0,
                            days_since_last_owner_action=0)
        name = kit.get("brand_short_name", kit_path.split("/")[1])
        print(f"┌─ {name}  ·  week {plan['week_of']}  ·  {plan['status']}")
        for t in plan["tasks"]:
            track = (t.get("offering_id") and f"offering: {t['offering_id']}") or "evergreen"
            flag = f"  [{t['flag']}]" if t.get("flag") else ""
            print(f"│   {t['target_date']}  ·  {track}{flag}  ·  {t.get('format','single')}")
        print(f"└─ {len(plan['tasks'])} pieces planned this week\n")


if __name__ == "__main__":
    main()
