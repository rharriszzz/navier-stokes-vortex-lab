#!/usr/bin/env bash
# Minimal Mac POV-Ray CLI reproduction for the R109 renderer failure.
set -u

POV_RAY="${POV_RAY:-povray}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-10}"

if ! command -v "$POV_RAY" >/dev/null 2>&1; then
  echo "ERROR: POV_RAY=$POV_RAY is not on PATH." >&2
  exit 2
fi

TIMEOUT_CMD=""
if command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_CMD="gtimeout --signal=KILL"
elif command -v timeout >/dev/null 2>&1; then
  TIMEOUT_CMD="timeout --signal=KILL"
else
  echo "ERROR: install GNU coreutils for gtimeout/timeout, or run the POV-Ray command manually." >&2
  exit 2
fi

TEST_DIR="$(mktemp -d "${TMPDIR:-/tmp}/povray-mac-repro.XXXXXX")"
trap 'rm -rf "$TEST_DIR"' EXIT

SCENE="$TEST_DIR/minimal.pov"
OUTPUT="$TEST_DIR/minimal"
LOG="$TEST_DIR/povray.log"

cat > "$SCENE" <<'POV'
#version 3.7;
camera { location <0, -3, 1> look_at <0, 0, 0> }
light_source { <2, -3, 4> color rgb 1 }
sphere { <0, 0, 0>, 0.8 pigment { color rgb <0.2, 0.5, 1> } }
POV

echo "POV-Ray: $(command -v "$POV_RAY")"
echo "Timeout: ${TIMEOUT_SECONDS}s"
echo "Scene: $SCENE"
echo "Command: $TIMEOUT_CMD $TIMEOUT_SECONDS $POV_RAY +I$SCENE +W64 +H64 +FN -D -V +O$OUTPUT"

set +e
$TIMEOUT_CMD "$TIMEOUT_SECONDS" "$POV_RAY" \
  "+I$SCENE" +W64 +H64 +FN -D -V "+O$OUTPUT" >"$LOG" 2>&1
STATUS=$?
set -e

echo "Exit status: $STATUS"
echo "--- POV-Ray output ---"
sed -n '1,120p' "$LOG"
echo "--- Output files ---"
find "$TEST_DIR" -maxdepth 1 -type f -print -exec file {} \;

if [[ -f "$OUTPUT.png" ]]; then
  echo "PASS: POV-Ray emitted $OUTPUT.png"
  exit 0
fi

echo "FAIL: POV-Ray did not emit $OUTPUT.png"
echo "Search terms: MacPorts POV-Ray macOS scheduleApplicationNotification Connection Invalid headless CLI"
exit "$STATUS"
