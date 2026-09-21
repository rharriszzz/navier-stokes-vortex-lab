# Finish Mac setup and compare it with the PC

Updated 2026-09-20 after R057. This is a software-readiness and machine-choice
checklist. It does not authorize a physical/campaign calculation or change any
scientific threshold.

## Mac installation checklist

The Mac is an Apple M4 iMac with 24 GiB RAM. R046 already verified the project
Conda environment's Python 3.12.13, DOLFINx/Basix 0.10.0, UFL 2025.2.1,
PETSc/PETSc4py 3.25.5, MPICH 5.0.1, mpi4py 4.1.2, Gmsh 4.15.2, NumPy 2.5.3
and SciPy 1.18.1 imports, plus a two-rank MPI startup. R034 found `ffmpeg` and
`ffprobe`. The only confirmed missing command-line tool for the visualization
pipeline is POV-Ray. The exact Mac FFCx Conda build/channel and POV-Ray package
manager are not yet recorded.

1. In a fresh Mac Terminal, check which package manager is already installed:

   ```bash
   command -v port || true
   command -v brew || true
   ```

   Use the manager already present; do not install a second manager only for
   POV-Ray. Homebrew currently documents `brew install povray` and an Apple
   Silicon bottle. MacPorts documents `sudo port install povray` (its port is
   the Unix command-line ray tracer). See the [Homebrew formula](https://formulae.brew.sh/formula/povray)
   and [MacPorts port](https://ports.macports.org/port/povray/). If neither
   manager is present, choose one before installing it and keep the choice
   separate from the project's Conda environment.

2. Verify the executable tools:

   ```bash
   povray -version
   ffmpeg -version
   ffprobe -version
   python3 -c 'import numpy; print("NumPy", numpy.__version__)'
   ```

3. Verify the FEM environment and capture the real package build separately
   from Python's version string:

   ```bash
   conda activate navier-stokes-vortex-b1
   conda list --show-channel-urls fenics-ffcx
   python -c 'import dolfinx, basix, ufl, ffcx, petsc4py, mpi4py, gmsh; print("DOLFINx",dolfinx.__version__,"Basix",basix.__version__,"UFL",ufl.__version__,"FFCx module",ffcx.__version__)'
   mpiexec -n 2 python -c 'from mpi4py import MPI; print(MPI.Get_library_version().splitlines()[0], "ranks", MPI.COMM_WORLD.size)'
   ```

   Keep the `fenics-ffcx=0.10.1` Conda pin. The v0.10.1 source tag still
   reports project/module version 0.10.0; this is known upstream metadata, not
   a reason to downgrade or reinstall. Save the Conda build and channel with
   future run provenance.

4. Smoke-test the complete movie path at low cost. From the repository root,
   generate ten frames, render ten preview frames, and encode them:

   ```bash
   python3 make_trajectories.py --frames 10
   NFRAMES=10 ./render.sh
   ./make_movie.sh
   ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_frames -show_entries format=duration -of default=noprint_wrappers=1 movie/navier-stokes-vortex-lab.mp4
   ```

   Inspect the first, middle, and last PNG for successful rendering and visible
   tracer motion. Confirm the MP4 is H.264, `yuv420p`, 1280x720, 30 fps, and
   contains ten frames. Generated `positions/`, `frames/`, and `movie/` remain
   untracked. Once this smoke test passes, the documented Mac software stack is
   ready for the project's currently implemented visualization and B1/B2
   verification tasks; it is not evidence of physical-model validity.

## Mac-versus-PC benchmark plan

The current evidence supports the PC for the immediate Astra/high review
because the disposable Linux runner and resource checks were exercised there.
The Mac is a plausible memory-sensitive candidate, but there is no matched
timing or FEM reference result yet. The Mac's 24 GiB and PC's 28 WSL-visible
logical CPUs do not establish which is faster. Windows and WSL memory readings
are two views of shared PC RAM and must not be added together.

### Before running benchmarks

1. Finish the Astra/high review of the R021/R013 numerical contract and the
   FFCx same-quadrature multi-integral/cache question on the PC. Stop before
   physical execution. Astra should select the small non-campaign FEM reference
   case, its acceptance checks, and an operational memory-headroom threshold
   before any FEM comparison.
2. Refresh capacity snapshots on both machines close together in time. Record
   machine/CPU, architecture, OS, available RAM, swap, free disk, power mode,
   and significant background load. On the PC, record Windows host and WSL
   guest separately; do not sum them. On the Mac, capture `memory_pressure` and
   available memory at the same time as the run.
3. Put identical source revisions and input files on local storage on each
   machine. Record the Git commit, input/mesh hashes, exact command, Python and
   package builds/channels, MPI implementation/rank count, thread limits,
   compiler/runtime versions, and all numerical tolerances. Use matching
   versions and settings as closely as each architecture permits.
4. Keep the initial comparison small and non-campaign. Use one unmeasured
   warm-up and three measured repetitions per case; report each result, median,
   and range. Separate one-time setup/JIT compilation from steady-state timing.
   For a cold-codegen measurement, use a new task-local FFCx cache; for warm
   timing, explicitly reuse only that task-local cache. Never delete or modify a
   shared/global cache to prepare a benchmark.

### Compare by project task

| Task | Matched workload | Compare |
|---|---|---|
| Trajectory generation | Same commit, seed, bead count, frame count and options to `make_trajectories.py` | Wall time; output file count and finite-coordinate/bounds checks; compare generated numerical data, not just speed |
| POV-Ray rendering | Same trajectory includes, scene, 1280x720 resolution, antialiasing and 10–20 preview frames | Render wall time; inspect first/middle/last images; compare pixel differences if outputs are not byte-identical |
| Movie encoding | Copy the exact same PNG frames to both machines and use the same FPS/H.264/CRF/pixel-format options | Encoding wall time; use `ffprobe` to compare codec, dimensions, frame rate, frame count, duration and pixel format |
| FEM verification | Only after Astra approves: same small non-campaign mesh/input, method, tolerances, MPI ranks and stopping criteria | Assembly and solve times separately; peak process-tree RSS; residual/convergence and output agreement under existing tolerances; confirm memory headroom |

For FEM, also record cold versus warm assembly/code-generation time separately.
Capture peak memory for the whole process tree, not only the launcher. On the
PC, include both the WSL process tree and Windows host headroom. On the Mac,
record the run's peak process memory and system memory pressure. Stop on an
existing watchdog, acceptance, or memory limit; do not make the comparison
pass by changing solver methods, tolerances, mesh, trace, or resource guards.

### How to choose

Choose a machine per task only after it completes the same workload correctly
and leaves the pre-agreed headroom. A faster render does not imply a better FEM
host, and a larger RAM figure alone is not enough. Keep the PC as the supported
host for the next scientific review. Use either computer for routine editing;
use matched timing, peak process-tree RSS, and numerical agreement to choose a
future FEM host. A failed or memory-limited run is useful evidence and must
remain in the comparison record.

No benchmark was run for R057. The first Mac action is to install/verify POV-Ray
through an existing package manager and complete the ten-frame render/encode
smoke test. The first scientific action remains the Astra/high PC review.
