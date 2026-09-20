# Project status: physical preparation and a realistic movie

Updated 2026-09-20 for
[R022](REQUEST_LOG.md#r022--2026-09-20--continue-with-overall-progress-in-statusmd),
following the higher-order prerequisite tests and their memory-cap stop.
The goals below preserve the
[R010 status-report request](REQUEST_LOG.md#r010--2026-09-20--project-status-and-user-goals).

Our goal is to determine whether exterior actuators and sensors can prepare
a contracting, stretching, swirling flow that follows the desired process
over a useful finite range, and to provide trustworthy data for a separate,
clear, approximately realistic 3D movie of that process.

**We are currently verifying the numerical tools needed to answer the physical
question. We have an implemented illustrative movie pipeline, but have not yet
demonstrated the required initial setup, an attainable range of contraction,
or a validated flow history for the movie.** The recent progress is in making
the calculations trustworthy; it is not yet evidence that the apparatus works.

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
| Trust the numerical boundary response | Current active stage; verification tools exist, physical accuracy gate fails | Finish the capped compatibility tests, then complete the matched-boundary comparison and resolve the resulting accuracy questions. |
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

## Latest checkpoint and the immediate next step

The [R022 prerequisite result](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_RESULT.md)
adds a disposable implementation of the R021 q=64/q=96 comparison and its
pre-solve compatibility barrier. The five original prerequisite phases,
wrong-root refusal and parent refusal passed. Both complex polynomial traces
passed their high-order projection and load checks on all four faces at both
orders: **16 checked facet cases**. Those tests validate polynomial integration
on a toy tetrahedron; they do not establish physical response accuracy.

The new test child then reached **513.61 MiB**, exceeding the unchanged
**512 MiB** child-tree cap, and the watchdog stopped it. Across both recorded
toy attempts, including a corrected JSON-reporting bug, elapsed time was
**16.41 seconds**. The actual harmonic pre-solve observer tests were not reached.
**No physical child, PDE solve, factorization or new flow response ran.** The
new runner remains unvalidated for physical execution.

The next bounded task is to isolate the high-order and observer toys in separate
processes and improve stage/memory reporting, preserving all tests and the
60 s/512 MiB cumulative toy limits. It stops after a complete prerequisite
result or another finite refusal, before physical execution. The
[session handoff](SESSION_HANDOFF.md) gives the exact checks and stopping rules.
A later physical attempt would still need to satisfy the
[R021 experiment contract](docs/realizability/B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md).

The latest physical attempt remains
[R020](docs/realizability/B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md): P's checked
response still fails reference accuracy, and A_32 was refused at pressure
compatibility. The paired physical comparison, continuum geometry-error
allocation and total FEM error floor remain unknown. The physical-response
campaign stays blocked (`campaign_ready=false`). Preparation, sensing, hardware
feasibility and a validated movie trajectory remain the later milestones
listed above.
