# Conservative-math MacPorts POV-Ray rebuild

R141–R144 authorize this rebuild **after** publishing the PC handoff. The user
runs it in an ordinary Mac Terminal and supplies the administrator password
there. The original handoff was delivered as `4101af9`; the user subsequently
installed revision 6 and the sphere test passed intersections and visual
inspection (R150–R155). Effective flags are `-Os -fno-fast-math`, not the intended
`-O2`; exact recompilation scope is unverified. Do not rerun just to settle
that question. R155 confirms the PC never started and Mac retains ownership.

```bash
bash /Users/rharris/git/navier-stokes-vortex-lab/packaging/macports/rebuild_povray.sh
```

Do not put `sudo` before this command. The launcher requests it for the package
installation phase only. Password typing is invisible. Keep Terminal open;
the operation uses two compiler jobs and a 30-minute package-operation limit
(plus up to 30 seconds for termination). Do not run another MacPorts operation
concurrently. No duration or performance improvement is promised.

## What it changes

The bundled recipe is the installed MacPorts `povray` 3.7.0.8 revision 5 recipe
and its three unchanged compatibility patches, with only these build changes:

- local revision 6, built from source;
- `--disable-optimiz`, preventing upstream's automatic fast-math flags;
- ordinary `-O2` optimization and explicit `-fno-fast-math`.

The source SHA-256 remains
`e86427f83b9bc356e6694bd053eb23b310aa0f942ac9215860c86f0035865ce2`.
See the [same-source diagnosis](../../docs/rendering/POVRAY_MAC_BUILD_DIAGNOSIS.md).

The installer creates the local recipe repository at
`/opt/local/var/macports/local-sources/vortex-lab`, indexes it, and puts its
`file://` entry before the existing default in `/opt/local/etc/macports/sources.conf`.
It first saves that configuration and refuses unexpected configuration changes
or differing existing local recipe files. The bundled before/after files match
the configuration checked on Mac `fire.lan`; this is not a universal installer.

MacPorts owns the build and activation; the launcher does not copy a temporary
binary over `/opt/local/bin/povray`. Existing POV-Ray configuration is preserved.
The old installed revision is retained as an inactive package image. `-n` and
`--no-rev-upgrade` avoid broad dependency upgrades: the same release already
passed the temporary-build checks against this Mac's installed libraries.
If dependency resolution fails, retain the log and review it; do not bypass
that failure or automatically upgrade unrelated packages.

The override survives upstream tree refreshes but also **shadows future
official POV-Ray recipes**. Review it when updating POV-Ray and retire it once
an official build passes the conservative-math checks.
[MacPorts local-repository documentation](https://guide.macports.org/#development.local-repositories).

## Logs, checks and recovery

Observed first-run caveat: the inherited recipe refuses to build while
`openexr` is active, despite using the separate `openexr2` dependency. The
user temporarily deactivated `openexr` and retried. ImageMagick/OpenCV depend
on it, so it must be reactivated after the build; this launcher does not
automatically perform or undo deactivation. R157 verifies the user's subsequent
reactivation of `openexr @3.4.15_0`, with openexr2 and POV-Ray revision 6 still
active. Review this preflight/restoration gap before another installation.

Before authentication, the launcher snapshots its inputs to a private run
directory under:

```text
~/Library/Logs/navier-stokes-vortex-lab/povray-rebuild/run.XXXXXX/
```

Everything thereafter is independent of the project checkout, so the PC may
own the repository while this user-managed Mac build runs. Logs and generated
images stay on the Mac; no binaries or build caches are transferred.

`build.log` records package output; `sources.conf.backup` preserves the original
configuration. `compiler-flags.txt` must show conservative flags, and the active
package must be `povray @3.7.0.8_6`. The ordinary-user smoke test renders the
canonical sphere with two threads and a 30-second bound, checks the PNG exists
and requires successful sphere intersections. `status.txt` records the outcome.
Inspect `sphere.png`: a visible red sphere is required. This automatic check is
not a substitute for visual inspection or the later beads/project-frame checks.

If installation or rendering fails, stop and keep the printed run directory.
The local recipe/configuration may already be installed even if the build
failed; do not assume automatic rollback. Inspect `port installed povray` and
the log before choosing recovery. Restoring the original source configuration
would remove recipe precedence, but would not itself reactivate an older binary.
The older revision is known to have the rendering fault, so reverting is only
package recovery, not a renderer fix. No automatic deletion/rollback is included.

Read-only preparation checks:

```bash
bash -n packaging/macports/rebuild_povray.sh
bash -n packaging/macports/install_povray_root.sh
bash packaging/macports/rebuild_povray.sh --check
/opt/local/bin/port -D packaging/macports/ports/graphics/povray lint
```

The installed sphere has now passed visual inspection. Beads and project
1/120/240 checks remain the [next Mac task](../../SESSION_HANDOFF.md#next-task),
with OpenEXR restoration already verified in R157. The user clarified that the PC did not start;
no PC ownership should be inferred from the earlier prepared handoff. The
current notes are included in R158's explicitly authorized publication before
a fresh Mac chat; actual delivery is reported separately from this document.
