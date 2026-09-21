# Finish Mac setup and compare it with the PC

Updated 2026-09-20 for R065's choice to continue on the PC. Inspected Mac
readiness remains from R058; the user now reports a POV-Ray build in progress.
Its completion has not been verified by this session.

## Immediate next step and sequence

**Stay on the PC for the R021/R013 and FFCx form/cache scientific review using
GPT-6 Astra/high. Stop after its documented decision, before numerical
execution.** The Mac POV-Ray build and movie checks are independent of this
review and do not block it. `Continue` on the PC selects that review.

Use the [machine handoff procedure](../../AGENTS.md#switching-between-the-mac-and-pc)
when the user later chooses to switch. The PC retains repository ownership;
the independent Mac package build can continue. Do not start a duplicate
build or assume the Mac checkout has received this local R065 priority change.

The scientific sequence is:

1. Complete the PC Astra/high R021/R013 and FFCx form/cache review. Finish with
   a documented decision and, if warranted, a repeatable FEM
   reference fixture, acceptance rules and resource contract. Stop before
   execution. The once-only physical q=64/q=96 experiment is a separate task.
2. Implement and validate the portable benchmark wrapper on each host using
   synthetic processes; freeze its source with the selected cases. Check PC
   POV-Ray/ffmpeg availability too; existing Mac readiness says nothing about
   PC visualization tools. Record monitor/version compatibility on both hosts.
3. Execute the separately scoped matched comparison in sequential host sessions
   with the same frozen workload and input artifacts. Collect both reports,
   check outputs first, then recommend a host per task. Stop on the first
   contract failure; do not run the physical experiment as a benchmark fallback.

Visualization comparisons need their own fixed contract and monitor checks and
can be explicitly scheduled independently of the FEM review. They do not need
to wait for a passing physical accuracy gate. No FEM fixture, launch allowance,
cross-host tolerance or validated Mac monitor has yet been selected by this guide.

**Deferred Mac task:** after the current POV-Ray build finishes and the user
chooses to work on the Mac, verify the build and run the isolated movie checks
below using Luna/medium. This establishes visualization readiness, not a speed
ranking. Its completion does not require repeating a completed PC review.

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
python -c 'import sys, platform, numpy; print(sys.executable); print(platform.machine()); print("NumPy", numpy.__version__)'
conda list --show-channel-urls fenics-ffcx
command -v povray
command -v ffmpeg
command -v ffprobe
```

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

The purpose is a choice **per project task**, with comparable outputs and
adequate memory headroom. Imported packages, installed RAM and core counts do
not establish relative speed. The PC's Linux path has the exercised R033
observer/watchdogs; the Mac is a candidate for future FEM work.

### 1. Separate visualization readiness from the FEM research decision

Trajectory/render/encode checks can proceed independently of the physical
research review, as described in [Project Tracks](../../PROJECT_TRACKS.md).
For FEM, first complete the [current PC scientific review](../../SESSION_HANDOFF.md#next-task)
on the PC: the [R021 contract](B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md),
[R013 limits](B2_MATCHED_TRACE_REVIEW.md), [R033 result](B2_COMPATIBLE_TRACE_PREFLIGHT_FOLLOWUP.md)
and R056 form/cache audit. Document the proposed small reference fixture,
expected numerical outputs, acceptance checks and resource allowance. That
review ends before physical execution. A subsequent scoped task may implement
and run the approved comparison; this checklist itself is not its authorization.

Do not run `B1_SETUP.md`'s general solver examples, a B2 campaign, or an archived
physical runner merely as an installation check. An archived runner may have
absolute Linux paths, fixed source identities and Linux-only monitoring.
Keep production and archived evidence intact and adapt a disposable copy.

### 2. Freeze a reproducible comparison contract

Before either machine runs, save a small manifest with:

- Same frozen workload Git revision and hashes of runner/input/scene/include/mesh
  files; exact commands, seed, output directory, case size and acceptance rules. Resolve dirty source
  changes first and put both checkouts on local storage. Use WSL's Linux
  filesystem for the PC case; record if `/mnt/c` is used because that measures
  a different I/O path. Record the workload `source_commit` separately from
  the later handoff/evidence `delivery_commit`: results may be committed between
  host sessions, but each host must archive the frozen source revision rather
  than whatever `HEAD` happens to be then. Give the comparison and each
  host/case/repetition a unique ID; track completed and refused runs to avoid
  accidental repetition on receipt. A coordinator must collect both machines'
  evidence; a Mac session cannot infer current PC load or execute there automatically.
- Full Python/NumPy/FEM versions; Conda package build, channel, subdir and artifact
  hash; compiler, MPI and BLAS implementation; PETSc scalar/index type and
  solver options. Native platform binaries differ, even at matching versions.
  Save `conda list --explicit` and selected `conda-meta` records after checking
  for credentials/private channel URLs. Never archive an entire environment.
- POV-Ray version, render flags and worker count; ffmpeg version/build,
  `libx264`, preset, CRF, frame rate and thread count. Match versions where
  practical; if they differ, label the result a comparison of installed
  software stacks and do not attribute the difference solely to hardware.
- Fresh, timestamped load/capacity readings immediately before and after each
  measured run: CPU/architecture/OS, power mode, available RAM, swap changes,
  free disk and background activity. On Mac record `memory_pressure`, `vm_stat`,
  `sysctl vm.swapusage` and `df -h .`. A memory-pressure percentage is not a
  directly comparable available-GiB measure. On PC capture Windows host memory
  and WSL `MemAvailable`/swap separately. They share RAM and cannot be added.
- Explicit cumulative wall-time and sampled process-tree memory caps for the
  entire planned sequence, including warm-ups, cold compilation and retries;
  minimum host/guest headroom; allowed sample gap; and the stop conditions below.
  Choose these from the reviewed workload and fresh capacity, not installed RAM
  or an old prerequisite cap. Swap is not extra compute RAM.

Make the fixture's time/memory allowance and headroom thresholds explicit for
each host before launch, and track consumed time across sessions. Use a common
case allowance for the baseline where both hosts can safely support it. If a
host needs a different allowance, disclose that in the manifest and report it
as a capacity constraint; do not silently change the workload or relax a cap
after observing the other host's result. Capacity snapshots need to be fresh
at each launch; matched runs need not overlap in wall-clock time.

Start with one worker/thread (and one MPI rank for an approved FEM fixture):

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
```

Verify the libraries actually honor the settings. Set POV-Ray `+WT1` and ffmpeg
`-threads 1` explicitly; these environment variables do not control them.
Only test a second MPI rank if the selected fixture supports it. A later
throughput comparison can choose suitable worker counts per machine, but record
it separately from the equal-worker baseline and avoid nested thread oversubscription.
The two-rank startup result is not proof that a solver fixture supports two ranks.

### 3. Validate portable timing and resource monitoring first

Use a common wrapper timing the complete child lifetime with a monotonic clock,
including subprocesses, plus stage timing where relevant. Save return codes,
stdout/stderr and every repetition. The archived R033
[`toy_runner.py`](evidence/r033/source/toy_runner.py) traverses `/proc` and is
**not runnable unchanged as a Mac memory monitor**. Before a guarded benchmark:

1. Implement/adapt monitoring in a new disposable runner. On macOS, a process
   table from `ps` or an explicitly installed/versioned process library can
   provide PID, parent/session or process-group membership, and RSS. Follow the
   benchmark child and descendants, including MPI/JIT compiler workers and
   reparented processes; measure these on Linux too. Exclude the monitoring
   parent from the budget consistently and record its overhead separately.
2. Normalize RSS to MiB and validate units on each OS. In particular,
   `resource.getrusage(...).ru_maxrss` is bytes on macOS and KiB on Linux.
   Its per-process high-water values and `/usr/bin/time` output are supplementary;
   they do not replace simultaneous process-tree RSS sampling. Sum RSS across
   the active tree at each timestamp, then take the maximum of those sums.
   Do not sum per-process maxima from different times. RSS sums can count
   shared pages repeatedly, so also record host pressure/headroom separately.
3. First exercise a synthetic timeout and a parent/child allocating and touching
   a known memory amount, with no PDE work. Verify discovery of both processes,
   memory and timeout stops, process-group cleanup and no live descendants.
   Preserve R033's nominal 0.05-second polling and maximum-gap check of
   0.1 seconds when porting that contract. If the Mac cannot meet the sampling
   contract, record the failure and review the monitor before any FEM launch.
   Unavailable RSS is an error, not zero; retain missing-sample and peak-gap data.
4. Record per-process RSS at the sampled peak, maximum sample gap, host memory
   pressure/swap deltas and the exact reason for any stop. Monitor Windows host
   pressure as well as WSL guest capacity; a WSL-only snapshot is insufficient.

There is no validated Mac monitor shipped by this documentation task. Completing
and checking that wrapper is a prerequisite for a guarded FEM benchmark.

### 4. Use fixed workloads and check outputs before interpreting speed

Run each case in a fresh source/output directory. For rendering, distribute
one identical generated include set; for encoding, distribute one identical
PNG set. Do not compare renderings generated from different trajectories or
encode times from different images. Keep generated includes/PNGs/meshes outside
Git and transfer them explicitly, with an inventory and SHA-256 hashes verified
on receipt. Identical regeneration is acceptable only after all input hashes
match; otherwise use the preserved input artifact. Stop if a required artifact
is missing. Repository synchronization alone does not transfer ignored outputs.

| Task | Initial fixed case | Required correctness evidence |
|---|---|---|
| Trajectory generation | `python make_trajectories.py --frames 240 --fps 30 --beads 500 --substeps 8 --seed 20260919` | 240 includes; first/middle/last inspection; all finite coordinates and stated bounds; same-host repeat hashes; cross-host numeric/scalar comparison if hashes differ. |
| POV-Ray | Same 240-frame includes and scene; render frames 1–10 at 1280x720, `+A0.2 -J -D -V +WT1`, overlays unchanged | Ten PNGs; inspect frames 1, 5, 10; compare decoded pixels if hashes differ. Keep `+KFF240` so timeline/numbering matches the input case. |
| Encoding | Identical ten PNGs; software `libx264`, preset `medium`, CRF 18, 30 fps, `yuv420p`, one thread | `ffprobe` codec/dimensions/fps/count/duration; decode successfully; compare decoded content, not only MP4 hashes/container metadata. |
| FEM | Fixture selected by the scientific review; identical mesh artifact and tags, method/order/quadrature, parameters, solver, ranks and tolerances | Record mesh/DOF counts, assembly/solve/output checks, residuals, iterations, observables and reference errors. Require both the fixture's acceptance and cross-host agreement under rules fixed before execution. |

The renderer command for the fixed case, after creating empty `frames/`:

```bash
povray fluid.pov +W1280 +H720 +KFI1 +KFF240 +SF1 +EF10 +KI0 +KF1 +FN -D -V +A0.2 -J +WT1 +Oframes/frame
```

The encoder command, after creating empty `movie/`:

```bash
ffmpeg -nostdin -y -framerate 30 -pattern_type glob -i 'frames/frame*.png' \
  -c:v libx264 -preset medium -crf 18 -threads 1 -pix_fmt yuv420p \
  -movflags +faststart movie/navier-stokes-vortex-lab.mp4
```

Freeze acceptable coordinate/scalar and decoded-image differences in the case
manifest before seeing cross-host output; exact hashes are a useful first
check, not a requirement for floating-point or container byte identity. A
mismatch needs investigation before assigning a performance winner. Match FEM
fields using mesh/global identities rather than local MPI array order. Keep
same-rank comparisons separate from scaling experiments. These tests establish
portability of their fixture, not the correctness of the physical experiment.

For FEM report mesh setup, compilation, assembly, factorization, solve and
postprocessing time separately when the runner exposes them, and always retain
end-to-end wall time. A cheap smoke fixture cannot predict larger-mesh LU memory
or high-quadrature cost: relate measured cells, DOFs, nonzeros and peak memory
to the intended workload and state where scaling is unknown.

### 5. Repetitions, caches, results and stop conditions

Use one explicitly labeled warm-up and three fresh-process measured runs of
an identical case per host; retain every time, median and range. For FEM, let
the warm-up use a fresh JIT cache and record its cold timing separately; the
three measured warm runs reuse only that host's cache. A cold FEM
run uses a new empty task-local cache passed through the actual DOLFINx JIT
`cache_dir` option. A warm run reuses that host's task-local cache, with fresh
solver/output state. Changing only an environment variable is insufficient if
the harness specifies its own cache. Never copy compiled caches between hosts
or delete shared caches. Distinguish cold **JIT** from filesystem/disk cache;
a new JIT directory does not make the OS disk cache cold.

Report cold compilation/startup separately from warm execution. If a choice
depends on cold timing, pre-budget and measure three independent cold runs too.
Do not turn the handoff's once-only physical experiment into repeated runs:
Astra must select a repeatable fixture or explicitly scope repetition first.
An interrupted, inaccurate or resource-limited run remains in the record and
is excluded from a successful-run median. Do not retry automatically or enlarge
caps after a stop. Stop on a numerical/refusal failure, watchdog limit, unknown
monitoring, excessive sampling gap, or pre-agreed host/guest pressure threshold.

Save small reviewed provenance, measurements and a comparison report under
`docs/realizability/evidence/<request-id>/`; large generated data belongs in
ignored `results/realizability/` or the recorded temporary directories. Suggested
one row per repetition (use JSON null plus a reason for unavailable values):

```text
comparison_id, run_id, host, source_commit, delivery_commit, case,
versions_manifest, input_hashes, ranks, threads,
cache_state, repetition, elapsed_s, stage_times_s, sampled_tree_peak_mib,
max_sample_gap_s, host_guest_headroom, swap_delta, returncode, stop_reason,
output_validation, output_metrics
```

Report the speed ratio as `PC median seconds / Mac median seconds` (>1 favors
the Mac), together with ranges and memory headroom. If variation overwhelms
the difference, report no reliable speed winner. Choose per task after
correctness passes and memory fits. A benchmark failure does not change any
scientific acceptance threshold; a failed accuracy gate stays failed even if
both hosts reproduce it.

## Completion and model handoff

The current PC review is complete when its scientific decision, remaining risks
and any proposed repeatable reference/monitor contract are documented. Stop
before numerical execution and choose the next bounded PC task from those
findings. Retain Astra/high for numerical choices or unexplained differences;
recommend Luna/medium for a bounded monitor
implementation only after its contract is settled. Each step of the sequence
above is a separate bounded task, not one automatic multi-machine execution.

The deferred Mac check is complete when counts, coordinates, separated images
and decoded MP4 metadata pass and evidence is recorded. Stop on an install/check
failure or after that report, then follow the current handoff without replaying
completed research work.

R062 rechecked the session catalog and the official
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) and
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) effort support.
Both are available in this session; recheck availability when executing. No
model switch or background task was started. No matched benchmark has yet
established a Mac or PC performance winner.
