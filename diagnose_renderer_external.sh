#!/usr/bin/env bash
# Run from an external host execution context on Mac, never the agent sandbox.
# Each invocation writes fresh output; existing examples are read-only inputs.
set -euo pipefail

POV_RAY="${POV_RAY:-povray}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-30}"
BEADS_SCENE="${BEADS_SCENE:-../beads/beads.pov}"
POV_INCLUDE="${POV_INCLUDE:-/opt/local/share/povray-3.7/include}"
POV_EXAMPLE="${POV_EXAMPLE:-/opt/local/share/povray-3.7/scenes/objects/torus1.pov}"
case "${1:-}" in
  ""|explicit-camera-only) ;;
  *) echo "Usage: bash $0 [explicit-camera-only]" >&2; exit 2 ;;
esac
command -v "$POV_RAY" >/dev/null
command -v gtimeout >/dev/null
for input in tests/scenes/centered_sphere.pov tests/scenes/explicit_camera.pov "$BEADS_SCENE" "$POV_EXAMPLE"; do
  [[ -f "$input" ]] || { echo "Missing input: $input" >&2; exit 2; }
done
output_dir="$(mktemp -d /tmp/povray-renderer-comparison.XXXXXX)"
echo "Evidence directory: $output_dir"
shasum -a 256 "$(command -v "$POV_RAY")" tests/scenes/centered_sphere.pov tests/scenes/explicit_camera.pov \
  "$BEADS_SCENE" "$POV_EXAMPLE" > "$output_dir/inputs.sha256"

render() {
  local name="$1" scene="$2"
  shift 2
  local status=0
  gtimeout --signal=KILL "$TIMEOUT_SECONDS" "$POV_RAY" \
    "+I$scene" "+L$POV_INCLUDE" +W160 +H120 +WT2 +FN -D -V -A -J \
    "+O$output_dir/$name.png" "$@" > "$output_dir/$name.log" 2>&1 || status=$?
  echo "$name status: $status"
  if [[ "$status" -ne 0 ]]; then
    tail -n 40 "$output_dir/$name.log"
    return "$status"
  fi
  [[ -s "$output_dir/$name.png" ]] || { echo "Missing PNG" >&2; return 1; }
  sed -n '/Render Statistics/,$p' "$output_dir/$name.log"
}

if [[ "${1:-}" == "explicit-camera-only" ]]; then
  render explicit_camera tests/scenes/explicit_camera.pov
  exit 0
fi

render sphere tests/scenes/centered_sphere.pov
render sphere_no_bounds tests/scenes/centered_sphere.pov Bounding=Off
render explicit_camera tests/scenes/explicit_camera.pov
render beads "$BEADS_SCENE" +K0
render official_torus "$POV_EXAMPLE"
echo "Render commands completed; inspect PNGs before declaring visual success."
