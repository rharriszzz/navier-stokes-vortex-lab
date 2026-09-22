#!/usr/bin/env bash
# Render the three bounded inspection frames in one externally approved call.
set -u

POV_RAY="${POV_RAY:-povray}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-300}"
WIDTH="${WIDTH:-640}"
HEIGHT="${HEIGHT:-360}"
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/povray-three-frames}"

if ! command -v "$POV_RAY" >/dev/null 2>&1; then
  echo "ERROR: POV_RAY=$POV_RAY is not on PATH." >&2
  exit 2
fi
if ! command -v gtimeout >/dev/null 2>&1; then
  echo "ERROR: gtimeout is required." >&2
  exit 2
fi
if [[ ! -f fluid.pov ]]; then
  echo "ERROR: run this script from the repository root." >&2
  exit 2
fi

mkdir -p "$OUTPUT_DIR"
for frame in 0001 0120 0240; do
  if [[ ! -f "positions/frame${frame}.inc" ]]; then
    echo "ERROR: missing positions/frame${frame}.inc" >&2
    exit 2
  fi
done

echo "Rendering frames 1, 120 and 240 at ${WIDTH}x${HEIGHT}."
echo "Each frame has a ${TIMEOUT_SECONDS}s bound."

for frame in 0001 0120 0240; do
  output="$OUTPUT_DIR/frame"
  frame_number=$((10#$frame))
  output_frame="$(printf '%03d' "$frame_number")"
  expected="$OUTPUT_DIR/frame${output_frame}.png"
  echo "--- frame ${frame} ---"
  gtimeout --signal=KILL "$TIMEOUT_SECONDS" "$POV_RAY" fluid.pov \
    "+W$WIDTH" "+H$HEIGHT" \
    +KFI1 +KFF240 "+SF$frame_number" "+EF$frame_number" +KI0 +KF1 \
    +FN -d -V +A0.2 -J "+O$output"
  status=$?
  echo "status: $status"
  if [[ "$status" -ne 0 ]]; then
    echo "STOP: frame ${frame} failed." >&2
    exit "$status"
  fi
  if [[ ! -f "$expected" ]]; then
    echo "STOP: POV-Ray reported success but produced no $expected." >&2
    exit 1
  fi
  file "$expected"
done

echo "All three separated frames were rendered: $OUTPUT_DIR/frame{0001,0120,0240}.png"
