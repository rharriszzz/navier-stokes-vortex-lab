# Project and track rules

Read this document before trajectory, rendering, encoding, or physical-realizability work.

## Project purpose

This repository develops a reproducible visualization and later experimental-design framework for a **finite-scale analogue** of a contracting, stretching, swirling Navier–Stokes flow.

The project uses:

- Python/NumPy for tracer trajectory integration,
- POV-Ray for deterministic 3D rendering,
- ffmpeg for movie assembly.

The current code is a **kinematic model**. Do not describe it as a CFD solution, a numerical solution of the full Navier–Stokes equations, or a realization of a mathematical singularity.

## Core architecture

Keep three layers separate.

### 1. Physics / trajectory layer

`make_trajectories.py`

Responsibilities:

- define the velocity field,
- integrate passive tracer trajectories,
- calculate per-frame scalar state such as core radius and actuator phase,
- write deterministic POV-Ray include files.

The trajectory layer must not depend on POV-Ray.

### 2. Rendering layer

`fluid.pov` plus `.inc` files.

Responsibilities:

- scene geometry,
- materials,
- camera,
- lights,
- tracer rendering,
- actuator visualization,
- frame-specific state loading.

POV-Ray should render precomputed state. Do not move numerical ODE integration into POV-Ray unless there is a compelling reason.

### 3. Encoding layer

`make_movie.sh` / `make_movie.ps1`

Responsibilities:

- convert numbered PNG frames into a standards-compatible H.264 MP4,
- preserve the source frame rate,
- use `yuv420p` for broad playback compatibility.

## Design principles

1. **Deterministic output**
   - Use fixed random seeds.
   - Do not introduce nondeterministic particle initialization.

2. **Cross-platform**
   - Keep source paths relative.
   - Do not hard-code `C:\Users\...`.
   - WSL/Linux is the primary shell environment.
   - Windows PowerShell scripts should remain available.

3. **Small source repository**
   - Generated `positions/frame*.inc`, `frames/*.png`, and `movie/*.mp4` stay out of Git.

4. **Readable numerical code**
   - Prefer explicit variables and equations over clever vectorized one-liners when clarity would suffer.
   - Document physical units or clearly state when quantities are nondimensional.

5. **Scientific honesty**
   - Distinguish:
     - illustrative velocity fields,
     - incompressible constructions,
     - numerical Navier–Stokes solutions,
     - physical experiments.
   - Never silently upgrade one category into another in documentation.

6. **Render correctness before visual polish**
   - Verify frame-to-frame motion numerically and visually before increasing resolution or adding expensive effects.

## Current tracer model

Passive tracers satisfy:

```text
dx/dt = u(x,t)
```

and are integrated with RK4.

The initial mean cylindrical flow is based on:

```text
u_r = -a(t) r
u_z =  2 a(t) z
```

which is divergence-free in the untapered linear core.

Swirl and an annular `m=4` perturbation are then added.

The current wall taper and perturbation are not guaranteed to preserve exact divergence-free flow. If modifying this part, prefer a construction that is explicitly divergence-free.

## Validation requirements

When changing trajectory code:

- run `python make_trajectories.py`,
- verify the expected number of frame include files,
- inspect at least the first, middle, and last include files,
- confirm all bead coordinates are finite,
- confirm no bead leaves the intended numerical bounds,
- report maximum/minimum radius and z range when useful.

When changing POV-Ray code:

- first render one frame,
- then render a short sequence,
- inspect at least three separated frames,
- do not infer animation success from one image.

When changing movie encoding:

- verify with `ffprobe`,
- confirm duration,
- frame rate,
- frame count,
- resolution,
- codec,
- pixel format.

## Rendering defaults

Development:

```text
1280x720
PNG
antialiasing enabled
short frame range
```

Final render only after validation:

```text
1920x1080 or 3840x2160
PNG
full frame range
```

Avoid unusually large frame sizes until playback compatibility is confirmed.

## POV-Ray style

Prefer:

- named macros,
- small include files by responsibility,
- `#declare` for project-level parameters,
- `#local` inside macros,
- repeated objects instantiated from shared prototypes.

Avoid:

- giant monolithic `fluid.pov`,
- duplicate material definitions,
- platform-specific absolute paths,
- numerical state embedded manually in the scene file.

## Python style

Use:

- Python 3.12 as the preferred project interpreter on both PC and Mac; the
  reproducible FEM environment pins Python 3.12.13 in `environment-b1.yml`,
- NumPy,
- standard library only where practical,
- type hints for public helper functions when they improve clarity,
- `pathlib.Path`,
- clear command-line parameters if configuration grows.

Do not introduce heavy dependencies without a concrete benefit.

Check `python --version` and the executable path after activating the intended
environment. Prefer that Python 3.12 environment for trajectory generation,
validation and utility scripts too. Keep system/MacPorts interpreters intact;
do not downgrade to 3.10 because an old record mentions it. If 3.12 is unavailable
for a task, record the exception and resolve the environment before numerical
comparisons. This preference does not require rewriting working syntax or
installing FEM dependencies into a separate NumPy-only visualization environment.

## Git discipline

Before a substantial change:

```bash
git status
```

After making changes:

- show a concise summary,
- list files changed,
- run relevant tests/render checks,
- do not commit or push unless explicitly asked.

Never delete user work or rewrite Git history without explicit approval.

## Important physical improvement target

A high-value next step is to replace the current tapered field with one whose divergence is analytically controlled.

Possible approaches include:

- vector-potential construction,
- streamfunction formulation for the meridional flow,
- divergence-free Fourier perturbation modes.

Any such change should be accompanied by a numerical divergence diagnostic.

## What to optimize for

In order:

1. correctness of file pipeline,
2. deterministic reproducibility,
3. scientific clarity,
4. visible and understandable tracer motion,
5. rendering quality,
6. rendering speed.

Do not sacrifice the first three for prettier output.

## Physical-realizability research track

The repository also contains a second track concerned with boundary-controlled
physical realizability. Before substantial work on that track, read:

- `PROJECT_TRACKS.md`
- `EXPERIMENT.md`
- `PHYSICAL_REALIZABILITY_PLAN.md`
- `CONTROL_RESEARCH_ROADMAP.md`

Do not silently make research-significant architectural choices involving CFD
solver selection, reduced-state definition, controllability/observability
interpretation, actuator physics, or boundary-condition design. State
assumptions and alternatives for review first.

For the realizability track:

- arbitrary volumetric forcing may define a reference target, but is not the
  final experimental actuation mechanism;
- every proposed actuator should map to plausible hardware;
- every feedback variable should map to a plausible sensor or estimator;
- do not give a controller exact hidden CFD state unavailable experimentally;
- report actuator amplitude, bandwidth, and other physical limits as well as
  tracking error;
- treat a negative or finite-limit result as scientifically useful.

The first control calculation should be a boundary-mode response study, not a
full closed-loop controller: excite physically interpretable normal and
tangential boundary modes, measure the reduced central-flow response, and
analyze reachability/conditioning. Perform the analogous observability study
for pressure/PIV sensing before attempting full trajectory control.
