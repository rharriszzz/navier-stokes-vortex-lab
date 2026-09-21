# Project status: physical preparation and a realistic movie

Updated 2026-09-21. The [R097 completion-certificate repair](docs/realizability/evidence/r097/README.md)
passed all nine new fixture groups. Acceptance and the outer observation boundary
remain to be reviewed; live/whole-recorder certification stays false. Current
ownership, delivery state and the single review task are in the
[handoff](SESSION_HANDOFF.md#next-task).
A [performance and memory test plan for Mac and PC](docs/realizability/MAC_PC_PERFORMANCE_MEMORY_PLAN.md)
is also ready as documentation; no benchmark has run.
The [technical handoff](SESSION_HANDOFF.md#next-task) records the next task.

Our goal is to determine whether exterior actuators and sensors can prepare
a contracting, stretching, swirling flow that follows the desired process
over a useful finite range, and to provide trustworthy data for a separate,
clear, approximately realistic 3D movie of that process.

**We are currently verifying the numerical tools needed to answer the physical
question. We have an implemented illustrative movie pipeline, but have not yet
demonstrated the required initial setup, an attainable range of contraction,
or a validated flow history for the movie.** The recent progress is in making
the calculations trustworthy; it is not yet evidence that the apparatus works.

## Recent results and their practical meaning

- **The reviews found ways a failed or unfinished calculation could appear
  complete.** Examples include accepting a success report despite an abnormal
  process exit, or declaring completion while supporting processes remain
  active. The required corrections are now specified, including checks that
  work has actually stopped and memory readings are current. R076 passed 16
  fixture/continuity groups; R081's deeper review reproduced eleven additional
  cases needing repair, including stale memory readings and unconfirmed helper
  cleanup. R082's new copy passes 17 fixture groups, with all three attempts and
  one reconciled fixture-only assertion preserved. R083 found omitted tests,
  false completion, host freshness and provenance gaps. R084 repairs those in
  a new copy; all 22 registered checks passed in attempt 3 after preserving two
  non-resource fixture assertion failures and their source-bound reconciliations.
  R085 verified the saved evidence but found residual ownership, cleanup timing,
  protocol and accounting gaps. R088 now passes 14 composed fixture groups on
  its first attempt. R096 reviewed all 14 saved functions; durable type binding,
  monitor evidence, admitted deadlines and independent outer receipts still need repair.
  Live operating-system adapter tests remain pending; further flow
  calculations remain disabled until the required safeguards are validated
  and launch is reviewed.
- **There is no new result yet on physical feasibility.** Previous experiment
  records were preserved, and the latest numerical boundary response still
  fails its accuracy comparison. This review adds no evidence about achievable
  contraction, adequate exterior sensing or practical actuator demands. Those
  questions remain open, and the existing numerical failure does not establish
  that the physical concept is impossible.
- **We now have a plan to choose a computer for each workload.** It compares
  trajectory generation, rendering, encoding and a small assembly/observer
  reference using fixed inputs, repeated timings and peak resident memory.
  Live monitor validation comes first. No benchmark has run under the plan,
  and neither computer has been shown faster or suitable for a larger solve.
- **The movie can still illustrate the concept.** The latest work supplies no
  new validated flow history for a physically supported animation. Connecting
  the movie to reliable fluid calculations remains a later milestone; the
  independent Mac POV-Ray build's completion is still unverified.

## Overall progress and remaining milestones

The software foundation is in place: we can generate illustrative tracer
motion, render it, and run reproducible numerical verification cases. We have
also built independent reference, stability, boundary-load and measurement
checks that expose errors an apparently plausible flow picture would miss.
The central research question remains unanswered because the boundary-driven
fluid calculation has not yet passed its physical accuracy checks.

| Milestone | Position now | Work still needed |
|---|---|---|
| Explain the apparatus and intended motion | Illustrative movie pipeline implemented | Further visual refinement is possible; label the prescribed flow clearly. |
| Trust the numerical boundary response | R088 passes composed fixtures; acceptance review pending, live adapters unvalidated and physical accuracy failed | Complete the [current handoff task](SESSION_HANDOFF.md#next-task), then review OS implementation and live validation before physical execution. |
| Determine what exterior actuators can influence | Benchmark commands/features defined; full six-input response campaign has not begun | Validate responses, then assess independent influence, conditioning and required amplitudes/times. |
| Determine what exterior sensors can distinguish | Basic sensor fixtures exist; B3 sensing study has not begun | Test pressure/PIV information with realistic noise, resolution and delay. |
| Prepare the desired initial flow | Concept and candidate hardware only | Define acceptable initial-state errors; test a finite actuator layout and its physical limits. |
| Establish the useful finite evolution | No demonstrated contraction range | Compare preparation alone with any continued driving, quantify attainable scales and duration, and validate against bench measurements. |
| Supply physically supported movie data | No validated time-dependent preparation/contraction dataset | Export a checked flow history, tracer paths and hardware/sensor records to the separate renderer. |

These are research milestones, not a schedule or a percentage-complete estimate.
The accuracy investigation may reveal that a different numerical approach is
needed. Later reachability or hardware tests may identify a useful finite limit
or a negative result. Neither outcome can be inferred from the present failed
numerical comparison. Explanatory movie work can proceed independently of
these scientific gates.

## The two goals guiding the work

1. **Physical feasibility:** determine whether equipment acting and sensing
   from outside the fluid can establish a sufficiently good initial flow to
   carry out some orders of magnitude of the intended process. This includes
   learning which interior quantities can be influenced and measured, what
   preparation requires, and how long the prepared state remains useful.
2. **Visualization data:** supply the geometry, flow evolution, tracer motion,
   and relevant actuator/sensor information needed for a separate 3D movie
   that is understandable and approximately realistic. The scientific data
   and the rendering should remain separate so improvements to either do not
   require conflating them.

For the first goal, we need to distinguish **preparing the initial state** from
**sustaining its later evolution**. It is not established that preparation alone
will suffice. A later experiment should state whether actuators are turned
off, follow a prescribed command, or use feedback during the process. Any
continued driving must be reported as part of the requirements. We should
not assume a full feedback controller is necessary before testing simpler
possibilities, nor assume the prepared flow will sustain itself.

“Some orders of magnitude” is an ambition whose measured quantity and range
still need to be specified. A factor of 100 in core radius differs greatly
from a factor of 100 in a similarity-time variable. Under the proposed
`r_c ∝ sqrt(tau)` scaling, a tenfold decrease in radius corresponds to a
hundredfold decrease in tau. Here tau is a finite-range scaling parameter;
we are not proposing to reach a mathematical singularity. The existing
10 mm → 3 mm benchmark is a prescribed initial test target, not an achieved
contraction or a limit on the user's eventual goal.

## What I am working toward now

The immediate objective is a **reliable, affordable calculation of how boundary
commands change the central flow**. That is a prerequisite for choosing a
preparation protocol: otherwise an apparent success or failure could be caused
by numerical error. The corresponding sensing study must then establish
whether realistic measurements can distinguish the states we need to prepare.

The present benchmark starts with small disturbances about resting water in
a nominal cylindrical vessel. It uses linear Stokes equations, not a full
nonlinear simulation of an already developed, contracting vortex. Its central
measurements include rotation, axial strain and signed perturbation components.
Passing this benchmark would justify the next response studies; it would not
by itself demonstrate preparation or several orders of the process.

The [current numerical handoff](SESSION_HANDOFF.md) specifies the next small
diagnostic. This status report records the broader purpose without changing
that experiment's parameters, acceptance criteria or resource limits.

## How far we have gotten

| Area | What exists | What it establishes, and what is missing |
|---|---|---|
| Illustrative movie | Python tracer integration, POV-Ray rendering and ffmpeg encoding, with example scene and motion settings | A usable way to explain the concept. The flow is prescribed; the rendered actuators do not generate it. It is not a validated physical evolution. |
| Target and measurement definitions | A finite reference target, boundary-command basis, central-flow features, and basic sensor/response diagnostics (B0) | A reproducible vocabulary for testing the idea. Prescribing a target does not show that exterior hardware can create it; sensor fixtures are not an observability study. |
| Fluid-response calculations | Two optional linear Stokes implementations and verification cases (B1/B2) | B1 failed its strong-divergence check. B2 addresses that issue in recorded cases, but its physical tangential-response accuracy remains unresolved. |
| Stability and accuracy checks | Independent swirl reference, repaired reporting, positive dissipation certificates on four meshes, and one completed physical response audit | The audited 50 mm case passes PDE checks but fails reference accuracy by a large margin. Stability does not establish response accuracy, and the physical B2 gate still fails. |
| Physical preparation and sensing | Research plan and candidate mechanisms | No demonstrated preparation protocol, validated actuation/measurement response study, or hardware feasibility result yet. No demonstrated multi-order evolution. |
| Data for a physically supported movie | Existing illustrative trajectories and numerical reference/diagnostic records | Useful explanatory material, but no validated time-dependent preparation/contraction dataset or completed export from such a calculation to the movie. |

The [project tracks](PROJECT_TRACKS.md) and [research roadmap](CONTROL_RESEARCH_ROADMAP.md)
give the implementation and longer-term context. There is no defensible
percentage-complete estimate for the physical goal: the key feasibility
questions are still open.

## What the latest work tells us

The [stability study](docs/realizability/B2_RESPONSE_COERCIVITY_RESULT.md)
established that the unforced discrete model dissipates energy at one tested
numerical setting (alpha=96) on the recorded 50/40/30/25 mm meshes. Alpha is a
numerical boundary-enforcement parameter, not an actuator strength. This removes
a particular stability uncertainty on those meshes. It does not select the final numerical settings
or establish the accuracy of a driven flow.

The [accuracy review](docs/realizability/B2_ACCURACY_REVIEW.md) reproduced an
independent reference for one simple case: periodic, axisymmetric tangential
wall motion about rest. At the benchmark's very small wall-speed amplitude
of 1e-7 m/s and frequency 0.01 Hz, the reference central disk-rotation amplitude
is approximately 6.91e-12 per second. Reference evaluation is reproducible far
below the comparison scale. The subsequent
[single physical response audit](docs/realizability/B2_PHYSICAL_RESPONSE_AUDIT.md)
ran the repaired solver on one coarse, stability-certified mesh. It completed
within the resource limits and passed its algebraic and divergence checks, but
its central response amplitude was about **29,000 times the reference**, with
about **74 degrees of phase error**. It cannot be used as validated physical
response data.

One residual correction changed that result negligibly. Finer measurement
quadrature also left the large discrepancy, while its own remaining sensitivity
was still too large relative to the tiny reference. The next numerical question
is how to distinguish inadequate boundary-layer resolution from effects of
the faceted vessel and its projected boundary command. This result establishes
a failed accuracy check on one mesh; it does not establish a universal numerical
error floor or a limit on physical actuation.

That tiny reference response is useful evidence about this particular way of
driving resting water. It does **not** establish that exterior actuation is
generally ineffective, that a prepared vortex cannot be influenced, or that
the response is experimentally detectable. Pumping, an established circulation,
nonlinear evolution and realistic sensor noise have not been settled by this
test. The current 5% magnitude/5-degree checks concern numerical comparisons;
they are not yet a definition of “good enough” for the physical experiment.

## What remains to answer the physical goal

After the current numerical accuracy issue is resolved, the work needs to
connect several distinct questions:

1. **Influence:** which combinations of exterior commands can independently
   change the interior features of interest, and with what amplitudes and
   preparation times?
2. **Measurement:** can exterior sensors identify those features with realistic
   noise, resolution and delay? Outside cameras viewing seeded fluid through
   the tank are one candidate; wall-pressure measurements alone must be assessed
   separately. Neither arrangement has been shown sufficient here.
3. **Preparation:** can a finite, physically plausible actuator arrangement
   create the required initial flow within speed, stroke, flow-rate, force and
   bandwidth limits? An ideal prescribed wall velocity is not a hardware design.
4. **Finite evolution:** starting from that prepared state, what range of
   contraction and other desired behavior survives viscosity, disturbances and
   practical limits? Measure the range attained and any continued actuation
   required, including a useful negative or finite-limit result.

“Good enough” will need an agreed set of observable targets, tolerances,
duration and range, rather than exact reproduction of an entire mathematical
velocity field. These choices remain open; this report does not silently set
them. A successful small response study must still be followed by an appropriate
finite-amplitude flow investigation and, eventually, experimental checks.

## How the research should support the separate movie

The movie can already illustrate the intended mechanism. Its next level of
physical support should come from a documented dataset that the renderer reads,
with the numerical integration kept outside POV-Ray. The proposed data handoff
should contain:

| Data | Purpose in the movie |
|---|---|
| Vessel and actuator geometry, coordinates and physical units | Keep dimensions and hardware placement consistent. |
| Time-stamped velocity fields or reproducible field evaluation, plus derived tracer paths | Show motion supported by the stated model; keep physical time distinct from playback time. |
| Core radius, rotation/swirl, strain and perturbation histories | Show what changes and quantify the finite range actually represented. |
| Actuator commands and predicted sensor readings, where available | Connect preparation and any continued driving to the depicted flow. |
| Model assumptions, parameter values, numerical uncertainty and validity interval | Distinguish a prescribed illustration, a verified benchmark and a physically supported prediction. |

This is an intended handoff, not an implemented or validated export contract.
A simpler representation fitted to reliable flow data may be adequate for a
clear movie, provided its approximation and range of validity are documented.
Useful visual aids can include enlarged tracer markers, cutaway views, arrows,
colour scales or slowed playback. Such choices should be labelled and should
not change the underlying physical trajectory or imply that exaggerated
actuator motion generated it. Preparation and subsequent evolution should be
shown as distinct stages when data for both become available.

The two goals can therefore advance at different rates: a clear explanatory
movie can precede physical feasibility, while later validated data should
replace or constrain its illustrative motion. Visual clarity alone is not
evidence of realizability.

## Latest scientific checkpoint and monitor review

The [R067 review](docs/realizability/B2_PHYSICAL_RUNNER_REVIEW.md) confirms the
saved observer/oracle coverage and the patched FFCx package, but finds stale
launch limits, incomplete evidence binding and failure/count reporting gaps.
R070 completed the disposable repair and R073 added passing fake monitor checks.
The [R074 adapter review](docs/realizability/B2_MONITOR_ADAPTER_REVIEW.md)
reproduces root/descendant completion, cleanup-exception, clock/scheduling/input
and return-code acceptance gaps. It specifies Linux containment/RSS/cleanup
and Windows host-pressure semantics. R073's ledger is preserved, with incomplete
all-attempt timing/RSS evidence explicitly noted. R076 implemented the fixture
contract and passed 16 check groups. R081's
[review](docs/realizability/B2_MONITOR_LIVE_VALIDATION_CONTRACT.md) reproduced
eleven remaining gaps and froze a ten-case future PC suite. It found a candidate
user-owned cgroup delegation read-only, with operations still untested; this
Python build lacks the pidfd wrappers. R076's timing covers its validator
subprocesses, not all recorder overhead. R082's new copy passed 17 fixture
groups; its explicit attempt-2 fixture reconciliation and outer-source hash
limitation are documented in
[R082 evidence](docs/realizability/evidence/r082/README.md). R084 completes the
G01–G07 fixture repairs in a separate copy: 22/22 registered groups passed on
attempt 3, while attempts 1 and 2 remain charged and source-bound as understood
fixture assertion reconciliations. The [R084 evidence](docs/realizability/evidence/r084/README.md)
records 15.691/120 s, a 30,060,544-byte maximum validator lifetime RSS and the
excluded timing scope. These are fixture results; no live adapter, native
helper, workload or physical run occurred. The [R085 review](docs/realizability/B2_MONITOR_R084_REVIEW.md) confirms the saved
22-function result and identifies residual composition, timing, protocol and
accounting gaps. Follow the [current handoff](SESSION_HANDOFF.md#next-task) for
acceptance review of the [R088 composed fixture result](docs/realizability/evidence/r088/README.md)
before the separate OS harness. R088 records 14 passing groups, 5.633/120 s
charged and 23,941,120 B validator peak RSS; outer guard startup/final persistence
remain excluded, so no whole-recorder or live certification is claimed.
The later observer/assembly reference retains unchanged numerical screens;
monitors must pass first. No comparative solver performance or physical
execution is established by these reviews.
The independent Mac POV-Ray build remains outside this task; its movie check
is deferred. R080 returns ownership to PC after this plan is published. See the
[handoff](SESSION_HANDOFF.md#next-task).

The [R033 prerequisite result](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_FOLLOWUP.md)
completes the disposable q=64/q=96 fixture and the actual pre-solve observer
checks. The five original phases, wrong-root and parent refusals, 16 high-order
facet checks, missing-layout/wrong-offset/lifting refusals, and compatible
P/A/A plus incompatible P/first-A/second-A cases all passed. The observer ran
once per case, agreed with the full block oracle, and recorded zero factor or
solve events. Four attempts used 56.25 seconds cumulatively; the largest
sampled child-tree RSS was 571.42 MiB, below the capacity-sized 1536 MiB cap.
The final cache-reuse pass peaked at 171.24 MiB. Two understood fixture defects
were repaired in the disposable copy, and every attempt was preserved.
**No physical child, PDE solve, factorization or flow response ran.** The B2
physical accuracy gate remains failed. R067 completed the observer/physical-path
review without launching that comparison; R070/R073/R074 still launch none.

R023's qualified 600-second/2048-MiB allowance was sized down for R033 after
the live Windows host check: the first launch used a 1536-MiB child-tree cap
with 2.66 GiB host memory available, and subsequent readings showed more
headroom. The R022 prerequisite work is now complete. Any later physical
attempt needs its own capacity estimate and must satisfy the unchanged
[R021 experiment contract](docs/realizability/B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md).

The latest physical attempt remains
[R020](docs/realizability/B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md): P's checked
response still fails reference accuracy, and A_32 was refused at pressure
compatibility. The paired physical comparison, continuum geometry-error
allocation and total FEM error floor remain unknown. The physical-response
campaign stays blocked (`campaign_ready=false`). Preparation, sensing, hardware
feasibility and a validated movie trajectory remain the later milestones
listed above.

## What the resource budgets mean

The previous 60-second/512-MiB toy allowance and 180-second/1.5-GiB physical
allowance were conservative watchdog settings chosen for bounded diagnostic
tasks. They were not hardware limits, a monetary budget, or numerical accuracy
criteria. A “toy” is a small verification problem, such as one tetrahedron with
a known polynomial velocity, used to check the implementation before a larger
flow calculation.

“Cumulative” applies to wall-clock time across the prerequisite phases and
failed attempts within that task. Imports, compilation and test reporting
count; analysis, editing and time between separate attempts do not. R022 used
5.24 seconds in its first attempt and 11.17 seconds in its second, totaling
16.41 seconds. This is not a running allowance for the lifetime of the project.

Memory is checked separately: the watchdog samples the sum of resident RAM
reported for the active test and its descendant processes, including compilers,
about every 0.05 seconds. Memory peaks from sequential tests are not added
together. Summed process RSS can count shared pages more than once; it is a
conservative process-tree measure, not the whole computer's memory usage.
R022 was stopped at 513.61 MiB by that watchdog, not by a reported system
out-of-memory condition.

The [R023 resource snapshot](docs/realizability/evidence/r023/resources.json)
shows approximately **7.6 GiB RAM visible to WSL**, with **6.3 GiB available**
at inspection, and 28 logical CPUs visible. A subsequent
[R024 Windows check](docs/realizability/evidence/r024/resources.json) found
**15.7 GiB usable host RAM, with 2.1 GiB available**. WSL then reported about
6.8 GiB available inside the guest. The two availability readings describe
different views of shared physical RAM; they cannot be added. Available RAM
varies as other applications run.

The user reports Chrome using 2.7 GB. Closing unused tabs/apps can make room
before larger calculations. The current approximately 8 GiB WSL ceiling was
sufficient for the completed prerequisite run, so increasing that ceiling was
unnecessary. It is consistent with the default of half the host's memory;
the user confirmed **8 GB memory and 2 GB swap** in WSL Settings in R025.
Swap is disk-backed overflow and is not counted as RAM for the planned test.
Microsoft documents inspection/configuration through Start-menu WSL Settings
or `%UserProfile%\.wslconfig` in its
[WSL configuration guidance](https://learn.microsoft.com/en-us/windows/wsl/wsl-config).

The user authorizes using the PC within its capabilities. Future local jobs
should use allowances based on available RAM and expected work, leaving room
for the operating system and other applications. R033 rechecked both Windows
and WSL before each attempt, did not count swap as RAM, and preserved its
600-second/1536-MiB limit. R074 specifies the remaining monitor/integration
requirements before any physical launch. Retain the provisional physical
180-second/1536-MiB limits. Preserve watchdogs, finite reports,
scientific acceptance thresholds and the recorded experiment scope. Historical
R022 resource results remain unchanged.

The user's Mac is an **Apple M4 iMac with 24 GiB RAM**. Its dated snapshot
recorded 68% system-wide free memory and 591 GiB free project-volume storage.
The pinned FEM packages import in its Conda environment, and two-rank MPICH
startup succeeded; no FEM assembly/solve or same-input reference comparison
has run. Conda reports FFCx 0.10.1 while the imported module reports 0.10.0.
R055 traced this to upstream v0.10.1 packaging metadata that still declares
project version 0.10.0; the release contains a critical quadrature-rule
code-generation fix, so retain the 0.10.1 pin. R058 checked the live Mac Conda
metadata: build, artifact URL and SHA-256 match the R056 PC record. See
[Mac readiness evidence](docs/realizability/evidence/r058/mac_readiness.json).
R056 confirmed that the PC already has conda-forge `fenics-ffcx 0.10.1`
(`pyhbc3ee6d_1`). R014/R016/R020 used this environment after installation, so
their `ffcx: 0.10.0` report values are module self-reports, not evidence of an
unfixed package; no rerun is required. R067 verified the installed compiler
files against package metadata and found the inspected repeated integrals merge
during symbolic analysis. Historical loaded binaries are not fully attributable
from cache timestamps; use the documented provenance checks for future runs.
The next FEM reference run should use a fresh isolated cache and record the Conda build/hash
separately. See [R056 environment evidence](docs/realizability/evidence/r056/ffcx_pc_environment.json).
The latest PC snapshot showed 15.72 GiB total/5.44 GiB free in Windows and
7.61 GiB total/6.73 GiB available in WSL; these are overlapping views of
shared host RAM. The Mac's 4 performance/6 efficiency cores and the PC's 28
WSL-visible logical CPUs do not establish comparative speed; no matched run
exists. The PC's R033 Linux observer/runner and resource checks were
exercised, so retain the PC for the current monitor implementation. The Mac is
a plausible future memory-sensitive FEM
candidate, but neither workload fit nor relative runtime is established. See
the [R053 comparison evidence](docs/realizability/evidence/r053/machine_snapshot.json)
and [handoff assessment](SESSION_HANDOFF.md#r053-machine-task-allocation-checkpoint).
Complete the R074 adapter implementation and required live validation before
refreshing capacity and running the specified observer/assembly reference on
both hosts. No physical calculation or matched benchmark was run for this comparison.

For the Mac software inventory (R054), the FEM Conda environment and MPI
startup have passed import checks, and `ffmpeg`/`ffprobe` are present. POV-Ray
is the remaining confirmed tool missing from the checked shell for the full
movie pipeline. The FFCx version-string discrepancy is explained by upstream
release metadata; retain the pinned 0.10.1 code. See the [Mac install handoff](SESSION_HANDOFF.md#next-task)
and [R055 finding](SESSION_HANDOFF.md#r055-ffcx-version-discrepancy).

The remaining Mac setup is in
[MAC_INSTALL_AND_BENCHMARK_PLAN.md](docs/realizability/MAC_INSTALL_AND_BENCHMARK_PLAN.md);
the new [Mac/PC test plan](docs/realizability/MAC_PC_PERFORMANCE_MEMORY_PLAN.md)
is the comparison protocol for both machines.
R058 confirmed that MacPorts is already installed, POV-Ray is not registered,
Xcode/clang is available, and ffmpeg/ffprobe 4.4.2 execute with libx264 listed.
R065 reports a POV-Ray build already running; check its outcome at a later Mac
session rather than launching another install. Once verified, use the guide's
fresh source copy for the one-frame and ten-frame checks. A passing
movie check establishes visualization readiness; FEM assembly, solving and
portable resource-monitor validation remain pending. No install or benchmark
was run as part of R058. R067 has now specified an observer/assembly reference
and comparison screens, with no solve benchmark or host winner inferred.

R065 retained PC ownership historically; R079 transferred it to Mac
for this documentation task after receipt of R076's published completion.
R080 returned ownership to PC; R081 received the delivery and completed the review.
R067/R070/R073/R074/R076/R081/R082/R083/R084/R085/R088 are complete within their recorded scope; live
validation remains ahead of a separately scoped reference. Follow the current
handoff instead of replaying older tasks. Mac movie readiness and visualization
benchmarks can be scheduled independently. The workload revision stays fixed
across later evidence commits; ignored benchmark inputs need an
explicit checksum-verified transfer. R063 adds a local machine/owner check at
session start. Uncertain ownership requires clarification; local Git cannot
detect the other machine's unpublished work or running processes.
