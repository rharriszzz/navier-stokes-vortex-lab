# Project status: a boundary-controlled engineering approximation

Updated 2026-09-21 (America/New_York), R171–R177. PC/WSL `daisy` owns the
repository. This assessment uses current source, saved experiment records and
the motivating paper; it launches no simulation or rendering workload.
The single [next task](SESSION_HANDOFF.md#next-task) is recorded in the handoff.

## Goal and present conclusion

The user's goal is **a visual simulation of an engineering approximation of
the first few orders of magnitude of the recent OpenAI result, with forcing
and sensors on the boundary only**. R172 confirms the motivating reference is
OpenAI's [*Finite time blowup for Navier–Stokes*](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf),
released with its [September 8 announcement](https://openai.com/index/navier-stokes-solution/).

**We have a working illustrative animation pipeline, a separate finite
reference flow, and useful numerical verification tools. We have not yet
demonstrated an accurate boundary-driven contracting flow, boundary-only
state estimation, or any physically validated number of decades.**
The completed preview is a visualization milestone, not completion of the
engineering goal.

R173 explicitly accepts that boundary-only forcing and sensing might make
the goal impossible, provided the project gives a clear explanation. A
supported negative result or a quantified finite limit is therefore a useful
deliverable, not a reason to weaken the boundary-only requirement.

The paper's Theorem 1.1 concerns smooth forcing in the fluid volume, starting
from rest, with bounded kinetic energy and finite-time unbounded velocity.
It does not provide a finite tank with boundary actuators and sensors.
Replacing that forcing by boundary action is an additional engineering and
control problem. Our attainable finite range must be measured, not inferred
from the theorem. We are not attempting to simulate the singular limit.

## What we have succeeded in doing

| Aspect | Accomplishment and evidence | Limit of the result |
|---|---|---|
| End-to-end visualization | Deterministic Python/RK4 tracer generation, saved-frame checking, POV-Ray rendering and H.264 encoding work together. R169 produced a checked 30-frame, one-second, 320×180 preview. | Motion comes from a prescribed velocity field. No boundary-control calculation generates this movie. |
| Input integrity | The independent [trajectory checker](check_trajectories.py) passed the actual PC inventory of 450 frames with 128 tracers each; separated frames 1/225/450 were visibly different. | Finite coordinates, bounds and motion do not establish incompressibility, momentum balance or integration convergence. |
| Cross-platform rendering | Mac renderer failure was diagnosed and repaired; installed revision 6 passed beads and project-frame checks. PC headless, one-thread rendering passed the bounded preview. | Mac and PC used different saved datasets; no equal-input performance comparison is established. The earlier PC crash's exact cause is unresolved. |
| Physically interpretable reference | [Reference code](realizability/reference.py) defines a smooth divergence-free, windowed Gaussian-vorticity target in SI units, with core radius 10 mm → 3 mm over 100 s. | This is a prescribed verification/reference field, not the paper's witness or an achieved boundary-driven trajectory. It is separate from the movie field. |
| Boundary commands | [Six implemented modes](realizability/boundary_modes.py) cover balanced normal strain, tangential swirl and both phases of normal/tangential m=4 perturbations. | These are ideal continuous wall velocities, not a validated finite actuator array or a successful six-input response campaign. |
| Measurement and analysis tools | Signed strain/rotation/mode features, core-peak diagnostics, stress correlations, pressure-difference covariance and phase-aware rank/identifiability tools exist. | Synthetic feature/rank checks do not establish sensor observability or an estimator for the actual flow. |
| Fluid solver verification | Two optional finite-element Stokes backends exist. B2 provides divergence-conforming discretization and passed scoped mass-balance/arithmetic checks where B1's strong-divergence screen failed. | Neither is a validated nonlinear contraction simulation. B2's physical-response accuracy gate still fails. |
| Independent error detection | Independent swirl reference, boundary-load checks, disk integration and stability studies expose wrong answers despite small linear residuals. | Detecting the error is a useful success; resolving it is still necessary before using the response for engineering. |

The [track overview](PROJECT_TRACKS.md), [benchmark](BOUNDARY_CONTROL_HANDOFF.md)
and [control roadmap](CONTROL_RESEARCH_ROADMAP.md) document the foundations.
Their older future-task language is historical where it conflicts with the
current handoff or the stricter sensing requirement below.

## What the current movie actually shows

The preview is `/tmp/r169-preview-EnjJq0/preview.mp4`, disposable local output
outside Git. R169 recorded H.264, yuv420p, 30 fps, 30 frames and 1.000000 s.
Three separately rendered snapshots sampled the beginning, middle and end of
the 450-frame PC dataset. R171 inspected existing headers and source; it did
not rerun the renderer, checker or ffprobe.

| Saved frame | Model time | Declared TauRatio | Declared CoreRadius |
|---|---:|---:|---:|
| 1 | 0 | 1 | 0.34 |
| 30 | 0.9666666667 | 1 | 0.34 |
| 225 | 7.466666667 | 0.1018442311 | 0.1812615792 |
| 450 | 14.96666667 | 0.01 | 0.1003803658 |

These radius values are scene coordinates, without an established conversion
to the benchmark's metres. The one-second clip covers initial tracer motion
before the scheduled contraction progresses. It is not a time-compressed
movie of the entire 15-second illustrative sequence.

[make_trajectories.py](make_trajectories.py) prescribes contraction, stretching,
swirl and an oscillatory m=4 perturbation. Its full field is not guaranteed
divergence-free; it also clips/constrains tracer positions near the numerical
bounds. No pressure, momentum equation or actuator-to-fluid response is solved.
The exported core marker follows `0.32 * TauRatio**0.30 + 0.02`, independently
of a core measurement from the velocity. The full dataset's label spans two
decades in TauRatio and approximately 3.39-fold marker-radius reduction.
Those are animation settings, not demonstrated physical scaling.

[fluid.pov](fluid.pov) currently hides the core, actuator, sensor and PIV
overlays by default. The optional [hardware illustration](actuators.inc)
contains three rings of 16 actuator markers and three rings of eight sensor
markers inside a box-shaped [tank](tank.inc). Those rings are not the wall
of the fluid domain. The research benchmark instead uses a cylinder of radius
0.10 m and full height 0.30 m. Geometry, units and actual boundary locations
must be reconciled before the movie can depict a particular engineered system.

A further distinction matters for fidelity to the paper: Section 2 describes
both radial and axial core scales shrinking, with the radial scale shrinking
faster. Material axial stretching/outflow does not mean the region of intense
flow grows in height. Our optional core graphic grows in half-height from
0.55 to 0.715; that is not a quantitative depiction of the paper's axial scale.
[Paper, Section 2](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf)

## Boundary forcing: what is implemented and what remains

For the proposed engineering calculation, imposed actuation must enter at the
actual fluid boundary. The baseline interior model is incompressible
Navier–Stokes with no imposed volumetric actuation:

```text
∂t u + (u·∇)u = -∇p/ρ + ν∇²u,    ∇·u = 0
boundary velocity/traction = physically interpretable actuator commands
```

The current research [configuration](realizability/config.py) uses nominal
water properties, ν=1e-6 m²/s and ρ=1000 kg/m³. Normal side-wall modes represent
balanced recirculation through a porous liner; tangential modes represent
moving wall elements. Endcaps are stationary. Instantaneous zero net volume
flux is built into the ideal normal basis. A fixed porous-wall model is not
automatically a finite-stroke diaphragm model.

We have run boundary-driven **linear Stokes** pilot calculations about rest,
without volume forcing. Manufactured body forces used in solver verification
are separate test fixtures and are not an allowed engineering actuator.
Linear Stokes omits nonlinear transport, so it cannot demonstrate the vortex
spin-up and nonlinear perturbation-stress mechanism central to the larger goal.

No reliable multi-input influence matrix, optimized command history, finite
actuator model, stroke/bandwidth/power feasibility result, nonlinear controlled
contraction or closed-loop controller has been established. Preparing the
initial state and sustaining its subsequent evolution are distinct tasks:
future results must say whether actuation stops, follows a prescribed history
or responds to sensors.

A useful engineering approximation should first match selected interior
observables. Exact reproduction of an arbitrarily volume-forced field is
generally a different problem: where exact matching to an unforced interior
solution is proposed, the target momentum residual must be a pressure gradient.
The [benchmark's residual criterion](BOUNDARY_CONTROL_HANDOFF.md#35-boundary-control-cannot-reproduce-every-forced-target-pointwise)
explains this necessary condition; it does not rule out approximate matching.

## Boundary sensors: an explicit requirement gap

R171's boundary-only requirement is stricter than the older plans that feed
interior PIV features into a controller. Pending clarification, this report
uses the strict interpretation: feedback contains only measurements of
boundary quantities, such as wall pressure and declared actuator measurements.
Interior fields and tracer images may be used for validation and visualization,
but may not be passed to the controller as measured state.

A camera outside the tank that measures interior velocities has exterior
hardware but interior measurement support. Whether that is permitted is a
separate user choice; it is not silently counted as boundary-only sensing.
No controller exists yet, so this is a specification gap, not a discovered
violation by a running controller.

There are useful early deductions and implemented checks:

- In the linear rest-Stokes benchmark, axisymmetric pure swirl has no
  first-order pressure signature. Wall pressure alone has a blind direction
  for that state. This does not prove pressure is useless around an established
  vortex, or that all boundary sensing is impossible.
- Eight equally spaced samples on one ring cannot distinguish both independent
  m=4 phases. The movie's marker count therefore is not a validated sensor
  layout. Multiple measurements, locations and physical operators require
  their own rank/noise analysis.
- [sensors.py](realizability/sensors.py) handles relative pressure and correlated
  reference noise; [response.py](realizability/response.py) handles complex
  response normalization and finite-family identifiability. These are analysis
  components, not a completed dynamic observability study.

B3 sensing, noisy/delayed measurements and state estimation have not begun as
a validated flow study. Potential additional boundary measurements, such as
shear/torque, would need explicit hardware and measurement definitions before
selection. They are not assumed available or sufficient.

## The main numerical obstacle, and what we learned from it

B1's Taylor–Hood implementation failed the required strong-divergence
tolerance. B2's divergence-conforming formulation addressed that issue in
recorded cases. A separate [stability study](docs/realizability/B2_RESPONSE_COERCIVITY_RESULT.md)
certified positive homogeneous dissipation at numerical penalty alpha=96 on
the recorded 50/40/30/25 mm meshes. This is stability evidence for those
discretizations, not nonlinear stability or response accuracy.

An [independent accuracy audit](docs/realizability/B2_PHYSICAL_RESPONSE_AUDIT.md)
then found that the 50 mm, alpha=96 tangential response at 0.01 Hz was about
28,963 times the reference amplitude, with about 74.12° phase error. The
reference disk-rotation amplitude is about 6.91e-12 s⁻¹ for a 1e-7 m/s wall
command. Small algebraic residuals and near-zero divergence did not make the
central response accurate. A residual correction barely changed it.

The latest recorded physical attempt is
[R020](docs/realizability/B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md).
Its cell-integrated original-command result still has amplitude ratio
28,963.4968 and phase error 74.1175°. A comparison using a known solution's
boundary trace stopped on pressure/flux compatibility before either
matched-trace solve. Consequently, the discrepancy has not been reliably
allocated among mesh resolution, faceted geometry, boundary data and
measurement integration.

[R033](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_FOLLOWUP.md) subsequently
passed the repaired toy/observer prerequisites for a proposed higher-order
comparison. It did not run that physical comparison. The numerical gate
remains failed and `campaign_ready=false`; neither the six-input campaign nor
a boundary-only observability study is validated.

This is an unresolved numerical accuracy problem, not proof that the
engineering goal is impossible. Conversely, an attractive animation cannot
resolve it. One mesh's large error does not establish a universal solver error
floor or the attainable physical contraction.

## What “the first few orders of magnitude” must mean

R177 now proposes measured quantities, a finite interval and explicit error
budgets in the [revised benchmark](BOUNDARY_CONTROL_HANDOFF.md#9-target-errors-and-interpretable-outcomes).
They remain proposals for user review, not achieved or finally approved limits. The
paper motivates a radial scale proportional to the square root of remaining
similarity time. Using that relation as a finite-range target gives:

| Chosen range | Corresponding radial contraction, if the scaling holds |
|---|---|
| 100-fold decrease in similarity time (2 decades) | 10-fold reduction in radius |
| 1,000-fold decrease in similarity time (3 decades) | About 31.6-fold reduction in radius |
| 100-fold reduction in radius (2 radius decades) | 10,000-fold decrease in similarity time (4 decades) |

These are algebraic translations of a proposed scaling, not achieved results.
The implemented reference's 10 mm → 3 mm trajectory is a modest first target;
10 mm → 1 mm is a larger candidate. Neither has been generated by validated
boundary control here. The animation's TauRatio is not a measurement of the
remaining time of a solved physical evolution.

For an engineering claim, report achieved core size, swirl, strain, relevant
mode amplitudes and stress transport, with mesh/time/measurement uncertainty
and actuator/sensor limits over that interval. A nonzero perturbation
correlation alone does not establish the required momentum transfer: its
spatial transport and the momentum-balance residual must also be assessed.
Finite failure at a smaller scale would be useful evidence about the attainable
range.

## What remains between today's preview and the intended simulation

1. Review the R177 finite-target proposal and its remaining user-level choices;
   its units, observables, tolerances and strict boundary sensing baseline are
   now explicit. Keep target, validation truth, sensors and estimates distinct.
2. Obtain an accurate small boundary-response benchmark; resolve the current
   B2 comparison before trusting a campaign built on it. Preserve independent
   reference checks and practical execution limits.
3. Establish influence and boundary-only identifiability at an explicitly
   stated operating point, then test finite-amplitude preparation and nonlinear
   evolution with physically limited actuators.
4. Quantify the achieved scale range and the need for continued driving;
   evaluate estimation/control with the allowed noisy, delayed measurements.
5. Export the accepted finite history to the separate renderer: geometry and
   SI units, physical timestamps, fields/tracers, measured core/strain/swirl
   histories, commands, sensor outputs, estimates and numerical uncertainty.

This sequence is a research path, not a completion percentage or a prediction
that all stages will succeed. Bench validation would be needed before claiming
that a real apparatus performs as simulated; building one is not a prerequisite
for producing an honestly labeled engineering simulation.

## Timed boundary forcing: the wave-focusing analogy

R174 describes a circular pool whose surrounding actuators produce a tall
central water column by coordinating different frequencies. A strong match
is Edinburgh's FloWave spike-wave experiment, though the exact demonstration
the user saw is not identified. Its researchers report central crests up to
6 m and explain the process as dispersive wave focusing followed by trough
collapse and jet formation. The facility has 168 perimeter wavemakers.
[Experimental paper](https://doi.org/10.1017/jfm.2021.1023),
[facility description](https://flowave.eng.ed.ac.uk/how-it-works).

The [commissioning paper](https://www.pure.ed.ac.uk/ws/files/14949375/Oceans_Flowave_final.pdf)
explicitly describes waves of decreasing frequency timed to reach the centre
together. Frequency-dependent travel and phase are coordinated so contributions
meet at a selected place and time. This provides an example of boundary actuation
creating a concentrated interior event. It motivates a command-history study
here; it does not show that the required vortex trajectory is reachable.
R175 acknowledges that our situation is harder; feasibility remains open.

For our benchmark, the relevant question is whether a sequence of normal and
tangential commands can prepare the desired state and produce a useful finite
interval of contraction. Testing one frequency or a static input/output rank
cannot settle that question. In a linear approximation about a steady base,
the appropriate object is a causal response to each input over time:

```text
change in feature i at time t
  = sum over actuators j of integral_0^t K_ij(t-s) command_j(s) ds
```

Here K is a measured/computed impulse-response kernel, not an assumed wave
travel time; the formula assumes zero initial perturbation. A complete,
validated complex frequency response can represent the same linear dynamics.
Our single-frequency accuracy pilot is only an early verification step.
Nonlinear finite-amplitude preparation would need a subsequent model/check.

The analogy has limits: FloWave uses a deforming free surface and gravity-wave
propagation. Our current closed-cylinder Stokes benchmark has neither that
surface nor that propagation mechanism; its vorticity transport about rest
is diffusive. No free-surface solver or new actuation mechanism is selected.
A transient peak also differs from tracking a contracting, swirling state
through a specified range of scales. Phase coordination can combine available
responses, but cannot create a missing control direction or remove physical
actuator limits. The admissible preparation time and robustness to timing
errors must be reported.

Finally, concentrating a known input is separate from reconstructing an
unknown interior state. The FloWave study used wave gauges and optical surface
measurements; it is not evidence for our strict boundary-only sensing goal.
The proposed benchmark should distinguish precomputed open-loop preparation
from any later boundary-measurement feedback and evaluate each on its own terms.

## If the boundary-only goal cannot be achieved, what would explain why?

We do not currently have a general impossibility result. A useful negative
conclusion must name the target, allowed controls and measurements, initial
state, time interval, accuracy/noise tolerance and hardware limits. It should
identify the limiting mechanism and the largest useful range still supported.

| Possible obstacle | Evidence that would justify a clear, scoped conclusion | What that conclusion would not establish |
|---|---|---|
| Exact target needs an interior force | A nonzero curl of the target momentum residual in a region where exact unforced matching is required. | It does not exclude an engineering approximation of selected observables. |
| Chosen boundary actuators cannot produce a required change | A verified response map with an inaccessible target direction, or a lower bound on tracking error under specified amplitude/bandwidth limits. | Failure of six linear modes about rest does not exclude other boundary layouts, operating points or nonlinear preparation. |
| Allowed sensors cannot distinguish necessary states | Two admissible states give identical boundary signals but different target observables or require different corrective actions; with noise, their signal difference stays below the measurement uncertainty. | It rules out the stated inference/feedback task, not automatically a prescribed open-loop flow or every possible boundary sensor. |
| Hardware becomes inadequate as the core shrinks | Converged calculations show that required speed, stroke, force, power or bandwidth exceeds declared limits, or sensor resolution/noise prevents the requested accuracy. | This is a limit of the specified apparatus and scale range, not a theorem about every boundary-controlled fluid. |
| Numerical results cannot resolve the answer | Reference, mesh/time refinement or measurement-error checks fail. This describes the present B2 obstacle. | An inconclusive calculation is neither engineering success nor evidence of physical impossibility. |

For a linear response study, an inaccessible direction can be exhibited as an
output combination that all allowed inputs leave unchanged. For sensing, the
corresponding witness is a state change invisible to every allowed measurement.
These concrete witnesses are more informative than reporting a bad condition
number alone. Small nonzero responses must be compared with numerical error,
input limits and sensor noise before interpreting them as practical barriers.

The pressure-blind pure-swirl direction already supplies a model-specific
example of the sensing issue. The large B2 reference discrepancy supplies an
example of numerical uncertainty. Neither currently establishes that the
user's finite-range boundary-only engineering approximation is impossible.

## Next task and execution status

R177 completed the [benchmark revision](BOUNDARY_CONTROL_HANDOFF.md). It proposes
300 s preparation from rest and 100 s tracking of the existing 10 mm → 3 mm
reference, six replayable command histories, strict wall-pressure/actuator
measurements, and explicit whole-history and uncertainty criteria. It separates
actuation limits, sensor-blind states, command-budget failures and numerical
inconclusiveness. The proposed range is 0.523 radius decades / 1.046
radius-squared decades, not the longer-term “few orders” goal achieved.

The single [next task](SESSION_HANDOFF.md#next-task) is concrete, bounded launch
integration for the existing R021 matched-trace diagnostic using the completed
R033 prerequisites and R070 repairs. Prepare and benign-test a default-disabled
physical path under practical supervision; stop before physical/FEM execution.
Do not restart completed toy work or create another general monitoring plan.
Retain GPT-6 Astra/high on PC/WSL daisy for numerical interfaces and scope
judgment. B2 accuracy remains failed and the q64/q96 physical comparison unused.

Unresolved user choices remain the proposed engineering tolerances/preparation
and command budgets, whether interior optical feedback is allowed, and later
credible hardware/noise limits. Strict boundary measurement support remains
the baseline. None of these changes the unchanged B2 accuracy diagnostic.
The rendering repair/preview is complete in `6deb9d0`; R170–R176's assessment
was delivered in `22cf3d7`. R177's start was published in `ace8311`, with completion
publication prepared in the logs. No preview retry or Mac work is required.

The [R103/R104 practical supervision policy](docs/realizability/B2_MONITOR_PRACTICAL_SUPERVISION_POLICY.md)
retains limits, cleanup and honest incomplete-result reporting while removing
recursive infrastructure certification. Optional cross-platform benchmarks
and general monitor features must not displace the named scientific task.
Physical execution still requires its applicable numerical and practical
safeguards; this report grants no attempt and changes no acceptance thresholds.

## What the resource budgets mean

The retained 180 s / 1536 MiB physical allowance is an execution limit, not an
accuracy target or the hardware's total capability. R033's separate completed
prerequisite allowance was 600 s / 1536 MiB. Neither grants a new run.
Capacity must be assessed at any future authorized launch; old free-memory
snapshots are not current measurements. The q64/q96 physical comparison
remains unrun. Detailed historical environment, monitor and resource records
remain linked from the [handoff](SESSION_HANDOFF.md) and
[practical supervision policy](docs/realizability/B2_MONITOR_PRACTICAL_SUPERVISION_POLICY.md).

## Evidence and checks for this update

R171–R174 reviewed source/configuration, existing frame headers, recorded
R169 acceptance, B2 stability/accuracy/R020/R033 evidence, and the paper's
Theorem 1.1 and Section 2. The source review also checked the movie's default
visibility flags, interior hardware markers and separate radius formula.
R174 additionally checked primary FloWave facility and experimental sources
and added the timing/phase analogy with its free-surface and sensing limits.
No new solver test, trajectory integration, renderer, encode, ffprobe, package
change or physical experiment ran. Documentation validation passed for 32 local
targets/anchors, unique request IDs, preserved committed request history and
diff whitespace; historical numerical test passes are not claimed as new runs.
R176's final publication review passed 33 local link/anchor checks, both
append-only log-prefix checks, unique request IDs through R176, four-file
documentation scope and whitespace. Fresh fetch confirmed equal local/upstream
tips before the authorized documentation commit; staged checks follow.

R177 reviewed the benchmark against the implemented configuration/reference,
R020/R021/R033/R070 evidence and R103/R104 policy; it rechecked the primary
paper and official model guidance. Only the benchmark and four continuity
documents changed. No numerical workloads, FEM tests, trajectory, render,
encode, controller, hardware or package work ran. Documentation checks and
actual delivery are recorded in the request/work logs and final response.
