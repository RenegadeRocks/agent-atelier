#!/bin/bash
# FULL PRODUCT DEMO — part C: the poller obeys the human, the kit is delivered.
set -e
cd "$(dirname "$0")/.."
PY=.venv/bin/python

show() {
  echo
  echo "\$ $*"
  sleep 1.5
  "$@"
}

banner() {
  echo; echo "=============================================================="
  echo "  $1"
  echo "=============================================================="; echo
  sleep 2
}

banner "STEP 6 · The poller obeys the human decision - re-gates, then exports"
KIT=$(ls -td brands/*/brand_kit.yaml 2>/dev/null | head -1)
SLUG=$(basename "$(dirname "$KIT")")
show $PY -c "from app.approval_poller import run_poller_tick; run_poller_tick('$KIT', '$SLUG')"

banner "STEP 7 · The deliverable: a ready-to-post kit, made for human hands"
KDIR=$(ls -td brands/$SLUG/handoff/*/ 2>/dev/null | head -1 || true)
if [ -n "$KDIR" ]; then
  echo "--- $KDIR"
  ls -la "$KDIR"
  echo
  echo "--- caption.txt ---"
  cat "$KDIR/caption.txt" 2>/dev/null || true
fi

banner "DONE · Brand in. Cadence planned. Piece made. Human held the gate."
