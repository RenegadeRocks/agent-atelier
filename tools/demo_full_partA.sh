#!/bin/bash
# FULL PRODUCT DEMO — part A: brand birth → weekly cadence → planned piece.
# Real system, no mocks. Recorded by asciinema; waits compressed at render.
set -e
cd "$(dirname "$0")/.."
PY=.venv/bin/python

show() {  # echo the command before running it, like a human typing it
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

banner "AGENT ATELIER — the full promise, live: brand in, weekly posts out"
sleep 1

banner "STEP 1 · A new brand is born in an interview (owner answers live)"
show $PY tools/interview_driver.py demo/brand-packs/tapri-toast-club/

banner "STEP 2 · The scheduler composes the week - the cadence, per brand"
show $PY tools/plan_week.py

banner "STEP 3 · The studio produces the first PLANNED slot - no idea given by any human"
KIT=$(ls -td brands/*/brand_kit.yaml 2>/dev/null | head -1)
echo "newest active kit: $KIT"
show $PY tools/produce_from_plan.py "$KIT"

banner "STEP 4 · Export the studio floor for the owner's console"
show $PY tools/export_floor_state.py
