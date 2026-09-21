# Current session handoff

Last updated: 2026-09-20. Latest request:
[R057](REQUEST_LOG.md#r057--2026-09-20--record-mac-installation-and-benchmark-plan-integrate-stash-publish),
which added a Mac installation and Mac/PC benchmark guide at
[MAC_INSTALL_AND_BENCHMARK_PLAN.md](docs/realizability/MAC_INSTALL_AND_BENCHMARK_PLAN.md).
The only confirmed missing software is POV-Ray; the installed Conda/MPI stack
and ffmpeg/ffprobe have already passed their recorded checks. The autostash's
earlier Mac inventory notes are reconciled with the later R046–R056 records and
are being removed after that reconciliation is included in the publication.
No software install or benchmark was run. R056 confirmed the PC already has
the pinned conda-forge FFCx 0.10.1 build; no upgrade or historical rerun is
needed. The R014/R016/R020 version fields report the module's embedded 0.10.0
string, though their commands used the 0.10.1 package. Astra's planned review
should check whether the project's forms hit the fixed
multiple-integral/same-quadrature-rule case and confirm future reference runs
use a fresh isolated FFCx cache. R055 traced the 0.10.1 distribution / 0.10.0
module version difference to upstream metadata. The release is a critical bug
fix; retain the project pin. The exact installed Mac build/channel has not been
independently checked from this PC. R054 found the Mac FEM Conda
environment and ffmpeg/ffprobe available, with POV-Ray still missing from the
checked shell. R053's Mac/PC comparison remains in place; the FEM environment
has not run an assembly or solve. The
user permits using the PC
within its capabilities; the former small diagnostic caps are not immutable
user requirements. R023–R032 did not invoke Continue or authorize publication
at the time; their resource and machine continuity is included here where
needed for R033's work. R033 authorizes commit/push of its scoped result. The
last physical checkpoint remains R020; R033 prerequisites passed
without a physical run. R034 also ran no numerical work. The last previously committed checkpoint is
`b15a562`.

R033's scoped result was committed as `85ebd85` and pushed successfully to
`origin/main` on branch `main`. The request log records the delivery outcome.
R034's scoped files are in commit `da46593`; the SSH recovery/history update is
in `b15a562`. Both are pushed to `origin/main`, and `origin` now uses the
sibling repositories' SSH URL. The key itself was neither replaced nor
regenerated.

## User goals

Read [STATUS.md](STATUS.md), including its new overall milestone table. The
user wants to learn whether exterior sensors and actuators can provide an
adequate initial setup for some orders of magnitude of the process, and provide
data for a separate, clear, approximately realistic 3D movie. Initial
preparation and continued driving are distinct. The quantity/range meant by
“orders of magnitude,” preparation tolerances, permitted continued actuation
and adequate sensing remain open. The illustrative movie pipeline is usable;
no physical preparation, attained contraction range or validated movie flow
history is established. We are still verifying numerical boundary responses.

## Reusable continuation request

In a session opened in this repository, say:

> Continue

The [short continuation request in AGENTS.md](AGENTS.md#short-continuation-request)
defines the workflow: log the request, complete the bounded task and checks,
update continuity, commit/push scoped work, and stop. Explicit qualifications
such as “Continue without pushing” override that default. It does not switch
the selected model or schedule another session. No scheduler is installed.

## Latest result: R022 toy memory stop

Read the [R022 result and next contract](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_RESULT.md),
[evidence index](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_EVIDENCE.md),
[derived result](docs/realizability/evidence/r022/result.json),
[validation](docs/realizability/evidence/r022/validation.json), and exact
[advanced toy source](docs/realizability/evidence/r022/advanced_toys.py),
[observer](docs/realizability/evidence/r022/presolve.py),
[physical runner](docs/realizability/evidence/r022/physical.py) and
[parent](docs/realizability/evidence/r022/run_contract.py).
Then read the [R021 contract](docs/realizability/B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md),
[R020 physical stop](docs/realizability/B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md),
[R013 original contract](docs/realizability/B2_MATCHED_TRACE_REVIEW.md) and
R016–R019 results linked there. Required research documents remain
`PROJECT_TRACKS.md`, `EXPERIMENT.md`, `PHYSICAL_REALIZABILITY_PLAN.md` and
`CONTROL_RESEARCH_ROADMAP.md`.

R022 preserved all 19 production identities and 440 historical files and
reaudited R021 with writes redirected. The disposable runner implements fixed
q=64/q=96 and a once-only pre-solve observer, checking P and both A candidates
on copies before allowing factorization. Accepted A vectors are retained.
The actual observer path remains unvalidated: its toy cases were not reached.

The first toy attempt exposed a NumPy-Boolean JSON-reporting defect, fixed by
converting `accepted` to built-in bool. Its exact code/reports and 5.239195592 s
are preserved. The second attempt passed wrong-root refusal, all five original
phases, actual parent refusal and 16 high-order polynomial facet checks.
It then hit the 512 MiB child-tree cap at 513.60546875 MiB, before the first
observer case. Cumulative toy time was 16.405468375 s; maximum sample gap was
0.058599793 s. There was no numerical retry after this resource stop.

The final advanced child record is a partial last checkpoint, with all four
trace/order cases and no observer cases. Its 180.66015625 MiB process high-water
value is not the final peak. The parent saw up to four processes. Source order
and a generated C cache artifact suggest compilation contributed, but no
per-process RSS or intervening stage checkpoint identifies the exact cause.
No physical child, factorization, PDE solve or physical trace evaluation ran.

## R033 prerequisite and observer completion

Read the [R033 follow-up result](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_FOLLOWUP.md),
[saved-data validation](docs/realizability/evidence/r033/validation.json),
[resource readings](docs/realizability/evidence/r033/resources.json), and
[cache accounting](docs/realizability/evidence/r033/cache_metadata.json).
The complete prerequisite suite passed in attempt 4 after four preserved
attempts and 56.251 seconds cumulative. All five original phases, wrong-root
and actual parent refusal, watchdogs, 16 high-order facet checks and all four
observer cases passed. The nine full block-oracle comparisons passed; the
observer ran once per case with zero factor/solve events. The maximum sampled
child-tree RSS across attempts was 571.42 MiB, under the capacity-sized 1536 MiB
cap; the final cache-reuse pass peaked at 171.24 MiB. One attempt exposed a
stale global FFCx cache artifact; another exposed a writable PETSc array access
in the toy. Both fixes were confined to the disposable harness. No global cache
or production source changed, and no physical child, mesh, factorization or PDE
solve ran. The B2 physical accuracy gate remains failed.

The Mac reassessment trigger from R031 has now been reached. The PC completed
this prerequisite comfortably within the selected cap. That does not size the
next physical calculation. The Mac's processor, OS, available RAM and exact
environment compatibility remain unknown, so there is not yet evidence to
recommend transferring the current work. Explicitly compare both machines
against the estimated physical workload before any physical launch; report the
choice then.

## Preserved physical limits

R020 remains the latest physical attempt: one mesh, P solve/correction and
checked outputs, then A_32 compatibility refusal before its solve. Its required
removal was 11.0906 times the unchanged arithmetic limit. The saved q64 flux
is motivation, not acceptance of an assembled candidate. R012 remains the
last complete physical response audit. R020's P gain is
`-1.6734724052233703 - 1.0983702805959774 i 1/m`, amplitude ratio 28,963.4968
and phase error 74.1175 degrees. Its arithmetic/output checks pass; reference
accuracy fails. No physical solution coefficient vector was saved.

Paired comparison, continuum geometry/spatial-error allocation and total FEM
error floor remain unknown. Alpha=48 remains inconclusive; certificates are
not integrated into schema-3 gate reports. The physical B2 gate stays failed
and `campaign_ready=false`. Force/power, pressure demand, hardware feasibility,
preparation, sensing and validated movie flow remain unassessed or unresolved.

## R023 resource clarification

Read [STATUS.md](STATUS.md#what-the-resource-budgets-mean) and the
[resource snapshot](docs/realizability/evidence/r023/resources.json). WSL sees
7.614 GiB RAM and 28 logical CPUs; 6.321 GiB was available when inspected.
This is not a measurement of total Windows-host RAM. Recheck capacity at launch.
The prior caps were local watchdog settings, not monetary or hardware limits.
Cumulative wall time covers all prerequisite phases and attempts within one
bounded task, including imports/compilation/reporting, but not analysis or
editing between launches. Memory is the sampled sum of resident memory of
active test descendants, not accumulated allocations over successive tests.

R023 supersedes the old prohibitions on increasing those conservative caps.
Use **600 seconds cumulative / 2048 MiB active child-tree RSS** for the next
prerequisite task, provided at least **4096 MiB RAM is available inside WSL at
launch**, and Windows also has adequate headroom for the workload (see R024
below). The guest check alone is insufficient. This leaves approximately
2 GiB of WSL headroom. If capacity differs, size the
job accordingly and record the chosen allowance before execution; do not
count swap as extra RAM. Keep runtime/memory watchdogs and stage reports.
Choose any later physical-run allowance from its expected workload and current
capacity when that separately scoped task is reached. A cap adjustment never
changes a scientific acceptance threshold or retroactively validates old data.

## R024 Windows and WSL memory

The [host/guest snapshot](docs/realizability/evidence/r024/resources.json)
records 15.725 GiB usable Windows RAM and 2.148 GiB available physical RAM;
WSL separately reported about 7.6 GiB total and 6.8 GiB available. These are
different views of shared physical resources, not two amounts of free RAM
that can be added. R023 measured only the guest. Check both host and guest
headroom before launching heavier work, and monitor host pressure during it.

Closing unused Chrome tabs/apps is a reasonable way to make room before the
next test; the user reported Chrome using 2.7 GB. No custom configuration file
was found at `C:\Users\rharr\.wslconfig`. The observed WSL capacity is consistent
with Microsoft's default of half the host RAM. Keep the current WSL limit for
the planned 2 GiB test; increasing it would not increase physical RAM. No app
was closed, WSL restarted, or host setting changed. The next scientific task
and all acceptance thresholds remain unchanged.

R025: the user confirms WSL Settings displays **8 GB memory and 2 GB swap**.
These are user-reported settings, consistent with the earlier guest readings.
Retain them for the planned test; swap is disk-backed overflow, not extra RAM.
Chrome Task Manager can identify individual tasks using memory (Shift+Esc on
Windows, or More tools > Task Manager). Advice only; no apps/settings changed.

R026: the user reports six YouTube tabs at about 0.2 GB each (roughly 1.2 GB
combined). Suggested bookmarking/closing unused tabs or enabling Chrome Memory
Saver; active playback can prevent automatic deactivation. No tabs were closed
or settings changed, and no resulting memory recovery was measured.

R027: Chrome Memory Saver was already on Balanced. The user is considering
Maximum; no switch is confirmed. Maximum deactivates eligible unused tabs
sooner, with reloading on return; active playback can still prevent this.
Suggested pausing unused videos and trying Maximum, then checking Windows
available memory. No new memory measurement or setting change was performed.

R028: the user highlights Maximum's "shorter period of time" versus Balanced's
"optimal period of time." Google's cited page supplies no exact timeout.
This describes earlier deactivation of eligible unused tabs, with the same
playback caveat; no setting change or memory recovery has been confirmed.

R029 supersedes the unconfirmed setting in R027/R028: the user switched Chrome
Memory Saver to Maximum and reports 2.6 GB Chrome memory after about one minute.
This is user-reported; no fresh host reading or causal effect was established.
Suggested pausing unused videos, leaving those tabs inactive for several more
minutes, then checking Windows available memory. No exact timeout is promised.

## R031 Mac decision checkpoint

The user has a Mac with **24 GB memory** and asks to be told when transferring
work would be worthwhile. Its chip, available memory, OS and installed tools
have not been inspected. Keep the next 2 GiB prerequisite task on the existing
PC setup if fresh host/guest capacity checks permit it. More installed memory
does not establish faster execution or adequate free memory on the Mac.

**Explicitly revisit and report the machine choice after prerequisite coverage,
before the next physical calculation.** Flag a move sooner if actual Windows
or WSL memory pressure prevents a bounded job from running comfortably after
reasonable headroom adjustments. Also reassess before a larger mesh or batch
whose estimated peak does not fit the PC with headroom. A local watchdog stop
alone is not evidence that another machine is required. Recommend transferring
only after comparing the expected workload with actual Mac capacity and the
cost of reproducing the environment. This is a checkpoint in future project
work, not a scheduled/background reminder or authorization to migrate now.

## R034 Mac assessment

Read the [captured Mac snapshot](docs/realizability/evidence/r034/mac_snapshot.json).
On 2026-09-20, this environment reported an **iMac Mac16,3, Apple M4, 4
performance plus 6 efficiency cores, arm64, macOS 26.6.2, and 24 GiB RAM**.
`memory_pressure` reported 68% system-wide free memory and zero cumulative
swap-ins/outs since boot; `df` reported 591 GiB free on the project volume.
These are one-time machine readings, not a runtime benchmark or the project's
active-child-tree RSS measure.

The inspected `/opt/local/bin/python3` is Python 3.10.19 with NumPy 2.2.6.
`dolfinx`, `petsc4py`, `mpi4py`, and `gmsh` were not importable there, and
`mpiexec`, Conda, Micromamba, Docker and Podman were not found on PATH. The
project pins Python 3.12.13, DOLFINx 0.10.0, PETSc/PETSc4py 3.25.5, MPICH
5.0.1, mpi4py 4.1.2 and Gmsh 4.15.2 in `environment-b1.yml`. This establishes
that the inspected shell is not ready to run the pinned FEM workflow. It does
not establish that these packages are absent everywhere on the Mac.

Against R033's dated PC snapshot (Windows 15.725 GiB usable with 6.294 GiB
available; WSL 7796 MiB total with 6924 MiB available), the Mac has more
installed memory and ample project-volume storage. The readings are not
simultaneous; PC host/guest views are not additive, and no matched solver
benchmark or physical-workload peak estimate exists. **Do not transfer the
next physical run yet.** Complete the handoff's Astra/high review first. If that
review recommends a physical comparison, compare current launch-time capacity
on both machines, reproduce the pinned stack on the Mac, adapt and validate
process-tree monitoring, and run a small reference comparison under unchanged
scientific tolerances before selecting a host. Do not copy Linux binaries or
JIT caches.

R046 subsequently verified the pinned FEM package imports and two-rank MPICH
startup in the Mac Conda environment. It did not run FEM assembly/solve or a
numerical reference case. Conda metadata lists `fenics-ffcx` 0.10.1 while the
imported module reports 0.10.0; preserve and resolve this reproducibility
discrepancy during review. The original MacPorts shell's missing packages are
not evidence that the packages are absent from the entire Mac.

FEniCSx documents a [macOS installation route](https://fenicsproject.org/download/),
but this project's exact pinned environment has not been tested there.
`environment-b1.yml` pins DOLFINx/PETSc/MPI versions; the current harmonic
backend uses coupled real blocks with a real PETSc build. Preserve that choice.
The archived watchdog reads Linux `/proc`, and RSS reporting must be checked
for the destination platform. At migration, establish the Mac architecture,
recreate compatible dependencies, adapt monitoring in a new copy, and run a
small reference comparison under unchanged scientific tolerances. Preserve
the PC checkpoint and historical evidence; do not copy Linux binaries/JIT
caches as a Mac environment or silently upgrade the numerical stack.

## R039 Mac FEM installation guidance

The user wants to install the FEM stack on the M4 Mac. The project pins
Python 3.12.13, DOLFINx/Basix 0.10.0, UFL 2025.2.1, FFCx 0.10.1,
PETSc/PETSc4py 3.25.5, MPICH 5.0.1, mpi4py 4.1.2, Gmsh/python-gmsh 4.15.2,
NumPy 2.5.3 and SciPy 1.18.1 in `environment-b1.yml`. Official FEniCS
instructions recommend Conda for macOS. The verified package listings show
DOLFINx 0.11.0 on osx-arm64, while the located DOLFINx 0.10.0 binary is
osx-64/Python 3.11; native availability of the project's exact 0.10.0/Python
3.12.13 combination is not established. Do not silently substitute 0.11 or
edit the existing environment.

Recommended safe first attempt in R039: install the Apple Silicon **Miniforge** build,
open a fresh Terminal, and verify `conda info` reports `osx-arm64`. From the
repository root, run
`conda search --override-channels -c conda-forge 'fenics-dolfinx=0.10.0'`.
If an osx-arm64 build is listed, try the unchanged
`conda env create -f environment-b1.yml`. The environment is isolated from
MacPorts Python. If the exact package or full environment solve is refused,
stop and preserve the solver message; review a separate candidate stack before
changing versions. PETSc4py 3.25.5, MPICH 5.0.1 and Gmsh 4.15.2 list arm64
builds, but that alone does not establish the whole environment solves. R041
supersedes the Miniforge installer recommendation with the user's preference
for Anaconda's official Miniconda ARM64 `.sh` installer; retain the conda-forge
channel and project pins.
POV-Ray was not found on PATH; ffmpeg/ffprobe were. No packages were installed
in R039. Continue the Astra/high physical-path review on the PC while Mac
environment compatibility remains unresolved.

## R046 Mac FEM environment check

The user created Conda environment `navier-stokes-vortex-b1` at
`/Users/rharris/miniconda3/envs/navier-stokes-vortex-b1`. Imports succeeded for
Python 3.12.13, DOLFINx 0.10.0, Basix 0.10.0, UFL 2025.2.1, PETSc/PETSc4py
3.25.5, mpi4py 4.1.2, Gmsh 4.15.2, NumPy 2.5.3 and SciPy 1.18.1. Conda lists
the pinned `fenics-ffcx` distribution as 0.10.1, while `ffcx.__version__`
reports 0.10.0; retain this as a reproducibility discrepancy for the next
review rather than changing the stack. A two-rank MPI launch succeeded with
MPICH 5.0.1. The sandbox denied MPICH access to `en1`; the same checks passed
after an approved out-of-sandbox rerun. No physical solver was run. The Mac
stack now imports and launches MPI, but no FEM assembly/solve or numerical
reference comparison was run, so migration suitability remains unestablished.
R055 traced the version-string difference to upstream v0.10.1 packaging
metadata: that tag's `pyproject.toml` still declares version 0.10.0. The release
itself contains the critical quadrature-rule fix, so the 0.10.1 Conda pin is
important and should not be downgraded. If provenance must be verified before
the FEM reference case, inspect the Mac's package build/channel with
`conda list --show-channel-urls fenics-ffcx`; no reinstallation is indicated.

## R054 Remaining Mac software

The numerical environment is installed: R046 verified Python 3.12.13,
DOLFINx/Basix 0.10.0, UFL 2025.2.1, PETSc/PETSc4py 3.25.5, MPICH 5.0.1,
mpi4py 4.1.2, Gmsh 4.15.2, NumPy 2.5.3 and SciPy 1.18.1 imports, plus a
two-rank MPI startup. The trajectory script itself uses NumPy and the Python
standard library. R034 found `ffmpeg` and `ffprobe` in the Mac shell. It did
not find POV-Ray, which `render.sh` requires; therefore the full movie tool
chain is not yet complete on the Mac.

Install POV-Ray through a package manager already on the Mac, then confirm
`povray -version`. The original Python path was `/opt/local/bin/python3`, so
check whether MacPorts `port` is available before installing another package
manager. R055 explained the FFCx report difference (`fenics-ffcx` distribution
0.10.1 versus imported `ffcx.__version__` 0.10.0): the upstream v0.10.1 source
tag's `pyproject.toml` still declares version 0.10.0. The release backports a
critical fix for multiple integrals sharing one quadrature rule. Retain the
0.10.1 project pin; optionally confirm the live Mac build/channel with
`conda list --show-channel-urls fenics-ffcx`. This metadata mismatch does not
currently block the separate FEM reference comparison and is no reason to
reinstall.
Once POV-Ray is available, run a small render/encode smoke test before
considering the Mac movie pipeline ready. No FEM assembly/solve is required to
finish this software checklist. Recommend Luna/medium for those mechanical
steps; return to Astra/high for any scientific stack or tolerance decision.

## R047 Mac versus PC decision measurements

The existing evidence does not establish which machine is faster or better
suited to the next FEM task: the Mac has a recorded M4/24 GiB snapshot and its
environment now imports/starts two-rank MPI; PC host/WSL memory readings are
older and there is no matched benchmark. During the next scientific review,
estimate the intended workload's mesh/order, solver and memory needs. Before a
separately authorized reference run, refresh host/guest capacity on both
machines and run the same small, non-campaign FEM reference workload with the
same versions, inputs and MPI ranks. Compare wall time, peak process-tree RSS,
residual/convergence behavior and output agreement under existing tolerances;
retain memory headroom and watchdogs. Generic CPU tests or RAM capacity alone
are insufficient. No FEM benchmark or solver was launched for R047. The
handoff's GPT-6 Astra/high review remains the next task and must stop before
physical execution; it should include workload sizing and the R056 targeted
audit of same-quadrature multi-integral forms and cache provenance. The current
PC environment is already at the pinned FFCx 0.10.1 package build. Keep the
module string `0.10.0` as a runtime self-report in the historical records; no
recorded R014/R016/R020 calculation needs rerunning for this discrepancy.

## R056 PC FFCx verification and result impact

The PC environment `/tmp/navier-fenicsx` already has conda-forge
`fenics-ffcx 0.10.1 pyhbc3ee6d_1`, the exact package version pinned by
`environment-b1.yml`. Conda history shows it was installed on 2026-09-19,
before R014/R016/R020 on 2026-09-20; their command records use this environment's
`/tmp/navier-fenicsx/bin/python`. The package's embedded metadata and
`ffcx.__version__` both report 0.10.0 because the upstream v0.10.1 tag's
`pyproject.toml` retains that project version. The archived PC package URL and
hash are in [R056 environment evidence](docs/realizability/evidence/r056/ffcx_pc_environment.json).

Therefore no PC upgrade or numerical rerun was needed. The R014/R016/R020
JSON fields remain accurate as module self-reports but should not be read as
the Conda artifact version. R033's incomplete global-cache C file was detected
before compilation; later attempts used the new isolated cache. It is not
evidence that R033 ran the unfixed package or that a numerical result changed.
The Mac's Conda build/channel remains unverified from this PC.

For the planned Astra/high review, inspect whether project UFL forms contain
multiple integrals with the same quadrature rule, the v0.10.1 fix trigger, and
whether any relied-upon compiled artifact could predate the patched build.
Keep the current pin. The next FEM reference run should use a fresh isolated
FFCx cache and record Conda build/hash separately from `ffcx.__version__`.
Stop the review before physical execution.

## R055 FFCx version discrepancy

The environment pins the Conda distribution `fenics-ffcx=0.10.1`, while the
Mac reported `ffcx.__version__ == 0.10.0`. This is explained by upstream
release metadata: the v0.10.1 tag's `pyproject.toml` still declares version
0.10.0. The v0.10.1 release backports PR #797, fixing a critical code-generation
bug when a form contains multiple integrals with the same quadrature rule. Keep
the 0.10.1 pin. The Mac's imports and two-rank MPI startup passed, but the exact
installed Conda build/channel has not been independently confirmed from the
PC; if provenance is needed, run `conda list --show-channel-urls fenics-ffcx`
there. No reinstall, pin edit, assembly or solve is warranted by this
version-string mismatch alone.

The next task remains the Astra/high review of R021/R013 on the PC, stopping
before physical execution. FFCx provenance can be checked before a matched FEM
reference run if needed; retain Astra/high if package identity or numerical
behavior remains unclear.

## R057 Mac software completion and host benchmarks

Use [the Mac installation and benchmark plan](docs/realizability/MAC_INSTALL_AND_BENCHMARK_PLAN.md)
to finish the remaining software check. R046 already passed Conda imports and
two-rank MPI on the Mac; R034 found `ffmpeg`/`ffprobe`; POV-Ray is the only
confirmed missing executable. Check which package manager is already present,
install POV-Ray through that manager, then run the ten-frame trajectory/render/
encode smoke test and inspect separated frames plus `ffprobe` metadata. Record
the Mac FFCx Conda build/channel separately from its Python module string.

The user wants evidence to choose between the Mac and PC per task. The next
scientific action remains the GPT-6 Astra/high R021/R013 method review on the
PC, including the FFCx form/cache audit, and must stop before physical
execution. Astra should define and approve a small non-campaign FEM reference
workload and acceptance/headroom thresholds before any FEM comparison. Then
refresh near-simultaneous capacity snapshots, run identical trajectory/render/
encode tasks and the approved FEM reference on both hosts, measure median wall
time/range and peak process-tree RSS, and check deterministic/numerical outputs
against unchanged tolerances. Separate cold JIT compilation from warm cache
timing with isolated task-local caches; never change shared caches or add the
Windows and WSL memory readings together. No benchmark was launched in R057.

The autostash's R034–R037 request additions duplicate/restate the current
R049–R052 history; its old inventory-pending handoff/status is superseded by
R046 and later host/software records. The Mac inventory prompt remains in the
repository. The crosswalk and removal are recorded in R057; no unique source,
evidence, or prompt file was lost. R057 was published as commit `63d6891` to
`origin/main`; the stash list is empty.

## R053 Machine task allocation checkpoint

The pull advanced `main` from `4a55bdf` to `8c27290`; the reconciled records and
Mac prompt were committed and pushed as `6cc842f`. A fresh PC snapshot at
2026-09-21T01:56:57Z showed Windows with 15.72 GiB total and 5.44 GiB free;
WSL showed 7.61 GiB total and 6.73 GiB available, with 28 logical CPUs. The
Windows and WSL readings are two views of shared RAM, not additive. The Mac's
24 GiB and 68% free-memory reading come from a separate 2026-09-20 snapshot, so
they are not contemporaneous or directly comparable. The full records are in
[R053 machine evidence](docs/realizability/evidence/r053/machine_snapshot.json).

For the immediate R021/R013 observer and physical-runner review, use the PC:
the disposable Linux path, guard checks and resource monitoring were actually
exercised there. The Mac is a promising future FEM candidate: its pinned
packages import and two-rank MPI starts, and it has more installed RAM. It has
not passed FEM assembly, a solve, process-tree monitoring or same-input output
checks; its exact FFCx Conda build/channel has not been independently confirmed,
although R055 explains the module version string from upstream metadata. Neither machine has a
matched timing/RSS benchmark for the physical workload.

For the eventual FEM host choice, estimate the reviewed workload, refresh both
machines' capacity near the same time, then compare an identical small
non-campaign case by wall time, peak process-tree RSS and output agreement
under unchanged tolerances. No such run was part of R053. For rendering, the
Mac snapshot found `ffmpeg`/`ffprobe` but not POV-Ray; current PC tool
availability was not measured here, so no render-host preference is supported.
The Mac has 4 performance and 6 efficiency CPU cores; the PC CPU model was not
captured, and WSL's 28 visible logical CPUs do not provide a matched CPU
performance measure. Use either machine for ordinary editing according to
convenience; that does not answer compute performance. The short Mac inventory
prompt is at
[MAC_INVENTORY_PROMPT.md](docs/realizability/MAC_INVENTORY_PROMPT.md); no
additional Mac run is needed before returning to the PC for the Astra/high
review. Stop that review before physical execution.

R041 clarifies the user's preference for software published by Anaconda Inc.
Recommend the official Miniconda Apple Silicon `.sh` installer, not Miniforge.
Anaconda currently lists macOS 12.1+ for Miniconda on Apple Silicon, compatible
with the recorded macOS 26.6.2. Use Miniconda as the conda manager but retain
the project's `conda-forge` source and exact environment pins. No software was
installed; native arm64 availability of the exact DOLFINx 0.10.0/Python 3.12.13
combination remains unresolved.

## Next task

Review the now-exercised disposable observer and remaining physical runner
against the unchanged R021/R013 contract before deciding whether to conduct a
separately scoped matched-trace physical comparison. Recommend **GPT-6 Astra
with high reasoning** for this scientific review. Recheck model availability
when handing off. R030 rechecked the official model pages:
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) and
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).
The review should check the saved P/A/A compatibility logic, the independent
full-block lifting oracle, refusal preservation and no-factorization sentinel;
then inspect physical launch gates, report counts, resource checks and output
validation against the R021 fixed q=64/q=96 experiment and R013 thresholds.
It should state assumptions, alternatives, unresolved numerical risks and
whether a separate physical experiment is warranted. Also compare the Mac and
PC against the estimated physical workload; do not recommend migration from
installed RAM alone.

Completion is a documented review and a separate decision boundary. Stop before
physical execution, solver changes, new meshes/orders, pressure/return-flow
repair, gate integration, campaign, B3, rendering or encoding. If the review
finds only a clearly understood mechanical defect, recommend GPT-5.6 Luna with
medium reasoning for a narrow repair. Retain GPT-6 Astra/high for unexplained
results or any scientific/numerical-method decision. No model switch or
automation occurred. **Next prompt: Continue.**

## R035 Git publication setup

Sibling repositories `beads`, `beads2`, `hsv_tools`, `madweave` and `sound`
configure `origin` as `git@github.com:...` SSH remotes. Two read-only sibling
`ls-remote` checks failed with `Permission denied (publickey)` in this session,
so matching their remote format alone will not authenticate. This repository
currently uses HTTPS. This Mac already has `~/.ssh/id_ed25519` and its public
key. Initial default SSH attempts failed because the agent had no identities
and no `github.com` host entry was found in `~/.ssh/config`. A later explicit
read-only test with `-i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes` succeeded and
GitHub greeted `rharriszzz`; this confirms the key is valid and registered.
The identity was added to the current agent by that test, but no persistent
Keychain, credential or remote setting was changed. The GitHub settings
fingerprint supplied in R037 exactly matched the diagnostic fingerprint.

Recommended persistent setup: run
`ssh-add --apple-use-keychain ~/.ssh/id_ed25519` in Mac Terminal, and add a
`Host github.com` entry in `~/.ssh/config` with `UseKeychain yes`,
`AddKeysToAgent yes`, and `IdentityFile ~/.ssh/id_ed25519`. The public key is
already registered, so do not create or replace keys. Confirm with
`ssh -T git@github.com`. Then change this repo's `origin` to
`git@github.com:rharriszzz/navier-stokes-vortex-lab.git` and push `main`.
R034's commit `da46593` remains one commit ahead of upstream; continuity edits
from the interrupted R035 staging attempt are unstaged and must be reviewed
before any follow-up commit. No GitHub CLI is installed. Do not install another
Git client solely for this issue.

**R037 resolution:** The supplied settings fingerprint matched exactly. The
explicit-key SSH test authenticated successfully, `origin` was changed to SSH,
and commits `da46593` and `b15a562` were pushed to `origin/main`. The push used
no force option. The remaining R035 notes above describe the diagnosis and
recommended persistent Keychain setup; the remote switch and publication are
complete.
