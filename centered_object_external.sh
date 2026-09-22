#!/usr/bin/env bash
# Render one canonical centered red sphere outside the restricted sandbox.
set -u

POV_RAY="${POV_RAY:-povray}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-300}"
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/povray-centered-object}"

command -v "$POV_RAY" >/dev/null 2>&1 || { echo "ERROR: povray is required." >&2; exit 2; }
command -v gtimeout >/dev/null 2>&1 || { echo "ERROR: gtimeout is required." >&2; exit 2; }
mkdir -p "$OUTPUT_DIR"
scene="$OUTPUT_DIR/centered-object.pov"
output="$OUTPUT_DIR/centered-object"

cat > "$scene" <<'POV'
#version 3.7;
global_settings { assumed_gamma 1.0 }
background { color rgb <0.97, 0.98, 1.00> }
camera {
  perspective
  location <0, 0, -3>
  look_at <0, 0, 0>
  angle 45
}
light_source { <-2, -3, -4> color rgb 1 }
sphere {
  <0, 0, 0>, 0.75
  pigment { color rgb <1, 0, 0> }
  finish { diffuse 0.8 }
}
POV

set +e
gtimeout --signal=KILL "$TIMEOUT_SECONDS" "$POV_RAY" \
  "+I$scene" +W256 +H256 +FN -d -V +A0.2 -J \
  "+O$output"
status=$?
set -e
echo "status: $status"
if [[ -f "$output.png" ]]; then
  file "$output.png"
  echo "PNG: $output.png"
else
  echo "ERROR: no PNG emitted" >&2
fi
exit "$status"
