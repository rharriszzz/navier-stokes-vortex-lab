#!/usr/bin/env bash
# Run one POV-Ray render without a timeout so Activity Monitor can sample it.
# Usage: ./run_povray_activity_monitor.sh [scene.pov]
set -u

POV_RAY="${POV_RAY:-povray}"
SCENE="${1:-fluid.pov}"
OUTPUT="${OUTPUT:-/tmp/povray-activity-monitor-frame}"

if ! command -v "$POV_RAY" >/dev/null 2>&1; then
  echo "ERROR: POV_RAY=$POV_RAY is not on PATH." >&2
  exit 2
fi
if [[ ! -f "$SCENE" ]]; then
  echo "ERROR: scene not found: $SCENE" >&2
  exit 2
fi

echo "This command has no timeout. Stop it with Ctrl-C after sampling it."
echo "In Activity Monitor, search for povray, select it, and use More (...) > Sample Process."
echo "Scene: $SCENE"
echo "Output: $OUTPUT.png"
echo "PID will be printed below."

"$POV_RAY" \
  "+I$SCENE" \
  +W160 +H90 \
  +KFI1 +KFF1 +KI0 +KF1 \
  +FN -d -V +A0.2 -J \
  "+O$OUTPUT" &
POV_PID=$!
echo "POV-Ray PID: $POV_PID"
echo "Command: $POV_RAY +I$SCENE +W160 +H90 +KFI1 +KFF1 +KI0 +KF1 +FN -d -V +A0.2 -J +O$OUTPUT"
wait "$POV_PID"
STATUS=$?
echo "POV-Ray exited with status: $STATUS"
if [[ -f "$OUTPUT.png" ]]; then
  file "$OUTPUT.png"
else
  echo "No PNG was produced: $OUTPUT.png"
fi
exit "$STATUS"
