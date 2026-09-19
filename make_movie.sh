#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

FPS="${FPS:-30}"

mkdir -p movie

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: ffmpeg is not on PATH." >&2
  exit 1
fi

# POV-Ray normally numbers the generated animation images starting at 1.
# Detect the actual digit count and starting name rather than assuming one
# particular POV-Ray filename convention.
FIRST_FRAME="$(find frames -maxdepth 1 -type f -name 'frame*.png' | sort | head -n 1 || true)"

if [[ -z "$FIRST_FRAME" ]]; then
  echo "ERROR: no PNG frames found in frames/." >&2
  exit 1
fi

echo "First frame: $FIRST_FRAME"

# The glob input is intentionally used because POV-Ray installations differ in
# how many digits they append. ffmpeg's glob support keeps this script portable.
ffmpeg -y \
  -framerate "$FPS" \
  -pattern_type glob \
  -i 'frames/frame*.png' \
  -c:v libx264 \
  -crf 18 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  movie/navier-stokes-vortex-lab.mp4

echo "Created movie/navier-stokes-vortex-lab.mp4"
