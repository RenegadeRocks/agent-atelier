#!/bin/bash
set -e
cd "$(dirname "$0")/.."
PY=.venv/bin/python
show() { echo; echo "\$ $*"; sleep 1.5; "$@"; }
banner() { echo; echo "=============================================================="; echo "  $1"; echo "=============================================================="; echo; sleep 2; }

banner "STEP 3 · The studio produces the first PLANNED slot - no idea given by any human"
show $PY tools/produce_from_plan.py brands/tapri/brand_kit.yaml

banner "STEP 4 · Export the studio floor for the owner's console"
show $PY tools/export_floor_state.py
