#!/bin/bash
# Agent Atelier — start-to-end live demo session (recorded by tools/record_demo.sh).
# Every command below is the real system doing real work: no mocks, no staging.
set -e
cd "$(dirname "$0")/.."
PY=.venv/bin/python

banner() {
  echo
  echo "=============================================================="
  echo "  $1"
  echo "=============================================================="
  echo
  sleep 2
}

banner "AGENT ATELIER - a live, unedited run  ·  brand: Chuski Club, Jaipur"
sleep 1

banner "SCENE 1 · The pipeline: 8 agents take one idea to a finished piece"
$PY tools/run_one_piece.py brands/chuski-club/brand_kit.yaml \
"A pyramid of fruit ice pops stacked on a flat bold hot-pink wall in hard afternoon sun, one mango pop being pulled out mid-heist by a hand from off-frame - poster-like flat color-block composition, youthful loud advertising energy, not documentary"

banner "SCENE 2 · The console feed: export the studio floor from the system of record"
$PY tools/export_floor_state.py

banner "SCENE 3 · The human gate: I approve the piece (one write to ONE cell)"
PIECE=$($PY - << 'EOF'
import json
d = json.load(open("ui/studio-floor/data/state.json"))
q = [p for p in d.get("pieces", []) if "queue" in str(p.get("status","")).lower()]
print(q[-1]["piece_id"] if q else "")
EOF
)
echo "piece awaiting the human: $PIECE"
sleep 2
$PY tools/apply_floor_actions.py --enqueue "{\"piece_id\":\"$PIECE\",\"action\":\"approve\"}"

banner "SCENE 4 · The poller obeys: re-runs the safety gauntlet, exports the Post Kit"
$PY -c "from app.approval_poller import run_poller_tick; run_poller_tick('brands/chuski-club/brand_kit.yaml', 'chuski-club')"

banner "SCENE 5 · The deliverable: a ready-to-post kit, made for human hands"
KIT=$(ls -td brands/chuski-club/handoff/*/ 2>/dev/null | head -1 || true)
if [ -n "$KIT" ]; then
  echo "--- $KIT"
  ls -la "$KIT"
  echo
  echo "--- caption.txt ---"
  cat "$KIT/caption.txt" 2>/dev/null || true
fi

banner "DONE · Nothing published itself. The human held the last gate."
