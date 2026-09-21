# Finish Mac setup and compare it with the PC

Updated 2026-09-21 for R077–R080. This page retains Mac installation and
movie-readiness instructions. Use the new
[Mac and PC performance and memory test plan](MAC_PC_PERFORMANCE_MEMORY_PLAN.md)
for the staged comparison, fixed cases, measurements, proposed budgets,
repetitions, correctness rules and evidence requirements.

## Immediate next step and sequence

R070 launch/report repair and R076 fixture-only monitor implementation are
complete. R079 transferred ownership to Mac for documentation; R080 returns
it to PC after publication. Follow the single
[current handoff task](../../SESSION_HANDOFF.md#next-task): the previously
planned Astra/high review of R076 and bounded live-adapter contract, stopping
before live workloads or benchmarks. Do not replay the completed repairs.

Later steps implement and validate actual OS adapters, establish local movie
readiness, and run frozen workloads sequentially on both computers under
[the new plan](MAC_PC_PERFORMANCE_MEMORY_PLAN.md#1-sequence-and-readiness-gates).
Its optional R067 assembly/observer reference has zero factor/solve events;
it cannot rank physical solves. The q64/q96 physical experiment remains
separate and once-only. Each machine change follows the
[handoff procedure](../../AGENTS.md#switching-between-the-mac-and-pc).

The independent Mac POV-Ray build's completion is still unverified. Check its
outcome when the movie-readiness task is selected; do not start a duplicate
installation or benchmark while it is active. No install, render, benchmark
or live monitor check ran in this documentation task.

## What remains to install

**Let the existing POV-Ray build finish, then verify the command-line tool.**
The other identified project dependencies are installed. Then validate the
movie pipeline; FEM execution needs its own portability and numerical checks.

[R058 live evidence](evidence/r058/mac_readiness.json) supplements the
[R034 hardware snapshot](evidence/r034/mac_snapshot.json) and R046 import/MPI
checks. This is an Apple M4 iMac with 24 GiB RAM.

| Component | Recorded state | Next action |
|---|---|---|
| MacPorts | `/opt/local/bin/port` exists; Homebrew was not found on the inspected PATH | Use MacPorts for POV-Ray. |
| Apple development tools | Xcode selected; `xcrun clang --version` succeeds | No compiler installation identified as missing; actual FEM JIT compilation is still untested. |
| POV-Ray | Absent in R058; user reports a build in progress in R065 | Check that build's result later; verify the executable before the movie check. |
| ffmpeg / ffprobe | Both execute, version 4.4.2; `libx264` encoder is listed | Keep them for the first smoke test; record versions for comparison with the PC. |
| Official Anaconda Miniconda | Existing `navier-stokes-vortex-b1` environment; Python/DOLFINx/PETSc/MPICH metadata identifies `osx-arm64` builds | Activate the existing environment. |
| FEM dependencies and NumPy | R046 imports and two-rank MPICH startup passed | Preserve `environment-b1.yml`; no reinstall identified as necessary. |
| FFCx | Mac and PC metadata identify the same conda-forge `0.10.1 pyhbc3ee6d_1` noarch artifact, including URL and SHA-256 | The module's `0.10.0` string is explained; keep the pin. |
| FEM monitor and reference comparison | Not validated on macOS | Follow the benchmark prerequisites below before a FEM run. |

FFCx identity is compared with [R056 PC evidence](evidence/r056/ffcx_pc_environment.json).
Matching package metadata is provenance evidence, not a numerical comparison.
The [v0.10.1 release](https://github.com/FEniCS/ffcx/releases/tag/v0.10.1)
fixes multiple integrals sharing a quadrature rule; the embedded version string
remained 0.10.0. See [B1 setup](B1_SETUP.md) for the historical-result caveat.

### 1. Install and verify POV-Ray

Run these in Mac Terminal. `sudo` asks for your Mac login password; Terminal
normally does not display characters while you type it.

R065 reports an installation/build already in progress. The install command
below is the original recipe, not an instruction to launch another copy.
Inspect the current build's result first and verify its executable when done.

```bash
sudo /opt/local/bin/port install povray
/opt/local/bin/povray -version
```

This is the [official MacPorts installation command](https://ports.macports.org/port/povray/).
MacPorts installs the required dependencies. If it reports an outdated ports
index/base, run `sudo /opt/local/bin/port selfupdate`, then retry the install.
A broad upgrade of all installed ports is not part of this checklist. If the
build fails, preserve the error and log path and diagnose that failure before
changing package managers. The existing Xcode version command alone does not
prove every build prerequisite is present.

If the absolute executable path works but `command -v povray` fails, use
`export PATH="/opt/local/bin:/opt/local/sbin:$PATH"` in that Terminal. Check
`povray`, `ffmpeg`, and `ffprobe` with `command -v` after activating Conda too,
since activation can change command selection.

### 2. Activate the installed Python environment

From the repository root:

```bash
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate navier-stokes-vortex-b1
python --version
python -c 'import sys, platform, numpy; print(sys.executable); print(platform.machine()); print("NumPy", numpy.__version__)'
conda list --show-channel-urls fenics-ffcx
command -v povray
command -v ffmpeg
command -v ffprobe
```

Prefer Python 3.12 on both machines (R069); the existing FEM pin is 3.12.13.
Use this Python consistently for the checks. This avoids accidentally using
the older `/opt/local/bin/python3` environment. Use native arm64 on this Mac;
do not solve the environment for Intel/Rosetta or copy Linux binaries/JIT caches.
No second Conda distribution, Docker, GPU toolkit, or extra Python dependency
is identified as required by the current pipeline.

R046 already ran the FEM imports and two-rank MPI check. Repeat those only if
the environment changes, and record the executable, package build/channel,
PETSc real scalar type and MPI library. A sandbox `Operation not permitted`
from MPI networking requires a permitted execution context; it does not alone
justify reinstalling MPI.

### 3. Validate the movie pipeline in a fresh source copy

Do this after installing POV-Ray. The generator removes existing
`positions/frame*.inc`; the renderer overwrites matching PNGs; the encoder
includes **all** matching PNGs and overwrites its MP4. A fresh source copy
prevents old frames from changing the test or existing output from being lost.
Use the committed revision intended for the check; `git archive HEAD` omits
uncommitted edits. Keep the same Terminal open for the following blocks, and
stop if a command fails.

```bash
repo_dir="$(git rev-parse --show-toplevel)"
git -C "$repo_dir" status --short
git -C "$repo_dir" rev-parse HEAD
smoke_dir="$(mktemp -d "${TMPDIR:-/tmp}/vortex-mac-smoke.XXXXXX")"
git -C "$repo_dir" archive HEAD | tar -x -C "$smoke_dir"
cd "$smoke_dir"
mkdir -p preview frames movie
python make_trajectories.py --frames 10 --fps 30 --beads 500 --substeps 8 --seed 20260919
povray fluid.pov +W1280 +H720 +KFI1 +KFF10 +SF1 +EF1 +KI0 +KF1 +FN -D -V +A0.2 -J +Opreview/frame
```

Inspect the one image under `preview/` before proceeding. These direct
POV-Ray options match `render.sh`'s scene, resolution, animation and antialiasing
settings, with `-D` added for a headless run. They avoid an unexpected GUI
preview. Leave the standard POV-Ray include-file installation accessible.

```bash
povray fluid.pov +W1280 +H720 +KFI1 +KFF10 +KI0 +KF1 +FN -D -V +A0.2 -J +Oframes/frame
FPS=30 bash make_movie.sh
ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,nb_frames,nb_read_frames \
  -show_entries format=duration -of json movie/navier-stokes-vortex-lab.mp4
```

For the agent performing this check:

- Confirm exactly ten trajectory includes and ten PNGs; verify each include
  declares 500 finite coordinates. Inspect first/middle/last files and images
  (frames 1, 5, 10) and confirm numerical and visible tracer motion.
- Check the nondimensional bounds in `Config`: radius at most 0.92 and
  `abs(z)` at most 0.98, allowing the documented include serialization rounding
  (for this check, absolute tolerance `1e-9`). Report extrema over all frames.
  The generator's final-state check alone does not inspect every saved frame.
- Expect H.264, `yuv420p`, 1280x720, 30 fps and ten decoded frames. Duration is
  approximately `10/30 = 0.333333` seconds, allowing container timestamp
  rounding. If `nb_frames` is missing, use `nb_read_frames` from `-count_frames`.
- Save the command transcript, versions, counts and inspection outcome before
  leaving the temporary directory; copy small evidence to the new request's
  evidence directory. Large includes/PNGs/MP4 stay outside tracked source.
  Return with `cd "$repo_dir"`; record `smoke_dir` if keeping the outputs.

Passing this check establishes the illustrative movie pipeline. FEM assembly,
solving, resource monitoring and cross-machine numerical equivalence remain
separate checks. The kinematic tracer movie is not a physical-flow validation.

## Agent protocol for Mac-versus-PC benchmarks

The authoritative comparison protocol is now
[MAC_PC_PERFORMANCE_MEMORY_PLAN.md](MAC_PC_PERFORMANCE_MEMORY_PLAN.md).
This heading is retained for existing links. The new plan specifies both
machines equally, includes explicit benign memory/monitor checks, and keeps
R067's numerical reference screens and all previous attempt allowances intact.
It supersedes this page's earlier benchmark sequence and monitoring suggestions.

In particular, a process ancestry scan alone does not establish complete
containment or cleanup, and the R076 fixture pass does not validate actual
platform adapters. Follow the review/implementation/live-validation gates
before timing work. Source/cache/ignored-input transfer, sampling semantics,
headroom and repetition accounting are specified in the new plan.

## Completion and model handoff

The future Mac movie-readiness check completes when counts, all-frame finite
coordinates/bounds, separated image inspections and decoded MP4 metadata pass.
Stop on failure or after recording that result. Its completion establishes
the kinematic movie pipeline only.

Use the [current handoff](../../SESSION_HANDOFF.md#next-task) for the next task,
model/effort, completion criteria and stops. The test plan is written; it has
not launched another session, switched models or established a host winner.
