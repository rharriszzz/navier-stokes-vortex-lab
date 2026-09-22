#!/usr/bin/env bash
# Render small scene variants in one external approval to isolate blank output.
set -u

POV_RAY="${POV_RAY:-povray}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-300}"
WIDTH="${WIDTH:-640}"
HEIGHT="${HEIGHT:-360}"
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/povray-visibility-diagnosis}"

if ! command -v "$POV_RAY" >/dev/null 2>&1 || ! command -v gtimeout >/dev/null 2>&1; then
  echo "ERROR: povray and gtimeout are required." >&2
  exit 2
fi
if [[ ! -f positions/frame0001.inc ]]; then
  echo "ERROR: positions/frame0001.inc is missing." >&2
  exit 2
fi

mkdir -p "$OUTPUT_DIR"
PROBE="$OUTPUT_DIR/tracer-only.pov"
CAMERA_PROBE="$OUTPUT_DIR/camera-only.pov"
SIMPLE_CAMERA_PROBE="$OUTPUT_DIR/simple-camera.pov"
REVERSE_CAMERA_PROBE="$OUTPUT_DIR/reverse-camera.pov"
EXPLICIT_CAMERA_PROBE="$OUTPUT_DIR/explicit-camera.pov"
cat > "$PROBE" <<'POV'
#version 3.7;
global_settings { assumed_gamma 1.0 }
#include "materials.inc"
#include "tracer.inc"
#include "positions/frame0001.inc"
background { color rgb <0.97, 0.98, 1.00> }
camera {
  perspective
  location <3.35, -4.65, 2.85>
  look_at <0, 0, 0>
  sky <0, 0, 1>
  angle 34
}
light_source { <4.0, -5.5, 7.0> color rgb <1.0, 0.96, 0.90> * 1.25 }
plane { z, -1.25 pigment { color rgb <0.86, 0.87, 0.90> } finish { diffuse 0.80 } }
RenderTracers()
POV

cat > "$CAMERA_PROBE" <<'POV'
#version 3.7;
global_settings { assumed_gamma 1.0 }
background { color rgb <0.97, 0.98, 1.00> }
camera {
  perspective
  location <3.35, -4.65, 2.85>
  look_at <0, 0, 0>
  sky <0, 0, 1>
  angle 34
}
light_source { <4.0, -5.5, 7.0> color rgb <1.0, 0.96, 0.90> * 1.25 }
plane { z, -1.25 pigment { color rgb <0.86, 0.87, 0.90> } finish { diffuse 0.80 } }
sphere { <0, 0, 0>, 0.30 pigment { color rgb <1, 0, 0> } finish { diffuse 0.8 } }
POV

cat > "$SIMPLE_CAMERA_PROBE" <<'POV'
#version 3.7;
global_settings { assumed_gamma 1.0 }
background { color rgb <0.97, 0.98, 1.00> }
camera { perspective location <0, 0, -3> look_at <0, 0, 0> angle 45 }
light_source { <2, -3, -4> color rgb 1 }
sphere { <0, 0, 0>, 0.50 pigment { color rgb <1, 0, 0> } finish { diffuse 0.8 } }
POV

cat > "$EXPLICIT_CAMERA_PROBE" <<'POV'
#version 3.7;
global_settings { assumed_gamma 1.0 }
background { color rgb <0.97, 0.98, 1.00> }
camera {
  perspective
  location <0, -3, 0>
  direction y
  up z
  right x*image_width/image_height
  angle 45
}
light_source { <2, -3, -4> color rgb 1 }
sphere { <0, 0, 0>, 0.50 pigment { color rgb <1, 0, 0> } finish { diffuse 0.8 } }
POV

cat > "$REVERSE_CAMERA_PROBE" <<'POV'
#version 3.7;
global_settings { assumed_gamma 1.0 }
background { color rgb <0.97, 0.98, 1.00> }
camera { perspective location <0, 0, 3> look_at <0, 0, 0> angle 45 }
light_source { <2, -3, 4> color rgb 1 }
sphere { <0, 0, 0>, 0.50 pigment { color rgb <1, 0, 0> } finish { diffuse 0.8 } }
POV

render_one() {
  local name="$1"
  shift
  local output="$OUTPUT_DIR/$name"
  echo "--- $name ---"
  set +e
  gtimeout --signal=KILL "$TIMEOUT_SECONDS" "$POV_RAY" fluid.pov \
    +W"$WIDTH" +H"$HEIGHT" +KFI1 +KFF240 +SF1 +EF1 +KI0 +KF1 \
    +FN -d -V +A0.2 -J "$@" +O"$output"
  local status=$?
  set -e
  echo "status: $status"
  [[ -f "$output".png ]] && file "$output".png || true
  return "$status"
}

render_one full-scene-frame || exit $?
render_one overlays Declare=ShowCore=1 Declare=ShowActuators=1 Declare=ShowSensors=1 || exit $?

echo "--- tracer-only ---"
set +e
gtimeout --signal=KILL "$TIMEOUT_SECONDS" "$POV_RAY" \
  "+I$PROBE" +W"$WIDTH" +H"$HEIGHT" +FN -d -V +A0.2 -J \
  +O"$OUTPUT_DIR/tracer-only"
status=$?
set -e
echo "status: $status"
[[ -f "$OUTPUT_DIR/tracer-only.png" ]] && file "$OUTPUT_DIR/tracer-only.png" || true

echo "--- camera-only ---"
set +e
gtimeout --signal=KILL "$TIMEOUT_SECONDS" "$POV_RAY" \
  "+I$CAMERA_PROBE" +W"$WIDTH" +H"$HEIGHT" +FN -d -V +A0.2 -J \
  +O"$OUTPUT_DIR/camera-only"
status=$?
set -e
echo "status: $status"
[[ -f "$OUTPUT_DIR/camera-only.png" ]] && file "$OUTPUT_DIR/camera-only.png" || true

echo "--- simple-camera ---"
set +e
gtimeout --signal=KILL "$TIMEOUT_SECONDS" "$POV_RAY" \
  "+I$SIMPLE_CAMERA_PROBE" +W"$WIDTH" +H"$HEIGHT" +FN -d -V +A0.2 -J \
  +O"$OUTPUT_DIR/simple-camera"
status=$?
set -e
echo "status: $status"
[[ -f "$OUTPUT_DIR/simple-camera.png" ]] && file "$OUTPUT_DIR/simple-camera.png" || true

echo "--- reverse-camera ---"
set +e
gtimeout --signal=KILL "$TIMEOUT_SECONDS" "$POV_RAY" \
  "+I$REVERSE_CAMERA_PROBE" +W"$WIDTH" +H"$HEIGHT" +FN -d -V +A0.2 -J \
  +O"$OUTPUT_DIR/reverse-camera"
status=$?
set -e
echo "status: $status"
[[ -f "$OUTPUT_DIR/reverse-camera.png" ]] && file "$OUTPUT_DIR/reverse-camera.png" || true

echo "--- explicit-camera ---"
set +e
gtimeout --signal=KILL "$TIMEOUT_SECONDS" "$POV_RAY" \
  "+I$EXPLICIT_CAMERA_PROBE" +W"$WIDTH" +H"$HEIGHT" +FN -d -V +A0.2 -J \
  +O"$OUTPUT_DIR/explicit-camera"
status=$?
set -e
echo "status: $status"
[[ -f "$OUTPUT_DIR/explicit-camera.png" ]] && file "$OUTPUT_DIR/explicit-camera.png" || true

echo "Outputs are in $OUTPUT_DIR"
