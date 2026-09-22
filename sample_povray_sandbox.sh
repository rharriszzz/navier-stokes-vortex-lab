#!/usr/bin/env bash
# Launch POV-Ray only inside this shell, sample its stack locally, then stop it.
set -u

POV_RAY="${POV_RAY:-povray}"
SAMPLE_SECONDS="${SAMPLE_SECONDS:-3}"
TEST_DIR="$(mktemp -d "${TMPDIR:-/tmp}/povray-sandbox-sample.XXXXXX")"
trap 'rm -rf "$TEST_DIR"' EXIT
SCENE="$TEST_DIR/minimal.pov"
LOG="$TEST_DIR/povray.log"
STACK="$TEST_DIR/povray.sample.txt"

cat > "$SCENE" <<'POV'
#version 3.7;
global_settings { assumed_gamma 1.0 }
camera { location <0, -3, 1> look_at <0, 0, 0> angle 45 }
light_source { <2, -3, 4> color rgb 1 }
sphere { <0, 0, 0>, 0.8 pigment { color rgb <0.2, 0.5, 1> } }
POV

echo "POV-Ray: $(command -v "$POV_RAY" 2>&1 || true)"
echo "Scene: $SCENE"
echo "Sample duration: ${SAMPLE_SECONDS}s"

set +e
"$POV_RAY" "+I$SCENE" +W64 +H64 +FN -d -V "+O$TEST_DIR/output" >"$LOG" 2>&1 &
POV_PID=$!
set -e
echo "POV-Ray child PID: $POV_PID"

sleep 1
if command -v lldb >/dev/null 2>&1 && command -v gtimeout >/dev/null 2>&1; then
  echo "Running bounded lldb attach"
  set +e
  gtimeout --signal=KILL 5 lldb -p "$POV_PID" \
    -o 'thread backtrace all' -o detach -o quit \
    >"$TEST_DIR/lldb.stdout" 2>"$TEST_DIR/lldb.stderr"
  LLDB_STATUS=$?
  set -e
  echo "lldb status: $LLDB_STATUS"
  sed -n '1,120p' "$TEST_DIR/lldb.stdout"
  sed -n '1,80p' "$TEST_DIR/lldb.stderr"
else
  echo "lldb or gtimeout is unavailable."
fi

if command -v sample >/dev/null 2>&1; then
  echo "Running: sample $POV_PID $SAMPLE_SECONDS -file $STACK"
  set +e
  sample "$POV_PID" "$SAMPLE_SECONDS" -file "$STACK" >"$TEST_DIR/sample.stdout" 2>"$TEST_DIR/sample.stderr"
  SAMPLE_STATUS=$?
  set -e
  echo "sample status: $SAMPLE_STATUS"
  sed -n '1,80p' "$TEST_DIR/sample.stderr"
  if [[ -f "$STACK" ]]; then
    sed -n '1,160p' "$STACK"
  else
    echo "No sample file was produced."
  fi
else
  echo "sample command is unavailable."
fi

echo "Terminating only child PID $POV_PID"
kill -TERM "$POV_PID" 2>/dev/null || true
wait "$POV_PID" 2>/dev/null || true
echo "--- POV-Ray log ---"
sed -n '1,80p' "$LOG"
echo "--- Child cleanup complete ---"
