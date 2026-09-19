#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

NFRAMES="${NFRAMES:-240}"
WIDTH="${WIDTH:-1280}"
HEIGHT="${HEIGHT:-720}"
AA_THRESHOLD="${AA_THRESHOLD:-0.2}"

mkdir -p frames

if ! command -v povray >/dev/null 2>&1; then
  echo "ERROR: povray is not on PATH." >&2
  exit 1
fi

if [[ ! -f positions/frame0001.inc ]]; then
  echo "Trajectory files not found; generating them first."
  python3 make_trajectories.py --frames "$NFRAMES"
fi

echo "Rendering $NFRAMES frames at ${WIDTH}x${HEIGHT} ..."

povray fluid.pov \
  +W"$WIDTH" +H"$HEIGHT" \
  +KFI1 +KFF"$NFRAMES" \
  +KI0 +KF1 \
  +FN -V \
  +A"$AA_THRESHOLD" -J \
  +Oframes/frame

echo "Finished. Rendered frames are in frames/."
