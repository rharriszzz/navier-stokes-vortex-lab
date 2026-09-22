#!/usr/bin/env bash
# Internal administrator phase, called by rebuild_povray.sh after authentication.
set -euo pipefail
[[ "$EUID" -eq 0 && "$#" -eq 1 ]] || { echo 'Use rebuild_povray.sh as your normal user.' >&2; exit 2; }
bundle="$(cd "$(dirname "$0")" && pwd)"
run_dir="$1"
overlay=/opt/local/var/macports/local-sources/vortex-lab
source_conf=/opt/local/etc/macports/sources.conf
port_dir="$overlay/graphics/povray"

if ! cmp -s "$source_conf" "$bundle/sources.conf.before" && \
   ! cmp -s "$source_conf" "$bundle/sources.conf.after"; then
  echo 'STOP: sources.conf has changed; review it before installing this override.' >&2
  exit 2
fi
for relative in Portfile files/truetype.cpp.patch files/patch-lseek64.diff files/patch-vfe-uint.diff; do
  if [[ -e "$port_dir/$relative" ]] && ! cmp -s "$port_dir/$relative" "$bundle/ports/graphics/povray/$relative"; then
    echo "STOP: preserving different existing local recipe: $port_dir/$relative" >&2
    exit 2
  fi
done

cp -p "$source_conf" "$run_dir/sources.conf.backup"
/usr/bin/install -d -m 755 "$port_dir/files"
for relative in Portfile files/truetype.cpp.patch files/patch-lseek64.diff files/patch-vfe-uint.diff; do
  /usr/bin/install -m 644 "$bundle/ports/graphics/povray/$relative" "$port_dir/$relative"
done
/opt/local/bin/portindex -e "$overlay"
/usr/bin/install -m 644 "$bundle/sources.conf.after" "$source_conf"
[[ "$(/opt/local/bin/port -q dir povray)" == "$port_dir" ]] || {
  echo 'STOP: MacPorts did not select the local recipe.' >&2; exit 2;
}

# Rebuild the same release against its already-installed dependencies. Avoid a
# broad dependency upgrade or unrelated rev-upgrade; retain the old port image.
# The verified temporary build used these existing libraries successfully.
/opt/local/bin/gtimeout --signal=TERM --kill-after=30s 1800 \
  /opt/local/bin/port -n -s upgrade --no-rev-upgrade povray build.jobs=2
/opt/local/bin/port installed povray
/opt/local/bin/port -q installed povray | /usr/bin/grep -Eq '@3\.7\.0\.8_6.*\(active\)' || {
  echo 'STOP: the expected rebuilt revision is not active.' >&2; exit 1;
}
/usr/bin/strings /opt/local/bin/povray > "$run_dir/binary-strings.txt"
/usr/bin/grep -E '^-pipe .*fno-fast-math' "$run_dir/binary-strings.txt" > "$run_dir/compiler-flags.txt"
if /usr/bin/grep -Eq '(^|[[:space:]])-ffast-math([[:space:]]|$)' "$run_dir/compiler-flags.txt"; then
  echo 'STOP: compiler flags still enable fast-math.' >&2
  exit 1
fi
cat "$run_dir/compiler-flags.txt"
echo 'INSTALLATION COMPLETE: POV-Ray 3.7.0.8_6, conservative math.'
