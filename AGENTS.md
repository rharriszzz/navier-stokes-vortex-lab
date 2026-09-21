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

At every session start, perform the read-only machine/ownership checks below
before repository writes or workload execution. For a receiving-computer handoff,
perform ownership/status checks and clean fast-forward synchronization **before**
allocating an ID or editing the log. This is the sole ordering exception to recording first and
prevents the log itself from dirtying the checkout before the pull. If receiving
is blocked, retain the request in the conversation until the shared history is
reconciled; do not invent a globally unique ID from an outdated checkout.

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

For every `Continue` session, also use the append-only `WORK_SESSIONS.md`
coordination log. After the clean fast-forward pull and request-log entry,
append a `STARTED` record with the request ID, UTC time, human machine label,
hostname/OS/architecture, checkout path, branch/upstream, starting commit and
bounded task. Commit and push this start record before substantive work. If
that publication fails, stop before the task. At task completion, append a
matching `COMPLETED` record with the UTC end time, outcome, changed files,
checks/skips, evidence, next task and release state before staging the scoped
task changes and making the final commit/push. Do not edit the log after that
push; report the delivery commit in the final response because a commit cannot
contain its own hash. If the same request already has an open `STARTED` record,
resume it rather than adding a duplicate. An open record on another owner
requires the existing handoff/release procedure. These committed records help
coordinate owners but are not a lock and cannot reveal another checkout's
unpublished work or live processes.

## Short continuation request

When the user says **Continue** as a task instruction in this repository
(ignoring capitalization and trailing punctuation), apply this full workflow.
This shorthand replaces the long prompt at the user's request, R003 in
`REQUEST_LOG.md`; it includes authorization to commit and push the scoped work.

1. Perform the read-only identity, ownership, Git status/branch/upstream and
   stash checks. Read `SESSION_HANDOFF.md`, the latest request entries and any
   open `WORK_SESSIONS.md` record. Do not pull over staged, unstaged or
   untracked work; inspect/fetch upstream read-only if needed, then stop to
   reconcile local work deliberately. On a clean intended branch, always run
   `git pull --ff-only --no-rebase --no-autostash` against its configured
   upstream, for same-owner continuations as well as receiving handoffs. If it
   fails, conflicts, or histories diverge, stop and reconcile explicitly; do
   not reset, rebase, force, or enable autostash. Review incoming commits and
   reread the updated handoff/log. Then append the actual user request to
   `REQUEST_LOG.md`, identify the bounded task, and append/commit/push its
   `STARTED` record in `WORK_SESSIONS.md` before substantive work. Resume an
   unfinished same-owner task rather than starting the next listed task.
2. Carry out that task and its prescribed checks through completion. Preserve
   user work, scientific assumptions, acceptance thresholds, and recorded stop
   conditions. Fix understood implementation errors within the task's scope.
3. At completion or a research-decision boundary, record evidence, changed
   files, checks/skips, and unresolved questions. Update the request log,
   relevant Markdown, `SESSION_HANDOFF.md`, and the matching completion entry
   in `WORK_SESSIONS.md` with one concrete next task, model/effort
   recommendation, completion criteria, stopping conditions, and owner release
   state. Explain when the next model should recommend a different
   model/effort. Append the completion entry before final staging/commit/push.
4. Stage only the task's changes, commit, and push to the current branch's
   configured upstream. Honor this authorization without asking the user to
   repeat it. Preserve unrelated changes and Git history; do not force-push.
   Report any actual permission, remote, or publication blocker accurately.
   Do not make a post-push log edit.
5. Stop at the bounded task's recorded stopping point. Report the result,
   checks, commit/push outcome, and recommended next model/effort concisely.
   Give **Continue** as the next prompt instead of another long instruction.

An explicit qualification in the user's message overrides the default workflow
(for example, “Continue without pushing”). Quoted examples and mentions of the
word in a question do not invoke it. The shorthand does not itself change the
selected model or schedule another session.

## Switching between the Mac and PC

Treat a computer switch as a handoff between task owners. Default to **one
active writing/execution session for this repository across both machines**:
even separate tasks share `REQUEST_LOG.md` and `SESSION_HANDOFF.md`. A clean
checkout or successful pull does not prove the other session has stopped.
Establish release from the outgoing handoff and any current user clarification;
record receipt on the new owner before substantive work. These records are
coordination notes, not an automatic lock or a remote process check.

An independent user-managed software build outside the shared project files
(for example, POV-Ray installation on the Mac) may continue while the PC owns
the repository review. Record it as ongoing and distinguish it from this task's
processes. It does not itself transfer repository ownership or require a machine
switch; do not stop or restart it without an applicable user instruction.

### Catch an unannounced switch

At each session start, even when the user does not mention switching, read the
current OS/architecture, hostname and checkout path (for example with Python's
`platform.system()`, `platform.machine()`, `platform.node()` and `Path.cwd()`).
Compare them with the outgoing/current owner and intended receiving machine in
`SESSION_HANDOFF.md`. Use a human label such as Mac or PC/WSL plus those local
identity fields; a changed checkout path alone can be a second checkout on the
same machine. Inspect Git status, branch/upstream and pending transfer records.
If the local handoff may be stale, fetch the configured upstream and inspect
its committed handoff/log before deciding that ownership is uncertain; this
updates remote-tracking refs without merging into the working tree. Do not
apply incoming changes over local work. A failed fetch leaves freshness unknown.

A machine/owner mismatch, absent identity, incomplete release or conflicting
task record is a **possible unannounced switch**. Say what was detected before
edits, request-ID allocation, package changes or workload launches. If the
record already establishes release and transfer, proceed with receiving checks
without asking again. Otherwise ask the user to confirm the former session and
task processes have stopped and whether unpublished changes/results remain.
Keep dependent work stopped until that uncertainty is resolved; read-only
inspection can continue. Reconcile any undelivered work before claiming ownership.

Local Git and a successful pull cannot see another machine's dirty worktree,
unpublished commits or live agents/processes. Do not claim guaranteed detection
or silently inspect the other machine. This is a check when a session starts,
not a background watcher. If the same hostname/owner record is stale, a switch
may still require the user's clarification.

At the end of a bounded step on the sending computer:

1. Finish or safely stop this task's child processes, including detached
   render/compiler/MPI workers, and record the cleanup result. End the old
   agent's task; do not leave it continuing edits after handoff. Record the
   request, outgoing machine, intended receiving machine, ownership/release
   state, branch/upstream, source commit, changed files, checks/skips, evidence,
   and one next task with model/effort, completion criteria and stopping condition
   in `REQUEST_LOG.md` and `SESSION_HANDOFF.md`. For an interrupted run, record
   consumed attempts/budgets and partial results; switching never resets a
   once-only attempt allowance or authorizes retry after a stop.
2. Keep large generated outputs and machine-specific environments local. Put
   only the small evidence needed to interpret a result in the repository;
   never transfer compiled binaries or JIT caches between macOS and Linux.
   List any ignored/untracked input required by the next task, its checksum,
   location and transfer or deterministic regeneration method. `/tmp` paths
   are local and disposable. Verify required artifacts on receipt; if an
   irreplaceable input is missing, stop rather than rerunning a once-only case.
3. If the user authorized publication for this step, commit only its scoped
   changes and push the current branch. Otherwise do not publish implicitly:
   leave a clear patch/handoff and do not start overlapping edits on the other
   checkout until the user chooses how to transfer them. Include new untracked
   source/evidence files in any patch transfer; a plain `git diff` omits them.
   If publication is authorized, check the push result and final `git status`,
   and report the exact **delivery commit** after committing. A handoff file
   cannot contain the hash of its own commit: label earlier hashes as source
   or base commits and use the final report/Git history for the delivery hash.
   Publication failure leaves transfer pending. Stop after successful delivery;
   do not make an uncommitted delivery-note edit after the final push.

Before the other computer starts:

1. Read the local handoff as possibly stale (inspect the fetched upstream
   handoff if needed), establish that the sending owner
   released the task, and check `git status --short --branch`,
   `git branch --show-current`, `git rev-parse --abbrev-ref '@{upstream}'` and
   `git stash list`. Do not pull over staged, unstaged or untracked work; first
   preserve and reconcile it deliberately. Inspect existing stashes as possible
   undelivered work; never auto-apply/drop them. Stop for detached HEAD, the
   wrong branch/upstream, or unresolved merge/rebase state.
2. On a clean checkout of the intended branch, record the old HEAD and run
   `git pull --ff-only --no-rebase --no-autostash` against its configured
   upstream. These flags prevent inherited rebase/autostash settings from
   silently changing the handoff procedure. If it fails or histories diverge,
   stop and reconcile explicitly; do not force, reset or retry with autostash.
   Review incoming commits/files and reread the updated handoff/log. Confirm
   HEAD equals the fetched upstream tip and includes the reported delivery
   commit; if HEAD is later, review the intervening changes. Treat a recorded
   source/base commit as an ancestor, not an equality requirement with HEAD.
   A locally cached `origin/main` alone is not evidence of a successful push.
3. Allocate the next request ID as one greater than the largest recorded ID
   (entries can be out of order), append the user's actual request and receiving
   machine/commit, and claim ownership in the handoff. Confirm that the task's
   required inputs and evidence arrived. For an explicit patch transfer, record
   its base, file inventory and reconciliation instead of claiming a Git push.
4. Verify the receiving machine's own package builds, architecture, executable
   paths and applicable resource-monitor behavior before running. Reuse recorded
   checks only while their environment/monitor remains unchanged; refresh live
   capacity at launch. Never copy the PC's `/tmp` environment path as a Mac
   command. Do not assume a successful import on one OS validates the other.
   Never launch the same once-only experiment on both machines.

If a pull creates an autostash or a conflict, preserve both histories, resolve
the request-ID collision explicitly, and drop the stash only after confirming
all of its unique content is present in the worktree or committed history.

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
