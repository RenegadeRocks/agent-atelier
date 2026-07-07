"""Produce the next PLANNED piece for a brand — the studio invents the concept.

Takes the first task from this week's real compose_week() plan and hands the
pipeline only the slot descriptor. No owner-written idea: the Managing Editor
generates this week's concept itself, per the brand canon.

Usage: .venv/bin/python tools/produce_from_plan.py brands/tapri-toast-club/brand_kit.yaml
"""
import asyncio
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from app.scheduler import compose_week  # noqa: E402
from app.brand_kit import load_brand_kit  # noqa: E402
from app.pipeline import run_pipeline_async  # noqa: E402


def main():
    kit_path = sys.argv[1]
    as_of = (datetime.datetime.fromisoformat(sys.argv[2])
             if len(sys.argv) > 2 else datetime.datetime.now())
    kit = load_brand_kit(kit_path, "specs/brand_kit.schema.json")
    plan = compose_week(as_of, kit, active_campaigns=[], queue_depth=0,
                        days_since_last_owner_action=0)
    if not plan["tasks"]:
        sys.exit("no planned tasks this week")
    task = plan["tasks"][0]
    track = (task.get("offering_id") and f"offering:{task['offering_id']}") or "evergreen"
    notes = ""
    for day, slot in (kit.get("standing_week") or {}).items():
        if slot and slot.get("notes") and (slot.get("track", "") == track or track == "evergreen"):
            notes = slot["notes"]
            break
    directive = (
        f"This is the scheduled slot from this week's plan — target date "
        f"{task['target_date']}, track '{track}'"
        + (f", slot notes: '{notes}'" if notes else "")
        + ". No concept has been provided by the owner. Generate this week's "
          "concept for this slot yourself, per the brand canon, then execute it."
    )
    print(f"[plan] week {plan['week_of']} · first slot -> {task['target_date']} · {track}")
    print(f"[plan] directive handed to the studio:\n{directive}\n")
    result = asyncio.run(run_pipeline_async(directive, kit_path))
    status = result.get("status", "?") if isinstance(result, dict) else str(result)
    print("\n==============================================")
    print(f"STATUS: {status}")
    print("==============================================")


if __name__ == "__main__":
    main()
