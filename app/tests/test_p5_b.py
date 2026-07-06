"""P5-B (Studio Floor v1) deterministic tests — no network, no live creds.

Covers: build_state derivation (pieces/events/needs_you/trust), the demo
fixture against the shared shape validator, the /action handler with a stub
SheetClient (Owner-Action-only writes, never Status), projection redaction,
and the no-external-resource guarantee of the static UI.
"""

import importlib.util
import json
import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
UI_DIR = ROOT / "ui" / "studio-floor"


def _load(name, rel_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


efs = _load("export_floor_state", "tools/export_floor_state.py")
fsrv = _load("floor_serve", "tools/floor_serve.py")


# ---------- fixtures ----------

KITS = {
    "chuski-club": {
        "brand_name": "Chuski Club",
        "approval_mode": "human",
        "auto_publish_enabled": False,
        "trust_threshold": {
            "window_pieces": 10,
            "min_approval_rate": 0.9,
            "max_avg_human_edits": 0.5,
            "zero_policy_violations": True,
        },
    },
}

QUEUE_ROWS = [
    ["piece_id", "status", "caption", "asset_url", "alt_text", "owner_action"],  # header
    ["chuski-club-aa1111", "Approval Queue", "Mango weekend at the cart.", "", "alt", ""],
    ["chuski-club-bb2222", "Approval Queue", "Slush season.", "", "", "Approve"],
    ["chuski-club-cc3333", "CD Review", "Cold brew aids digestion.", "", "", ""],
    ["chuski-club-dd4444", "Published", "Kulfi drop.", "", "", "Mark posted"],
]

# audit shape: [piece_id, verb, status/stage, detail, actor?, ts?, operator_id?]
AUDIT_ROWS = (
    [["chuski-club-%d" % i, "owner_approve", "HUMAN_GATE", "clean", "human",
      "2026-07-0%dT10:00:00+05:30" % (1 + i % 5), "owner"] for i in range(9)]
    + [["chuski-club-x9", "owner_approve_with_edits", "HUMAN_GATE", "tightened hook",
        "human", "2026-07-05T11:00:00+05:30", "owner"]]
    + [
        ["chuski-club-cc3333", "safety_blocked", "LINT",
         "FAIL-CLOSED: matches claims_forbidden", "system",
         "2026-07-06T10:47:00+05:30", ""],
        ["chuski-club-aa1111", "cd_revise", "CD_REVIEW",
         "revise 1/2: hook repeats last 3 posts; add one concrete detail",
         "creative_director", "2026-07-06T10:14:00+05:30", ""],
        ["chuski-club-aa1111", "queued_approval", "HUMAN_GATE",
         "queued -> Approval Queue", "publishing_ops",
         "2026-07-06T11:32:00+05:30", ""],
    ]
)


def built_state():
    return efs.build_state(QUEUE_ROWS, AUDIT_ROWS, KITS)


# ---------- (1) build_state derivation ----------

def test_build_state_pieces_and_monotonic_seq():
    state = built_state()
    assert efs.validate_state(state) == []
    # header row skipped
    ids = [p["piece_id"] for p in state["pieces"]]
    assert "piece_id" not in ids and len(ids) == 4
    seqs = [e["seq"] for e in state["events"]]
    assert seqs == sorted(seqs) and len(set(seqs)) == len(seqs)
    assert all(isinstance(s, int) for s in seqs)
    # events carry stable ids and StudioEvent-shaped fields
    for e in state["events"]:
        assert e["event_id"].startswith("evt-")
        assert e["severity"] in ("info", "needs_you", "alert")


def test_build_state_needs_you():
    state = built_state()
    by_id = {p["piece_id"]: p for p in state["pieces"]}
    # Approval Queue + blank Owner Action -> needs you
    assert by_id["chuski-club-aa1111"]["needs_you"] is True
    # Approval Queue but Owner Action already written -> not
    assert by_id["chuski-club-bb2222"]["needs_you"] is False
    # fail-closed marker in audit -> needs you + exception
    blocked = by_id["chuski-club-cc3333"]
    assert blocked["needs_you"] is True
    assert blocked["exception"] == "Safety-Blocked"
    # published piece never needs you
    assert by_id["chuski-club-dd4444"]["needs_you"] is False
    # CD note carried onto the piece from the revise event
    assert "hook repeats last 3 posts" in by_id["chuski-club-aa1111"]["cd_note"]
    assert by_id["chuski-club-aa1111"]["review_round"] == 1


def test_build_state_trust_math():
    state = built_state()
    t = state["trust"]["chuski-club"]
    w = t["window"]
    # 10 decisions: 9 approve + 1 approve_with_edits -> all approving
    assert w["decisions"] == 10
    assert w["approvals"] == 10
    assert w["approval_rate"] == 1.0
    assert w["avg_human_edits"] == 0.1
    assert w["policy_violations"] == 0
    assert w["met"] is True  # window 10 filled, rate 1.0 >= 0.9, 0.1 <= 0.5
    assert t["auto_publish_enabled"] is False


def test_trust_not_met_on_violation_or_thin_window():
    violation = [["chuski-club-zz", "policy_violation", "", "post-publish catch",
                  "system", "2026-07-06T12:00:00+05:30", ""]]
    state = efs.build_state(QUEUE_ROWS, AUDIT_ROWS + violation, KITS)
    assert state["trust"]["chuski-club"]["window"]["met"] is False
    thin = efs.build_state(QUEUE_ROWS, AUDIT_ROWS[:3], KITS)
    assert thin["trust"]["chuski-club"]["window"]["met"] is False


# ---------- (2) demo fixture passes the same validator ----------

def test_demo_state_valid():
    demo = json.loads((UI_DIR / "data" / "demo-state.json").read_text())
    assert efs.validate_state(demo) == []
    # the required verbatim CD note is present in the fixture
    dump = json.dumps(demo)
    assert "hook repeats last 3 posts; add one concrete detail" in dump
    # one revise-loop at R2, one human-gate wait, one published, one fail-closed
    by_status = {}
    for p in demo["pieces"]:
        by_status.setdefault(p["status"], []).append(p)
    assert any(p["review_round"] == 2 for p in demo["pieces"])
    assert any(p["needs_you"] for p in by_status.get("Approval Queue", []))
    assert by_status.get("Published")
    assert any(p.get("exception") == "Safety-Blocked" for p in demo["pieces"])
    assert len(demo["brands"]) == 3


def test_inline_demo_state_mirrors_canonical_fixture():
    """index.html embeds the demo fixture inline for file:// use (fetch of
    local files is blocked there); it must stay equivalent, as parsed JSON,
    to data/demo-state.json. Regenerate with:
    python3 tools/export_floor_state.py --embed-demo"""
    html = (UI_DIR / "index.html").read_text(encoding="utf-8")
    m = re.search(
        r'<script type="application/json" id="demo-state">(.*?)</script>', html, re.S)
    assert m, "inline demo-state block missing from index.html"
    inline = json.loads(m.group(1).replace("<\\/", "</"))
    canonical = json.loads((UI_DIR / "data" / "demo-state.json").read_text(encoding="utf-8"))
    assert inline == canonical, "inline demo state drifted — rerun --embed-demo"
    # the inline block passes the same shape validator as any state
    assert efs.validate_state(inline) == []


# ---------- (3) action handler with a stub SheetClient ----------

class StubClient:
    """Records calls; deliberately exposes no Status-writing surface."""

    def __init__(self):
        self.calls = []

    def set_owner_action(self, piece_id, label):
        self.calls.append(("set_owner_action", piece_id, label))

    def append_audit(self, row):
        self.calls.append(("append_audit", list(row)))


def test_approve_writes_owner_action_and_audit_never_status(tmp_path):
    stub = StubClient()
    status, payload = fsrv.handle_action(
        {"piece_id": "chuski-club-aa1111", "action": "approve", "note": "ship it", "rev": 3},
        client=stub, actions_path=tmp_path / "actions.jsonl", operator_id="tester",
    )
    assert status == 200 and payload["ok"] is True
    kinds = [c[0] for c in stub.calls]
    assert kinds == ["set_owner_action", "append_audit"]
    assert stub.calls[0][1:] == ("chuski-club-aa1111", "Approve")
    audit_row = stub.calls[1][1]
    assert audit_row[0] == "chuski-club-aa1111"
    assert audit_row[1] == "owner_approve"
    assert "ship it" in audit_row[3] and "rev 3" in audit_row[3]
    assert audit_row[4] == "human"
    assert audit_row[6] == "tester"
    # structurally: no call and no method can touch Status
    assert not any("status" in k.lower() for k in kinds)
    assert not [m for m in dir(stub) if not m.startswith("_") and "status" in m.lower()]


def test_invalid_action_is_400(tmp_path):
    stub = StubClient()
    status, payload = fsrv.handle_action(
        {"piece_id": "x", "action": "unstick"},  # unstick is not active in v1
        client=stub, actions_path=tmp_path / "a.jsonl",
    )
    assert status == 400 and "error" in payload
    assert stub.calls == []
    status, _ = fsrv.handle_action({"action": "approve"}, client=stub,
                                   actions_path=tmp_path / "a.jsonl")
    assert status == 400


def test_missing_creds_queues_to_jsonl(tmp_path):
    path = tmp_path / "actions.jsonl"
    status, payload = fsrv.handle_action(
        {"piece_id": "chuski-club-aa1111", "action": "reject", "note": "off-brand"},
        client=None, actions_path=path, operator_id="tester",
    )
    assert status == 202 and payload["queued"] is True
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["piece_id"] == "chuski-club-aa1111"
    assert record["action"] == "reject"
    assert record["applied"] is False


def test_status_writing_client_is_refused(tmp_path):
    class BadClient(StubClient):
        def set_status(self, piece_id, status):  # pragma: no cover
            pass

    with pytest.raises(AssertionError):
        fsrv.handle_action(
            {"piece_id": "x-abc123", "action": "approve"},
            client=BadClient(), actions_path=tmp_path / "a.jsonl",
        )


# ---------- (4) projection redaction ----------

def test_no_env_value_lands_in_projection(monkeypatch, tmp_path):
    monkeypatch.setenv("SENTINEL_SECRET", "sekrit-sentinel-value-9f8e7d6c")
    state = built_state()
    dump = json.dumps(state)
    assert "sekrit-sentinel-value-9f8e7d6c" not in dump
    # write_state enforces the same invariant structurally
    out = efs.write_state(state, tmp_path / "state.json")
    assert "sekrit-sentinel-value-9f8e7d6c" not in out.read_text()


def test_write_state_asserts_on_leak(monkeypatch, tmp_path):
    monkeypatch.setenv("SENTINEL_SECRET", "sekrit-sentinel-value-9f8e7d6c")
    state = built_state()
    state["pieces"][0]["caption"] = "oops sekrit-sentinel-value-9f8e7d6c"
    with pytest.raises(AssertionError):
        efs.write_state(state, tmp_path / "state.json")


# ---------- (5) no external resources in the static UI ----------

CROSS_ORIGIN = re.compile(
    r"""(?:src|href)\s*=\s*["']https?://(?!localhost|127\.0\.0\.1)"""
    r"""|@import\s+(?:url\()?["']?https?://(?!localhost|127\.0\.0\.1)"""
    r"""|\bimport\s+[^;]{0,80}["']https?://(?!localhost|127\.0\.0\.1)"""
    r"""|url\(\s*["']?https?://(?!localhost|127\.0\.0\.1)""",
    re.IGNORECASE,
)


def test_ui_is_self_contained():
    for name in ("index.html", "app.js", "styles.css"):
        text = (UI_DIR / name).read_text(encoding="utf-8")
        hits = CROSS_ORIGIN.findall(text)
        assert not hits, f"{name} references external resources: {hits}"
        assert "fonts.googleapis" not in text and "cdn." not in text.lower()
