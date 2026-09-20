# AGENTS.md

Instructions for AI coding/debugging agents working on `navier-stokes-vortex-lab`.

## Request recording and session continuity

For every new user request in this repository, including follow-up corrections,
append an entry to `REQUEST_LOG.md` before substantive work. Use a sequential
ID, date, the user's wording, interpreted scope, and status. Preserve previous
entries; append dated outcome/validation notes rather than rewriting the request.
Record only requests actually available in the conversation. Context blocks and
automatic continuation messages are not new user requests. Redact credentials
or other secrets and label the redaction; do not copy private session files.

At session start, read `SESSION_HANDOFF.md` and the latest request entries.
Follow its current task and read the linked research documents before acting.
A new user request takes precedence over a stale handoff. Keep a bounded plan,
completion criteria, and explicit stopping conditions. At completion, record
changed files, checks and skips, evidence paths, unresolved decisions, and the
next task in the log and handoff. Do not claim an unexecuted check passed.
On compaction/resume, continue the existing entry rather than duplicating it.
The request log is history; do not replay completed requests as new assignments.

When the remaining task becomes routine, recommend a concrete available model
and reasoning effort. Give it an actionable task, checks, a stop condition,
and a rule for recommending the following model/effort. Routine execution is
usually suitable for GPT-5.6 Luna with medium reasoning; numerical-method or
scientific interpretation usually warrants GPT-6 Astra with high reasoning.
Recheck current availability when making the recommendation. Do not claim a
model switch occurred unless it did. A written handoff does not launch another
session or schedule an automation. See `SESSION_HANDOFF.md` for the reusable
continuation request and current recommendation.

Commit/push authorization must come from the user, including the short
continuation request defined below. Record its scope and honor it without
asking again; logging alone does not authorize every future push.

## Short continuation request

When the user says **Continue** as a task instruction in this repository
(ignoring capitalization and trailing punctuation), apply this full workflow.
This shorthand replaces the long prompt at the user's request, R003 in
`REQUEST_LOG.md`; it includes authorization to commit and push the scoped work.

1. Record the user's actual words in `REQUEST_LOG.md`. Check `git status`, read
   `SESSION_HANDOFF.md` and its required documents, and identify the current
   bounded task. Resume unfinished work before starting the next listed task;
   use recorded outcomes and Git history to avoid repeating completed work.
2. Carry out that task and its prescribed checks through completion. Preserve
   user work, scientific assumptions, acceptance thresholds, and recorded stop
   conditions. Fix understood implementation errors within the task's scope.
3. At completion or a research-decision boundary, record evidence, changed
   files, checks/skips, and unresolved questions. Update the request log,
   relevant Markdown, and `SESSION_HANDOFF.md` with one concrete next task,
   model/effort recommendation, completion criteria, and stopping conditions.
   Explain when the next model should recommend a different model/effort.
4. Stage only the task's changes, commit, and push to the current branch's
   configured upstream. Honor this authorization without asking the user to
   repeat it. Preserve unrelated changes and Git history; do not force-push.
   Report any actual permission, remote, or publication blocker accurately.
5. Stop at the bounded task's recorded stopping point. Report the result,
   checks, commit/push outcome, and recommended next model/effort concisely.
   Give **Continue** as the next prompt instead of another long instruction.

An explicit qualification in the user's message overrides the default workflow
(for example, “Continue without pushing”). Quoted examples and mentions of the
word in a question do not invoke it. The shorthand does not itself change the
selected model or schedule another session.

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

- Python 3.10+ compatible syntax,
- NumPy,
- standard library only where practical,
- type hints for public helper functions when they improve clarity,
- `pathlib.Path`,
- clear command-line parameters if configuration grows.

Do not introduce heavy dependencies without a concrete benefit.

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
