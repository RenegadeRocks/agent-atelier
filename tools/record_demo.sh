#!/bin/bash
# Record tools/demo_run.sh as a real terminal session and render it to mp4.
# Waits are compressed (idle-time cap), never cut — the run stays honest.
set -e
cd "$(dirname "$0")/.."
OUT=${1:-demo}
asciinema rec --overwrite --window-size 100x30 --command "bash tools/demo_run.sh" "$OUT.cast"
agg --font-size 18 --idle-time-limit 6 --theme asciinema "$OUT.cast" "$OUT.gif"
ffmpeg -y -loglevel error -i "$OUT.gif" -vf "fps=30,scale=1920:-2:flags=lanczos,format=yuv420p" -c:v libx264 -crf 18 "$OUT.mp4"
rm -f "$OUT.gif"
echo "recorded: $OUT.cast  rendered: $OUT.mp4"
