#!/usr/bin/env bash
# Run in a normal Mac Terminal after the PC handoff has been published.
# Copies all inputs to a separate log directory and never writes to the repo.
set -euo pipefail
[[ "$(uname -s)" == Darwin && "$EUID" -ne 0 ]] || {
  echo 'Run this as your normal Mac user, not with sudo in front.' >&2; exit 2;
}
bundle="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "$bundle/../.." && pwd)"
for tool in /opt/local/bin/port /opt/local/bin/portindex /opt/local/bin/gtimeout; do
  [[ -x "$tool" ]] || { echo "Missing required tool: $tool" >&2; exit 2; }
done
[[ -f "$repo/tests/scenes/centered_sphere.pov" ]] || { echo 'Missing sphere fixture.' >&2; exit 2; }
if [[ "${1:-}" == --check ]]; then
  cmp -s /opt/local/etc/macports/sources.conf "$bundle/sources.conf.before" || \
    cmp -s /opt/local/etc/macports/sources.conf "$bundle/sources.conf.after"
  /opt/local/bin/port -D "$bundle/ports/graphics/povray" info --name --version --revision
  echo 'Preflight complete; no installation or build was launched.'
  exit 0
fi
[[ "$#" -eq 0 ]] || { echo "Usage: bash $0 [--check]" >&2; exit 2; }

log_root="$HOME/Library/Logs/navier-stokes-vortex-lab/povray-rebuild"
mkdir -p "$log_root"
run_dir="$(mktemp -d "$log_root/run.XXXXXX")"
cp -R "$bundle" "$run_dir/bundle"
cp "$repo/tests/scenes/centered_sphere.pov" "$run_dir/sphere.pov"
# The macports build user needs traversal to read its separate root-owned
# installed Portfile, not this private log/input snapshot.
echo "Build log: $run_dir/build.log"
echo 'Enter your administrator password in Terminal when sudo asks.'
echo 'Keep this Terminal open. Two compiler jobs; 30-minute package-operation limit.'
printf 'awaiting-administrator-authentication\n' > "$run_dir/status.txt"
status=0
sudo /bin/bash "$run_dir/bundle/install_povray_root.sh" "$run_dir" \
  2>&1 | tee "$run_dir/build.log" || status=$?
if [[ "$status" -ne 0 ]]; then
  printf 'installation-failed status=%s\n' "$status" > "$run_dir/status.txt"
  echo "Build stopped (status $status). Keep $run_dir for diagnosis." >&2
  exit "$status"
fi

printf 'installed-smoke-test-running\n' > "$run_dir/status.txt"
if /opt/local/bin/gtimeout --signal=KILL 30 /opt/local/bin/povray \
    "+I$run_dir/sphere.pov" "+O$run_dir/sphere.png" \
    +W160 +H120 +WT2 +FN -D -V -A -J > "$run_dir/sphere.log" 2>&1 && \
    [[ -s "$run_dir/sphere.png" ]] && \
    awk '$1 == "Sphere" && $3 > 0 { found = 1 } END { exit !found }' "$run_dir/sphere.log"; then
  printf 'installed-sphere-intersections-passed; visual-inspection-pending\n' > "$run_dir/status.txt"
  echo "Rebuild succeeded; sphere intersections passed. Inspect: $run_dir/sphere.png"
else
  printf 'installed-smoke-test-failed\n' > "$run_dir/status.txt"
  echo "Installation finished, but sphere smoke test failed. See $run_dir/sphere.log" >&2
  exit 1
fi
