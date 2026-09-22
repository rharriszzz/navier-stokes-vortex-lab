#!/usr/bin/env bash
# Compare likely POV-Ray timeout causes on macOS versus a restricted sandbox.
set -u

POV_RAY="${POV_RAY:-povray}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-8}"

if ! command -v "$POV_RAY" >/dev/null 2>&1; then
  echo "ERROR: POV_RAY=$POV_RAY is not on PATH." >&2
  exit 2
fi
if command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_BIN=(gtimeout --signal=KILL)
elif command -v timeout >/dev/null 2>&1; then
  TIMEOUT_BIN=(timeout --signal=KILL)
else
  echo "ERROR: gtimeout/timeout is required." >&2
  exit 2
fi

TEST_DIR="$(mktemp -d "${TMPDIR:-/tmp}/povray-timeout-diagnosis.XXXXXX")"
trap 'rm -rf "$TEST_DIR"' EXIT
SCENE="$TEST_DIR/minimal.pov"
LOG_DIR="$TEST_DIR/logs"
mkdir -p "$LOG_DIR"

cat > "$SCENE" <<'POV'
#version 3.7;
global_settings { assumed_gamma 1.0 }
camera { location <0, -3, 1> look_at <0, 0, 0> angle 45 }
light_source { <2, -3, 4> color rgb 1 }
sphere { <0, 0, 0>, 0.8 pigment { color rgb <0.2, 0.5, 1> } }
POV

echo "=== Environment ==="
date
uname -a
command -v "$POV_RAY"
"${TIMEOUT_BIN[@]}" 2 "$POV_RAY" --version 2>&1 | head -3 || true
printf 'cwd: '; pwd
printf 'DISPLAY=%q\n' "${DISPLAY-<unset>}"
printf 'PATH=%s\n' "$PATH"
printf 'uid: '; id -u; printf ' user: '; id -un
printf 'umask: '; umask
printf 'limits:\n'; ulimit -a 2>&1 | sed -n '1,30p'
printf 'filesystem:\n'; df -h "$TEST_DIR" . 2>&1
printf 'output write test: '
if touch "$TEST_DIR/write-test"; then echo pass; else echo fail; fi
printf 'process listing test: '
if ps -p $$ >/dev/null 2>&1; then echo pass; else echo denied-or-unavailable; fi
printf 'window/display services are intentionally not assumed available in a sandbox.\n'

run_case() {
  local name="$1"
  shift
  local output="$TEST_DIR/$name"
  local log="$LOG_DIR/$name.log"
  echo
  echo "=== $name ==="
  echo "command: ${TIMEOUT_BIN[*]} $TIMEOUT_SECONDS $* +O$output"
  set +e
  "${TIMEOUT_BIN[@]}" "$TIMEOUT_SECONDS" "$POV_RAY" "$@" "+O$output" >"$log" 2>&1
  local status=$?
  set -e
  echo "status: $status"
  sed -n '1,40p' "$log"
  if [[ -f "$output.png" ]]; then
    file "$output.png"
    echo "image: PASS"
  else
    echo "image: none"
  fi
}

# A. Startup/CLI behavior, independent of the project scene.
run_case help -h

# B. Headless/display variants on the valid minimal scene.
run_case lowercase-d "+I$SCENE" +W64 +H64 +FN -d -V
run_case plus-d0 "+I$SCENE" +W64 +H64 +FN +d0 -V
run_case display-off "DISPLAY=off" "$SCENE" +W64 +H64 +FN -d -V
run_case quiet-headless "+I$SCENE" +W64 +H64 +FN -d

# C. Project input and output-path behavior, still one tiny frame.
if [[ -f fluid.pov ]]; then
  run_case project-tiny +Ifluid.pov +W64 +H64 +KFI1 +KFF1 +KI0 +KF1 +FN -d -V
else
  echo; echo "=== project-tiny ==="; echo "skipped: fluid.pov not found"
fi

echo
echo "=== Interpretation ==="
echo "status 0 + PNG: this variant works."
echo "status 124: timeout utility expired; status 137: timeout sent SIGKILL."
echo "Parse errors mean POV-Ray started; startup warnings alone do not prove a render hang."
echo "Compare this report with an interactive Mac run of the same script."
