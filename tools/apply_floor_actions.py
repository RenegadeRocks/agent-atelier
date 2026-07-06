"""Apply locally-queued Floor Actions (ui/studio-floor/data/actions.jsonl)
to the Sheets SoR via the same Owner-Action-only client as floor_serve.

Usage:
  python3 tools/apply_floor_actions.py
  python3 tools/apply_floor_actions.py --enqueue '{"piece_id":"...","action":"approve","note":"..."}'

Each applied record is marked applied=true (with applied_at) in place;
nothing is ever deleted, so the file doubles as a local audit trail.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from floor_serve import ACTIONS_PATH, VALID_ACTIONS, _assert_no_status_writer, make_client  # noqa: E402


def load_records(path):
    records = []
    if Path(path).exists():
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    return records


def save_records(path, records):
    text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    Path(path).write_text(text, encoding="utf-8")


def apply_actions(records, client):
    """Apply every unapplied record. Returns (applied_count, failed_count)."""
    _assert_no_status_writer(client)
    applied = failed = 0
    for record in records:
        if record.get("applied"):
            continue
        action = record.get("action")
        piece_id = record.get("piece_id")
        if action not in VALID_ACTIONS or not piece_id:
            record["applied"] = True
            record["apply_error"] = "invalid record — skipped"
            failed += 1
            continue
        note = record.get("note") or ""
        rev = record.get("rev")
        detail = note if rev is None else f"{note} (rev {rev})".strip()
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        try:
            client.set_owner_action(piece_id, VALID_ACTIONS[action])
            client.append_audit([
                piece_id, f"owner_{action}", "", detail, "human", ts,
                record.get("operator_id") or "owner",
            ])
        except Exception as exc:
            record["apply_error"] = str(exc)
            failed += 1
            continue
        record["applied"] = True
        record["applied_at"] = ts
        record.pop("apply_error", None)
        applied += 1
    return applied, failed


def main(argv=None):
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--actions", default=str(ACTIONS_PATH),
                        help="path to actions.jsonl")
    parser.add_argument("--enqueue", metavar="JSON",
                        help="append one action record before applying "
                             '(e.g. \'{"piece_id":"...","action":"approve"}\')')
    args = parser.parse_args(argv)

    path = Path(args.actions)
    records = load_records(path)

    if args.enqueue:
        record = json.loads(args.enqueue)
        record.setdefault("operator_id", os.environ.get("FLOOR_OPERATOR", "owner"))
        record.setdefault("ts", datetime.now(timezone.utc).isoformat(timespec="seconds"))
        record.setdefault("applied", False)
        records.append(record)
        path.parent.mkdir(parents=True, exist_ok=True)
        save_records(path, records)
        print(f"enqueued 1 action for {record.get('piece_id')}")

    pending = [r for r in records if not r.get("applied")]
    if not pending:
        print("nothing to apply.")
        return 0

    client = make_client()
    if client is None:
        print(f"apply_floor_actions: no Sheets credentials — {len(pending)} action(s) "
              "stay queued. Set GOOGLE_APPLICATION_CREDENTIALS and re-run.")
        return 1

    applied, failed = apply_actions(records, client)
    save_records(path, records)
    print(f"applied {applied} action(s), {failed} failed/skipped.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
