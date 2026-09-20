# Project Tracks

This repository deliberately contains two related but distinct projects.

The shared goals are to assess whether exterior actuators and sensors can
prepare a flow that carries out a useful finite range of the desired process,
and to supply data for a clear, approximately realistic separate 3D movie.
[STATUS.md](STATUS.md) connects those goals to current progress, unresolved
questions and the distinction between initial preparation and continued driving.

## Track A — Visualization

### Question

What does the proposed flow and apparatus look like in three dimensions?

### Current status

Implemented and actively usable.

### Current pipeline

```text
prescribed velocity field
        ↓
Python RK4 tracer integration
        ↓
POV-Ray frame rendering
        ↓
ffmpeg movie
```

### Important limitation

The rendered actuator hardware does **not** generate the tracer flow.

The visualization is useful for understanding motion, apparatus layout, actuator placement, sensor placement, PIV optical access, and communication. It is not evidence that the physical boundary-control concept works.

### Work that can proceed now

- improve appearance,
- improve tracer visibility,
- optimize render speed,
- improve tank/hardware geometry,
- add useful views,
- validate frame/movie pipeline.

---

## Track B — Physical realizability and boundary control

### Question

Can physically realizable external actuators and sensors reproduce something meaningfully similar to a finite portion of the desired interior dynamics?

### Current status

The research track has implemented B0 benchmark diagnostics and optional B1/B2
linear Stokes verification backends. This is a bounded verification pipeline,
not a validated boundary-control system or a physical realization of the target.

- **B0:** NumPy-only configuration, boundary-mode, observable, and sensor
  diagnostics run without a CFD solver. They check benchmark assumptions and
  verification fixtures; they do not calculate a controlled flow.
- **B1:** An optional DOLFINx Taylor–Hood backend runs linear unsteady-Stokes
  verification cases and coarse boundary pilots. Its strong-divergence check
  failed the required tolerance, so B1 does not establish a reliable
  divergence-free response.
- **B2:** A separate optional DOLFINx BDM2/DG1 backend adds divergence-conforming
  Stokes verification, stability audits, and a pre-campaign response gate. The
  stored physical-pilot gate remains failed: the tangential response has not
  converged against the independent reference, and stability/boundary issues
  still require numerical-method review. Schema-3 reports now make physical
  reference discrepancies and unresolved campaign blockers explicit; even a
  passing legacy aggregate leaves readiness false until actual response-mesh
  stability and physical accuracy are reviewed.

Changed-parameter manufactured and swirl cases are verification fixtures only;
they do not validate the physical 0.01 Hz response or demonstrate physical
control. The six-input campaign and B3 sensing work have not begun.

The acceptance-report repair and physical-reference diagnostics are complete.
The [scalable stability review](docs/realizability/B2_SCALABLE_STABILITY_REVIEW.md)
calibrates a sufficient local coercivity bound against dense small-cylinder
fixtures and compares it with sparse constrained inertia counts. The separate
`b2-coercivity` diagnostic is implemented and has been evaluated on 100, 70,
and 50 mm fixtures. The subsequent
[response-geometry study](docs/realizability/B2_RESPONSE_COERCIVITY_RESULT.md)
also certifies positive homogeneous dissipation at alpha=96 on the exact
40/30/25 mm physical-pilot geometries; alpha=48 remains inconclusive on all
four 50/40/30/25 mm meshes. This supplies scoped stability evidence without
establishing physical accuracy or selecting a production penalty. The separate
diagnostic is not integrated into the gate. The completed
[accuracy review](docs/realizability/B2_ACCURACY_REVIEW.md) reproduces the tiny
physical disk response and finds reference sensitivity far below the existing
comparison scale. The subsequent
[single physical response audit](docs/realizability/B2_PHYSICAL_RESPONSE_AUDIT.md)
completed one 50 mm alpha=96 solve and same-factor correction within its caps.
PDE/arithmetic checks pass, but the finest-rule amplitude is 28962.69 times the
reference with a 74.12-degree phase discrepancy. The observed correction is tiny;
feature quadrature remains unresolved at the reference error scale. The completed
[method review](docs/realizability/B2_MATCHED_TRACE_REVIEW.md) specifies a paired
boundary-data experiment on that same mesh: compare the current command with a
known solution's full boundary trace, and integrate the disk separately by cell.
The experiment is not yet run. Its discrete boundary sensitivity will not by
itself identify continuum geometry error. A total FEM error floor is still
unknown. The B2 gate remains failed and campaign readiness false. Use
[SESSION_HANDOFF.md](SESSION_HANDOFF.md) for completion criteria and stops.

### Core constraint

The final model should not rely on arbitrary volumetric forcing.

Reference fields may use such forcing, but the realizable model should use boundary mechanisms that map to plausible hardware.

### Proposed pipeline

```text
finite reference trajectory
        ↓
bounded-domain CFD
        ↓
normal/tangential boundary modes
        ↓
input → interior-state response tests
        ↓
reachability analysis
        ↓
state → sensor response tests
        ↓
observability analysis
        ↓
finite actuator array
        ↓
hardware limits
        ↓
open-loop tracking
        ↓
realistic estimator
        ↓
closed-loop CFD
        ↓
bench experiment
```

### Immediate milestone

Do **not** begin with full control.

First answer:

> Can a modest set of physically interpretable boundary modes independently influence the reduced central-flow quantities we care about?

Then answer:

> Can realistic pressure/PIV measurements distinguish those quantities?

These questions are smaller, falsifiable, and highly informative.

---

## Shared scientific rules

Both tracks must maintain the distinctions among:

- mathematical target,
- kinematic visualization,
- CFD solution,
- boundary-control calculation,
- physical experiment.

Do not describe success in one category as success in another.

A failure or finite limitation is useful data.

---

## Documentation map

- `README.md` — project entry point and practical visualization instructions.
- `STATUS.md` — user goals, current progress, unresolved feasibility questions,
  and the intended data handoff to a separate movie.
- `AGENTS.md` — implementation and AI-agent rules.
- `REQUEST_LOG.md` — user requests, scope, validation, and outcomes.
- `SESSION_HANDOFF.md` — current bounded task, reusable continuation request,
  model/effort recommendations, and stop conditions.
- `EXPERIMENT.md` — physical experiment concept.
- `PHYSICAL_REALIZABILITY_PLAN.md` — broad realizability philosophy and plan.
- `CONTROL_RESEARCH_ROADMAP.md` — concrete staged computational research program.
- `BOUNDARY_CONTROL_HANDOFF.md` — proposed benchmark decisions, scientific
  diagnostics, and implementation/testing work packages for the next coding agent.
- `PROJECT_TRACKS.md` — this high-level separation of the two avenues.
