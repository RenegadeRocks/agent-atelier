"""Serve ui/studio-floor statically and accept Floor Actions. Stdlib only.

POST /action  body: {piece_id, action in [approve, request_changes, reject], note?, rev?}
  - writes ONLY the Owner-Action cell for that piece's row (section 12.2:
    the orchestrator is the SOLE writer of Status; the console submits owner
    signals, never status writes) and appends an Audit row (actor=human).
  - if credentials are unavailable, the action is queued to
    ui/studio-floor/data/actions.jsonl and 202 {queued: true} is returned;
    apply later with tools/apply_floor_actions.py.

The SheetClient interface is injectable for tests: any object with
set_owner_action(piece_id, label) and append_audit(row). It structurally
has NO method that can write the Status column.
"""

import json
import os
import sys
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI_DIR = ROOT / "ui" / "studio-floor"
ACTIONS_PATH = UI_DIR / "data" / "actions.jsonl"
HOST, PORT = "127.0.0.1", 8787
MAX_BODY = 64 * 1024

# action -> the section 12.2 Owner-Action dropdown label
VALID_ACTIONS = {
    "approve": "Approve",
    "request_changes": "Request changes",
    "reject": "Reject",
}

# Origins that may POST /action. Loopback bind alone does not stop a
# malicious page in the owner's browser from POSTing at localhost (the
# classic localhost-CSRF vector, validation MINOR-5); the Origin gate does.
# Allowed: the two names this server answers to, and "null" (a file://
# page). An ABSENT Origin header is also allowed — curl and the
# tools/apply_floor_actions.py CLI fallback send none.
ALLOWED_ORIGINS = {
    "null",
    f"http://127.0.0.1:{PORT}",
    f"http://localhost:{PORT}",
}


def origin_allowed(origin):
    """True when this Origin header value may POST /action.

    None/empty (no header: curl, CLI fallback, some same-origin POSTs) and
    the ALLOWED_ORIGINS set pass; any other origin is a cross-site page
    driving the local server and is refused (403).
    """
    if origin is None or origin == "":
        return True
    return origin in ALLOWED_ORIGINS

# Audit row shape kept aligned with the as-built worksheet + export tool:
# [piece_id, verb, status, detail, actor, ts, operator_id]


class GspreadSheetClient:
    """Live client. Writes ONLY the Owner-Action column (F) on the Queue
    worksheet and appends Audit rows. There is deliberately no method that
    can touch the Status column."""

    OWNER_ACTION_COL = 6  # column F in the as-built Queue schema

    def __init__(self, sheet_id, creds_path):
        import gspread  # lazy: server must start without gspread installed
        gc = gspread.service_account(filename=creds_path)
        self._sh = gc.open_by_key(sheet_id)
        try:
            self._queue = self._sh.worksheet("Queue")
        except Exception:
            self._queue = self._sh.sheet1

    def set_owner_action(self, piece_id, label):
        piece_ids = self._queue.col_values(1)
        if piece_id not in piece_ids:
            raise KeyError(f"piece_id not found in Queue: {piece_id}")
        row_idx = piece_ids.index(piece_id) + 1
        self._queue.update_cell(row_idx, self.OWNER_ACTION_COL, label)

    def append_audit(self, row):
        try:
            ws = self._sh.worksheet("Audit")
        except Exception:
            ws = self._sh.add_worksheet(title="Audit", rows=1000, cols=10)
        ws.append_row(list(row))


def _assert_no_status_writer(client):
    # Structural guard: the injected client must not expose any way to
    # write Status (12.2 sole-writer rule holds even against a bad client).
    offenders = [
        name for name in dir(client)
        if not name.startswith("_") and "status" in name.lower()
    ]
    if offenders:
        raise TypeError(f"SheetClient exposes Status-writing surface: {offenders}")


def _sheet_id():
    sid = os.environ.get("SHEET_ID")
    if sid:
        return sid
    sys.path.insert(0, str(ROOT))
    try:
        from app.agents.config import SHEET_ID
        return SHEET_ID
    except Exception:
        return None


def make_client():
    """Return a live SheetClient, or None when creds/deps are unavailable
    (the caller then queues actions locally)."""
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds or not Path(creds).exists():
        return None
    try:
        import gspread  # noqa: F401
    except ImportError:
        return None
    sid = _sheet_id()
    if not sid:
        return None
    return GspreadSheetClient(sid, creds)


def handle_action(body, client, actions_path=ACTIONS_PATH, operator_id=None):
    """Validate and execute one Floor Action. Returns (http_status, payload).
    Pure of HTTP so tests can drive it with a stub client."""
    if not isinstance(body, dict):
        return 400, {"error": "body must be a JSON object"}
    piece_id = body.get("piece_id")
    action = body.get("action")
    note = body.get("note") or ""
    rev = body.get("rev")
    if not piece_id or not isinstance(piece_id, str):
        return 400, {"error": "piece_id is required"}
    if action not in VALID_ACTIONS:
        return 400, {
            "error": f"action must be one of {sorted(VALID_ACTIONS)}",
            "got": action,
        }
    if not isinstance(note, str):
        return 400, {"error": "note must be a string"}

    operator_id = operator_id or os.environ.get("FLOOR_OPERATOR", "owner")
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    record = {
        "piece_id": piece_id, "action": action, "note": note, "rev": rev,
        "operator_id": operator_id, "ts": ts, "applied": False,
    }

    if client is None:
        actions_path = Path(actions_path)
        actions_path.parent.mkdir(parents=True, exist_ok=True)
        with actions_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return 202, {
            "queued": True,
            "piece_id": piece_id,
            "action": action,
            "hint": "queued locally — apply with tools/apply_floor_actions.py",
        }

    _assert_no_status_writer(client)
    detail = note if rev is None else f"{note} (rev {rev})".strip()
    try:
        client.set_owner_action(piece_id, VALID_ACTIONS[action])
        client.append_audit(
            [piece_id, f"owner_{action}", "", detail, "human", ts, operator_id]
        )
    except Exception as exc:
        return 502, {"error": f"sheet write failed: {exc}", "piece_id": piece_id}
    return 200, {"ok": True, "piece_id": piece_id, "action": action, "ts": ts}


class FloorHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def _send_json(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/action":
            self._send_json(404, {"error": "unknown endpoint"})
            return
        origin = self.headers.get("Origin")
        if not origin_allowed(origin):
            self._send_json(403, {
                "error": "cross-origin POST refused",
                "origin": origin,
            })
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            self._send_json(413, {"error": "body too large"})
            return
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid JSON"})
            return
        status, payload = handle_action(body, self.server.sheet_client)
        self._send_json(status, payload)

    def end_headers(self):
        if self.command == "GET":
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("[floor_serve] %s\n" % (fmt % args))


def main():
    client = make_client()
    if client is None:
        print("floor_serve: no Sheets credentials — Floor Actions will be "
              f"queued to {ACTIONS_PATH.relative_to(ROOT)} (202 queued mode).")
    else:
        print("floor_serve: live Sheets client ready (Owner-Action writes only).")
    server = ThreadingHTTPServer((HOST, PORT), FloorHandler)
    server.sheet_client = client
    print(f"Studio Floor at http://{HOST}:{PORT}/  (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
