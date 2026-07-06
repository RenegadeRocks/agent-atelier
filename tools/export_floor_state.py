"""Export the Studio Floor projection -> ui/studio-floor/data/state.json.

The projection is a denormalized, presentational view of the Sheets SoR +
Audit trail (PRD build-view section 12.4: "never authoritative over them").
Pure derivation lives in build_state(); main() does the live fetch and
imports gspread / app config lazily so importing this module never needs
credentials.

As-built source shapes (app/tools/sheets_server.py):
  Queue row:  [piece_id, status, caption, asset_url, alt_text, owner_action]
  Audit row:  [piece_id, verb, status, detail, actor?, ts?, operator_id?]
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "ui" / "studio-floor" / "data" / "state.json"

STATUSES = ["Draft", "CD Review", "Approval Queue", "Approved", "Published", "Archived"]
SEVERITIES = {"info", "needs_you", "alert"}

# section 12.5 owner verb set (normalized; "owner_" prefix stripped first)
DECISION_VERBS = {"approve", "approve_with_edits", "request_changes", "reject", "mark_posted"}
APPROVING_VERBS = {"approve", "approve_with_edits", "mark_posted"}

AGENT_ROLES = {
    "managing_editor", "evergreen_content", "offering_content",
    "research_verification", "creative_director", "visual_production",
    "publishing_ops", "brand_strategist",
}

# fail-closed / blocked markers surfaced from audit (section 12.4 stuck-list items 1/6/8)
_BLOCK_PATTERNS = [
    (re.compile(r"safety|fail.?closed|policy.?block", re.I), "Safety-Blocked"),
    (re.compile(r"breaker", re.I), "Breaker-Paused"),
    (re.compile(r"publish_refused|publish.?fail", re.I), "Publish-Failed"),
    (re.compile(r"escalat", re.I), "Escalated"),
]
_VIOLATION_RE = re.compile(r"policy.?violation", re.I)
_REVISE_RE = re.compile(r"revise|sent_back|request_revision", re.I)

_STATUS_STAGE = {
    "Draft": ("DRAFT", "evergreen_content"),
    "CD Review": ("CD_REVIEW", "creative_director"),
    "Approval Queue": ("HUMAN_GATE", "publishing_ops"),
    "Approved": ("HUMAN_GATE", "publishing_ops"),
    "Published": ("RECORD", "publishing_ops"),
    "Archived": ("RECORD", "publishing_ops"),
}

DEFAULT_THRESHOLD = {
    "window_pieces": 20,
    "min_approval_rate": 0.95,
    "max_avg_human_edits": 0,
    "zero_policy_violations": True,
}

DEFAULT_BUDGET = {
    "run_tokens_used": 0, "run_token_cap": 130000, "pct": 0,
    "band": "normal", "breaker": "OK", "iterations": 0, "iteration_cap": 40,
}


def _norm_verb(verb):
    v = (verb or "").strip().lower().replace(" ", "_").replace("-", "_")
    if v.startswith("owner_"):
        v = v[len("owner_"):]
    return v


def _brand_of(piece_id, kits):
    for brand in sorted(kits, key=len, reverse=True):
        if piece_id.startswith(brand + "-"):
            return brand
    # real format: <brand-id>-<6char>
    return re.sub(r"-[a-z0-9]{6}$", "", piece_id or "")


def _title_from_caption(caption):
    line = (caption or "").strip().splitlines()[0] if (caption or "").strip() else ""
    line = re.sub(r"#\S+", "", line).strip(" -—·")
    if not line:
        return "(untitled piece)"
    return line if len(line) <= 48 else line[:47].rstrip() + "…"


def _severity_for(verb):
    v = _norm_verb(verb)
    for pat, _exc in _BLOCK_PATTERNS:
        if pat.search(v):
            return "alert"
    if v in ("queued_approval", "queued") or "needs_you" in v:
        return "needs_you"
    return "info"


def _event_from_row(idx, row, kits):
    row = list(row) + [""] * (7 - len(row))
    piece_id, verb, stage, detail, actor, ts, operator_id = row[:7]
    verb_n = _norm_verb(verb)
    if not actor:
        if verb_n in DECISION_VERBS or (verb or "").lower().startswith("owner"):
            actor = "human"
        elif verb_n.startswith("lint") or verb_n in ("publish_refused",) or "breaker" in verb_n:
            actor = "system"
        else:
            actor = "system"
    eid = hashlib.sha1(
        f"{idx}|{piece_id}|{verb}|{ts}|{detail}".encode("utf-8", "replace")
    ).hexdigest()[:12]
    return {
        "seq": idx + 1,
        "event_id": f"evt-{eid}",
        "brand_id": _brand_of(piece_id, kits) if piece_id else "",
        "ts": ts or "",
        "piece_id": piece_id or None,
        "run_id": None,
        "stage": stage or None,
        "actor": actor,
        "operator_id": operator_id or None,
        "verb": verb_n or "event",
        "detail": detail or "",
        "span_ref": None,
        "severity": _severity_for(verb),
        "rule": None,
    }


def _exception_from_events(piece_events):
    for evt in reversed(piece_events):
        for pat, exc in _BLOCK_PATTERNS:
            if pat.search(evt["verb"]):
                return exc, evt["detail"]
    return None, None


def _trust_for_brand(brand_id, kit, brand_events):
    threshold = dict(DEFAULT_THRESHOLD)
    threshold.update((kit or {}).get("trust_threshold") or {})
    decisions = [e for e in brand_events if _norm_verb(e["verb"]) in DECISION_VERBS]
    window = decisions[-int(threshold["window_pieces"]):]
    n = len(window)
    approvals = sum(1 for e in window if _norm_verb(e["verb"]) in APPROVING_VERBS)
    edits = sum(1 for e in window if _norm_verb(e["verb"]) == "approve_with_edits")
    violations = sum(1 for e in brand_events if _VIOLATION_RE.search(e["verb"]))
    rate = (approvals / n) if n else 0.0
    avg_edits = (edits / n) if n else 0.0
    met = (
        n >= int(threshold["window_pieces"])
        and rate >= float(threshold["min_approval_rate"])
        and avg_edits <= float(threshold["max_avg_human_edits"])
        and (violations == 0 or not threshold["zero_policy_violations"])
    )
    return {
        "approval_mode": (kit or {}).get("approval_mode", "human"),
        "auto_publish_enabled": bool((kit or {}).get("auto_publish_enabled", False)),
        "threshold": threshold,
        "window": {
            "decisions": n,
            "approvals": approvals,
            "approval_rate": round(rate, 3),
            "avg_human_edits": round(avg_edits, 3),
            "policy_violations": violations,
            "met": met,
        },
    }


def build_state(queue_rows, audit_rows, kits, budget=None, generated_at=None):
    """Pure projection builder. queue_rows/audit_rows are raw sheet value
    lists (as-built shapes above); kits maps brand_id -> brand-kit dict."""
    from datetime import datetime, timezone

    events = []
    for idx, row in enumerate(audit_rows or []):
        if not row or not any(str(c).strip() for c in row):
            continue
        if str(row[0]).strip().lower() in ("piece_id", "piece id"):
            continue
        events.append(_event_from_row(len(events), row, kits))

    by_piece = {}
    for evt in events:
        if evt["piece_id"]:
            by_piece.setdefault(evt["piece_id"], []).append(evt)

    pieces = []
    for row in queue_rows or []:
        row = list(row) + [""] * (6 - len(row))
        piece_id, status, caption, asset_url, alt_text, owner_action = [
            str(c).strip() for c in row[:6]
        ]
        if not piece_id or piece_id.lower() in ("piece_id", "piece id"):
            continue
        if status not in STATUSES:
            status = "Draft"
        pevents = by_piece.get(piece_id, [])
        exception, exc_detail = _exception_from_events(pevents)
        stage, agent = _STATUS_STAGE[status]
        for evt in reversed(pevents):
            if evt["stage"]:
                stage = evt["stage"]
                break
        for evt in reversed(pevents):
            if evt["actor"] in AGENT_ROLES:
                agent = evt["actor"]
                break
        revises = [e for e in pevents if _REVISE_RE.search(e["verb"])]
        needs_you = False
        reason = None
        if status == "Approval Queue" and not owner_action:
            needs_you, reason = True, "Waiting at the human gate"
        if exception:
            needs_you = True
            reason = exc_detail or f"{exception} — needs your call"
        pieces.append({
            "piece_id": piece_id,
            "brand_id": _brand_of(piece_id, kits),
            "title": _title_from_caption(caption),
            "status": status,
            "exception": exception,
            "stage": stage,
            "agent": agent,
            "caption": caption,
            "asset_url": asset_url,
            "alt_text": alt_text,
            "owner_action": owner_action,
            "rev": 1,
            "queued_at": None,
            "review_round": len(revises),
            "review_cap": 2,
            "needs_you": needs_you,
            "needs_you_reason": reason,
            "cd_note": revises[-1]["detail"] if revises else None,
            "posted_permalink": None,
        })

    brand_ids = sorted(set(kits) | {p["brand_id"] for p in pieces if p["brand_id"]})
    brands = [{
        "brand_id": b,
        "name": (kits.get(b) or {}).get("brand_name") or b.replace("-", " ").title(),
    } for b in brand_ids]

    trust = {}
    for b in brand_ids:
        brand_events = [e for e in events if e["brand_id"] == b]
        trust[b] = _trust_for_brand(b, kits.get(b), brand_events)

    return {
        "schema": "studio-floor-state/v1",
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "brands": brands,
        "pieces": pieces,
        "events": events,
        "trust": trust,
        "budget": dict(DEFAULT_BUDGET, **(budget or {})),
    }


def validate_state(state):
    """Shape validator shared by tests and the demo fixture. Returns a list
    of error strings (empty list == valid)."""
    errors = []

    def err(msg):
        errors.append(msg)

    if not isinstance(state, dict):
        return ["state is not a dict"]
    for key in ("generated_at", "brands", "pieces", "events", "trust", "budget"):
        if key not in state:
            err(f"missing top-level key: {key}")
    for i, b in enumerate(state.get("brands", [])):
        if not isinstance(b, dict) or not b.get("brand_id"):
            err(f"brands[{i}] missing brand_id")
    for i, p in enumerate(state.get("pieces", [])):
        for key in ("piece_id", "brand_id", "title", "status", "needs_you"):
            if key not in p:
                err(f"pieces[{i}] missing {key}")
        if p.get("status") not in STATUSES:
            err(f"pieces[{i}] bad status: {p.get('status')!r}")
        if not isinstance(p.get("needs_you"), bool):
            err(f"pieces[{i}] needs_you not bool")
    last_seq = 0
    for i, e in enumerate(state.get("events", [])):
        for key in ("seq", "event_id", "ts", "actor", "verb", "severity"):
            if key not in e:
                err(f"events[{i}] missing {key}")
        if not isinstance(e.get("seq"), int) or e["seq"] <= last_seq:
            err(f"events[{i}] seq not strictly monotonic: {e.get('seq')!r}")
        else:
            last_seq = e["seq"]
        if e.get("severity") not in SEVERITIES:
            err(f"events[{i}] bad severity: {e.get('severity')!r}")
    trust = state.get("trust", {})
    if not isinstance(trust, dict):
        err("trust is not a dict")
    else:
        for b, t in trust.items():
            for key in ("approval_mode", "auto_publish_enabled", "threshold", "window"):
                if key not in t:
                    err(f"trust[{b}] missing {key}")
            for key in ("window_pieces", "min_approval_rate", "max_avg_human_edits",
                        "zero_policy_violations"):
                if key not in t.get("threshold", {}):
                    err(f"trust[{b}].threshold missing {key}")
            for key in ("decisions", "approvals", "approval_rate", "avg_human_edits",
                        "policy_violations", "met"):
                if key not in t.get("window", {}):
                    err(f"trust[{b}].window missing {key}")
    budget = state.get("budget", {})
    pct = budget.get("pct")
    if not isinstance(pct, (int, float)) or not (0 <= pct <= 100):
        err(f"budget.pct out of range: {pct!r}")
    return errors


def _assert_no_env_leak(dump):
    # The projection carries only ids/status/text fields; no environment
    # value may ever land in it (section 14.6 redaction invariant).
    for key, value in os.environ.items():
        if len(value) >= 8 and value in dump:
            raise AssertionError(f"env value of {key} leaked into the projection")


def write_state(state, path=STATE_PATH):
    errors = validate_state(state)
    if errors:
        raise ValueError("invalid state: " + "; ".join(errors))
    dump = json.dumps(state, indent=2, ensure_ascii=False)
    _assert_no_env_leak(dump)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump + "\n", encoding="utf-8")
    return path


def main():
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds or not Path(creds).exists():
        print("export_floor_state: GOOGLE_APPLICATION_CREDENTIALS not set/found — "
              "nothing exported. The UI falls back to its bundled demo fixture "
              "(amber DEMO DATA badge).")
        return 1
    import gspread  # lazy: importing this module never needs creds

    sheet_id = os.environ.get("SHEET_ID")
    if not sheet_id:
        sys.path.insert(0, str(ROOT))
        try:
            from app.agents.config import SHEET_ID as sheet_id  # noqa: N811
        except Exception as exc:
            print(f"export_floor_state: no SHEET_ID env and config import failed ({exc}).")
            return 1

    gc = gspread.service_account(filename=creds)
    sh = gc.open_by_key(sheet_id)
    try:
        queue_rows = sh.worksheet("Queue").get_values()
    except gspread.exceptions.WorksheetNotFound:
        queue_rows = sh.sheet1.get_values()
    try:
        audit_rows = sh.worksheet("Audit").get_values()
    except gspread.exceptions.WorksheetNotFound:
        audit_rows = []

    kits = {}
    try:
        import yaml
        for kit_path in sorted((ROOT / "brands").glob("*/brand_kit.yaml")):
            kit = yaml.safe_load(kit_path.read_text()) or {}
            kits[kit.get("brand_id") or kit_path.parent.name] = kit
    except ImportError:
        print("export_floor_state: pyyaml not installed — using default trust thresholds.")

    state = build_state(queue_rows, audit_rows, kits)
    out = write_state(state)
    print(f"wrote {out} ({len(state['pieces'])} pieces, {len(state['events'])} events)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
